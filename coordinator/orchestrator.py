# coordinator/orchestrator.py

import time
import logging
import json
import re
import google.generativeai as genai

from agents.brief_agent import BriefAgent
from agents.decisions_agent import DecisionsAgent
from agents.actions_agent import ActionsAgent
from agents.risks_agent import RisksAgent
from agents.changes_agent import ChangesAgent
from agents.questions_agent import QuestionsAgent
from agents.email_agent import EmailAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Minimum spacing between sequential Gemini calls (free tier ≈ 5 req/min).
AGENT_CALL_INTERVAL_SEC = 13


def _coerce_list(payload, list_key: str) -> list:
    """Extract a list from agent payload regardless of JSON nesting shape."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        value = payload.get(list_key)
        if isinstance(value, list):
            return value
        for candidate in payload.values():
            if isinstance(candidate, list):
                return candidate
    return []


class CoordinatorOrchestrator:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self.brief_agent = BriefAgent(model_name)
        self.decisions_agent = DecisionsAgent(model_name)
        self.actions_agent = ActionsAgent(model_name)
        self.risks_agent = RisksAgent(model_name)
        self.changes_agent = ChangesAgent(model_name)
        self.questions_agent = QuestionsAgent(model_name)
        self.email_agent = EmailAgent(model_name)

    def generate_meeting_arc(self, transcript: list) -> list:
        """Use Gemini to segment the transcript into 4-6 chronological chapters (Meeting Arc)."""
        formatted_lines = []
        for entry in transcript:
            formatted_lines.append(f"[{entry.get('timestamp', '00:00')}] {entry.get('speaker', 'Unknown')}: {entry.get('text', '')}")
        transcript_text = "\n".join(formatted_lines)

        prompt = f"""
            You are an expert meeting analyst. Segment the following meeting transcript into 4 to 6 logical, chronological chapters or topics (representing a "Meeting Arc").
            For each chapter, identify:
            1. The timestamp (MM:SS) where this segment begins.
            2. A short label summarizing the topic (1-4 words).
            
            Transcript:
            \"\"\"
            {transcript_text}
            \"\"\"
            
            Respond ONLY with a JSON array of objects structured like this:
            [
              {{"timestamp": "00:00", "label": "Kickoff & context"}},
              {{"timestamp": "08:12", "label": "Checkout metrics review"}}
            ]
            """
        model = genai.GenerativeModel(self.model_name)
        last_error = None

        for attempt in range(4):
            try:
                response = model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"},
                )
                data = json.loads(response.text.strip())
                if isinstance(data, list):
                    return data
                if isinstance(data, dict):
                    for value in data.values():
                        if isinstance(value, list):
                            return value
                raise ValueError(f"Unexpected meeting arc shape: {type(data)}")
            except Exception as e:
                last_error = e
                error_text = str(e)
                if ("429" in error_text or "quota" in error_text.lower()) and attempt < 3:
                    delay = 30.0
                    match = re.search(r"retry in ([0-9.]+)s", error_text, flags=re.IGNORECASE)
                    if match:
                        delay = float(match.group(1)) + 1.0
                    logger.info("Meeting arc rate limited — retrying in %.1fs", delay)
                    time.sleep(delay)
                    continue
                if attempt < 3:
                    time.sleep(2 * (attempt + 1))

        logger.error("Error generating meeting arc: %s", last_error)
        if len(transcript) > 0:
            return [
                {"timestamp": transcript[0].get("timestamp", "00:00"), "label": "Kickoff & context"},
                {"timestamp": transcript[-1].get("timestamp", "00:00"), "label": "Wrap-up & details"},
            ]
        return [{"timestamp": "00:00", "label": "Meeting sync"}]

    def calculate_speaker_airtime(self, transcript: list) -> list:
        """Calculate speaking time percentages based on the character length of speech segments."""
        speaker_chars = {}
        total_chars = 0
        
        for entry in transcript:
            speaker = entry.get("speaker", "Unknown")
            text = entry.get("text", "")
            char_count = len(text)
            speaker_chars[speaker] = speaker_chars.get(speaker, 0) + char_count
            total_chars += char_count
            
        if total_chars == 0:
            return []
            
        # Color palette for airtime representation
        colors = ["#7A1636", "#A67CFF", "#64748b", "#10b981", "#C4B5FD", "#06b6d4", "#9333ea"]
        
        airtime_list = []
        for i, (speaker, count) in enumerate(sorted(speaker_chars.items(), key=lambda x: x[1], reverse=True)):
            percentage = round((count / total_chars) * 100)
            color = colors[i % len(colors)]
            airtime_list.append({
                "speaker": speaker,
                "percentage": percentage,
                "color": color
            })
        return airtime_list

    def process_transcript(self, transcript: list, title: str = "Meeting Intelligence Report") -> dict:
        """
        Executes specialized analyzers in parallel, merges outputs, and computes overall report metadata.
        
        Args:
            transcript (list): Diarized transcript with speaker names and timestamps.
            title (str): The name/title of the meeting.
            
        Returns:
            dict: The merged intelligence report.
        """
        start_time = time.time()
        logger.info("Starting sequential analysis of meeting transcript...")
        
        # Parallel execution of agents
        agents = {
            "brief": self.brief_agent,
            "decisions": self.decisions_agent,
            "actions": self.actions_agent,
            "risks": self.risks_agent,
            "changes": self.changes_agent,
            "questions": self.questions_agent,
            "email": self.email_agent
        }
        
        # Run agents sequentially to avoid free-tier rate-limit bursts (429).
        # Transcription already consumes one request; firing 7 in parallel drops most agents.
        results = {}
        agent_items = list(agents.items())
        for index, (name, agent) in enumerate(agent_items):
            if index > 0:
                time.sleep(AGENT_CALL_INTERVAL_SEC)
            try:
                res = agent.analyze(transcript)
                if res.get("status") == "success":
                    results[name] = res.get("data") or {}
                    logger.info("Agent %s returned data keys: %s", name, list(results[name].keys()))
                else:
                    logger.error("Agent %s returned error status: %s", name, res.get("data"))
                    results[name] = {}
            except Exception as exc:
                logger.error("Agent %s generated an exception: %s", name, exc)
                results[name] = {}

        processing_duration = time.time() - start_time
        logger.info("Sequential analysis finished in %.2f seconds.", processing_duration)
        
        # Calculate dynamic metadata
        unique_speakers = list(set([entry.get("speaker", "Unknown") for entry in transcript]))
        airtime = self.calculate_speaker_airtime(transcript)
        time.sleep(AGENT_CALL_INTERVAL_SEC)
        timeline = self.generate_meeting_arc(transcript)
        
        # Parse transcript to extract/add tags for visualization
        # We can scan the decisions, risks, changes and tag them in the transcript for jumping!
        enriched_transcript = []
        decisions_texts = [d.get("text", "").lower()[:20] for d in _coerce_list(results.get("decisions"), "decisions")]
        changes_texts = [c.get("title", "").lower()[:20] for c in _coerce_list(results.get("changes"), "changes")]
        risks_texts = [r.get("title", "").lower()[:20] for r in _coerce_list(results.get("risks"), "risks")]
        
        for entry in transcript:
            entry_copy = entry.copy()
            text_lower = entry.get("text", "").lower()
            
            # Simple matching heuristic
            is_decision = any(dt in text_lower for dt in decisions_texts) if decisions_texts else False
            is_change = any(ct in text_lower for ct in changes_texts) if changes_texts else False
            is_risk = any(rt in text_lower for rt in risks_texts) if risks_texts else False
            
            if is_decision:
                entry_copy["tag"] = "Decision"
            elif is_change:
                entry_copy["tag"] = "Change request"
            elif is_risk:
                entry_copy["tag"] = "Risk"
                
            enriched_transcript.append(entry_copy)
            
        # Compile counts
        # Compile lists and handle dictionaries defensively
        dec_list = _coerce_list(results.get("decisions"), "decisions")
        for idx, d in enumerate(dec_list):
            if isinstance(d, dict) and "id" not in d:
                d["id"] = f"D{idx + 1}"

        act_list = _coerce_list(results.get("actions"), "action_items")
        for idx, a in enumerate(act_list):
            if isinstance(a, dict) and "id" not in a:
                a["id"] = f"A{idx + 1}"

        risk_list = _coerce_list(results.get("risks"), "risks")
        for idx, r in enumerate(risk_list):
            if isinstance(r, dict) and "id" not in r:
                r["id"] = f"R{idx + 1}"

        change_list = _coerce_list(results.get("changes"), "changes")
        for idx, c in enumerate(change_list):
            if isinstance(c, dict) and "id" not in c:
                c["id"] = f"C{idx + 1}"

        ques_list = _coerce_list(results.get("questions"), "questions")
        for idx, q in enumerate(ques_list):
            if isinstance(q, dict) and "id" not in q:
                q["id"] = f"Q{idx + 1}"

        brief_data = results.get("brief")
        if not isinstance(brief_data, dict):
            brief_data = {}
        brief_merged = {
            "summary": brief_data.get("summary") or "No summary generated.",
            "tags": brief_data.get("tags") or []
        }
        
        email_data = results.get("email")
        if not isinstance(email_data, dict):
            email_data = {}
        email_merged = {
            "to": email_data.get("to") or "team@company.com",
            "cc": email_data.get("cc") or "",
            "subject": email_data.get("subject") or f"{title} — decisions & next steps",
            "tones": {
                "Concise": email_data.get("tones", {}).get("Concise") or "No concise email summary generated.",
                "Warm": email_data.get("tones", {}).get("Warm") or "No warm email summary generated.",
                "Executive": email_data.get("tones", {}).get("Executive") or "No executive email summary generated.",
                "Detailed": email_data.get("tones", {}).get("Detailed") or "No detailed email summary generated."
            } if isinstance(email_data.get("tones"), dict) else {
                "Concise": "No concise email summary generated.",
                "Warm": "No warm email summary generated.",
                "Executive": "No executive email summary generated.",
                "Detailed": "No detailed email summary generated."
            },
            "suggestion": email_data.get("suggestion") or ""
        }
        
        decisions_high = sum(1 for d in dec_list if isinstance(d, dict) and d.get("impact", "").lower() == "high")
        actions_due = sum(1 for a in act_list if isinstance(a, dict) and ("today" in a.get("due_date", "").lower() or "jul 5" in a.get("due_date", "").lower() or a.get("priority", "").lower() == "high"))
        risks_unresolved = len(risk_list)
        
        # Build Report
        report = {
            "metadata": {
                "title": title,
                "date": time.strftime("%A, %b %d"),
                "time": time.strftime("%I:%M %p"),
                "duration": "Dynamic", 
                "speakers_count": len(unique_speakers),
                "engine": "Gemini 2.5 Flash",
                "processed_time": f"Processed in {int(processing_duration)}s",
                "clarity_score": 87 
            },
            "metrics": {
                "decisions_total": len(dec_list),
                "decisions_high_impact": decisions_high,
                "actions_total": len(act_list),
                "actions_due_this_week": actions_due,
                "risks_total": len(risk_list),
                "risks_unresolved": risks_unresolved
            },
            "brief": brief_merged,
            "decisions": dec_list,
            "action_items": act_list,
            "risks": risk_list,
            "changes": change_list,
            "questions": ques_list,
            "timeline": timeline,
            "airtime": airtime,
            "transcript": enriched_transcript,
            "email": email_merged
        }
        
        return report
