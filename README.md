# MeetInsight — Enterprise AI Meeting Intelligence Platform

MeetInsight converts meeting recordings (video/audio) into structured executive intelligence. It transcribes discussions, performs speaker diarization, runs parallel AI agents to extract key highlights, decisions, action items, risks, changes, and open questions, and compiles them into a premium web dashboard with interactive follow-up email editing and report exporting (PDF, Markdown, iCalendar).

---

## Technical Stack

- **Backend & AI Orchestration**: Python 3.11, Google GenAI SDK (Google ADK)
- **Frontend**: Streamlit
- **Media Processing**: FFmpeg (via static-ffmpeg)
- **Generative AI Models**: Google Gemini 1.5 Flash (for transcription, diarization, parallel analysis, and email generation)

---

## Getting Started

### 1. Requirements

Make sure you have Python 3.11+ installed. Install the dependencies:
```bash
pip install -r requirements.txt
```

### 2. Environment Variables

MeetInsight requires a Gemini API key. Set either the `GEMINI_API_KEY` or `GOOGLE_API_KEY` environment variable:

On Windows (Command Prompt):
```cmd
set GEMINI_API_KEY=your_gemini_api_key_here
```

On Windows (PowerShell):
```powershell
$env:GEMINI_API_KEY="your_gemini_api_key_here"
```

On macOS/Linux:
```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

### 3. Run the Application

Start the Streamlit application:
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## Core Architecture

MeetInsight follows a modular clean architecture:

1. **`app.py`**: Handles UI rendering, user interactions, page state, and routing.
2. **`media/`**:
   - `audio_extractor.py`: Extracts and compresses audio from videos to optimize API uploads.
   - `transcriber.py`: Uploads audio to Gemini for speech-to-text and speaker identification (diarization).
3. **`coordinator/`**:
   - `orchestrator.py`: Orchestrates specialized agents using thread pools to execute them in parallel, compiles counts and speaker airtime percentages, and maps chronological chapters.
4. **`agents/`**:
   - Specialized AI micro-agents (Brief, Decisions, Action Items, Risks, Changes, Questions, Email) that leverage Gemini Structured Outputs to return verified JSON.
5. **`exports/`**:
   - PDF, Markdown, and iCalendar exporters to generate shareable summaries and sync tasks with calendar applications.
