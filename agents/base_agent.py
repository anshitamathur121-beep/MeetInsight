# agents/base_agent.py

import os
import re
import json
import time
import logging
# pyrefly: ignore [missing-import]
import google.generativeai as genai
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Expected list keys per module — used to normalize Gemini JSON shapes.
MODULE_LIST_KEYS = {
    "decisions": "decisions",
    "actions": "action_items",
    "risks": "risks",
    "changes": "changes",
    "questions": "questions",
}

MODULE_ALTERNATE_KEYS = {
    "decisions": ("decision", "items", "results"),
    "actions": ("actions", "tasks", "items", "actionItems"),
    "risks": ("risk", "items", "results"),
    "changes": ("change_requests", "changeRequests", "items", "results"),
    "questions": ("question", "open_questions", "items", "results"),
}


class BaseAgent(ABC):
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not found in environment variables (GEMINI_API_KEY or GOOGLE_API_KEY).")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def format_transcript_as_text(self, transcript: list) -> str:
        """Helper to format a transcript list of dicts into a readable text block."""
        formatted_lines = []
        for entry in transcript:
            ts = entry.get("timestamp", "00:00")
            speaker = entry.get("speaker", "Unknown")
            text = entry.get("text", "")
            formatted_lines.append(f"[{ts}] {speaker}: {text}")
        return "\n".join(formatted_lines)

    @abstractmethod
    def analyze(self, transcript: list) -> dict:
        """
        Runs the analyzer on the transcript.

        Returns:
            dict: {"status": "success"|"error", "module": str, "data": dict}
        """
        pass

    def _clean_json_text(self, response_text: str) -> str:
        """Strip markdown fences and whitespace from model output before parsing."""
        text = response_text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s*```$", "", text)
        return text.strip()

    def _retry_delay_seconds(self, error: Exception) -> float:
        """Parse Gemini retry_delay from a 429 error when available."""
        message = str(error)
        match = re.search(r"retry in ([0-9.]+)s", message, flags=re.IGNORECASE)
        if match:
            return float(match.group(1)) + 1.0
        match = re.search(r"retry_delay\s*\{\s*seconds:\s*([0-9]+)", message)
        if match:
            return float(match.group(1)) + 1.0
        return 30.0

    def _normalize_response(self, data, module_name: str):
        """Coerce common Gemini JSON variants into the schema orchestrator expects."""
        if module_name in ("brief", "email"):
            return data if isinstance(data, dict) else {}

        list_key = MODULE_LIST_KEYS.get(module_name)
        if not list_key:
            return data if isinstance(data, dict) else {}

        if isinstance(data, list):
            return {list_key: data}

        if isinstance(data, dict):
            if isinstance(data.get(list_key), list):
                return data
            for alt in MODULE_ALTERNATE_KEYS.get(module_name, ()):
                if isinstance(data.get(alt), list):
                    return {list_key: data[alt]}
            for value in data.values():
                if isinstance(value, list):
                    return {list_key: value}

        return {list_key: []}

    def _execute_analysis(self, prompt: str, module_name: str, max_retries: int = 4) -> dict:
        """Executes content generation with JSON configuration, retries, and normalization."""
        last_error = None

        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"},
                )
                response_text = self._clean_json_text(response.text)
                parsed = json.loads(response_text)
                data = self._normalize_response(parsed, module_name)
                logger.info("Agent %s succeeded on attempt %s", module_name, attempt + 1)
                return {
                    "status": "success",
                    "module": module_name,
                    "data": data,
                }
            except json.JSONDecodeError as e:
                last_error = e
                logger.error(
                    "JSON parse failed for %s (attempt %s): %s",
                    module_name,
                    attempt + 1,
                    e,
                )
            except Exception as e:
                last_error = e
                error_text = str(e)
                is_rate_limit = "429" in error_text or "quota" in error_text.lower()
                logger.error(
                    "Error running analyzer for %s (attempt %s): %s",
                    module_name,
                    attempt + 1,
                    e,
                )
                if is_rate_limit and attempt < max_retries - 1:
                    delay = self._retry_delay_seconds(e)
                    logger.info("Rate limited on %s — retrying in %.1fs", module_name, delay)
                    time.sleep(delay)
                    continue

            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))

        return {
            "status": "error",
            "module": module_name,
            "data": {"error": str(last_error)},
        }
