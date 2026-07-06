# media/transcriber.py

import os
import time
import json
import logging
# pyrefly: ignore [missing-import]
import google.generativeai as genai
import utils.helpers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_api_key() -> str:
    """Retrieve Gemini API Key from environment variables."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Gemini API key not found in environment variables (GEMINI_API_KEY or GOOGLE_API_KEY).")
    return api_key

def transcribe_audio(audio_path: str) -> list:
    """
    Transcribes audio with speaker diarization using Gemini multimodal input.
    
    Args:
        audio_path (str): Absolute path to the MP3 or WAV file.
        
    Returns:
        list: A list of speech segments: [{"timestamp": "MM:SS", "speaker": "Name", "text": "..."}]
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    
    logger.info(f"Reading audio file: {audio_path}...")
    with open(audio_path, "rb") as f:
        audio_data = f.read()
        
    _, ext = os.path.splitext(audio_path.lower())
    mime_map = {
        ".mp3": "audio/mp3",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".mp4": "audio/mp4",
    }
    mime_type = mime_map.get(ext, "audio/mp3")

    audio_part = {
        "mime_type": mime_type,
        "data": audio_data
    }
    
    logger.info("Triggering diarized transcription via inline audio payload...")
    
    try:
        # We use gemini-2.5-flash since it is fast and supports current keys
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = """
        You are a highly accurate meeting transcriber and speaker identification system.
        Analyze the audio recording and generate a chronological transcript.
        
        For each speech segment:
        1. Identify who is speaking (diarization). Listen to introductions or names referenced during the call to deduce real names (e.g. Priya, Marcus, Ada, Jonas, Noor). If you cannot deduce a name, use a consistent label like 'Speaker A', 'Speaker B', etc.
        2. Identify the timestamp (e.g., "12:41") of when the speaker begins speaking.
        3. Transcribe the words spoken as accurately as possible.
        
        Respond ONLY with a JSON array containing objects structured exactly like this:
        [
          {
            "timestamp": "00:12",
            "speaker": "Priya S.",
            "text": "Alright — let's lock the roadmap for Q3. Priority number one is getting checkout out."
          },
          {
            "timestamp": "08:12",
            "speaker": "Ada C.",
            "text": "Cart conversion is up 6% on the beta cohort. We're within the guardrails."
          }
        ]
        
        Return nothing but valid JSON. Ensure the JSON is clean and doesn't contain any backticks or markdown wrapping.
        """
        
        # Request JSON output
        response = model.generate_content(
            [audio_part, prompt],
            generation_config={"response_mime_type": "application/json"}
        )
        
        response_text = response.text.strip()
        logger.info("Received transcription response from Gemini.")
        
        # Parse JSON
        transcript_data = json.loads(response_text)
        if not isinstance(transcript_data, list):
            raise ValueError("API did not return a JSON array list.")
            
        return transcript_data
        
    except json.JSONDecodeError as je:
        logger.error(f"Failed to parse Gemini response as JSON. Raw response: {response_text}")
        raise RuntimeError(f"Gemini did not return valid JSON: {je}")
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        raise e
