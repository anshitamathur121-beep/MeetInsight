# agents/decisions_agent.py

from agents.base_agent import BaseAgent

class DecisionsAgent(BaseAgent):
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        super().__init__(model_name)
        
    def analyze(self, transcript: list) -> dict:
        transcript_text = self.format_transcript_as_text(transcript)
        
        prompt = f"""
        You are a meeting alignment specialist. Analyze the following meeting transcript.
        Extract all major decisions made during the meeting.
        
        For each decision:
        - Identify the precise statement or agreement that represents a decision.
        - Attribute it to the speaker who proposed or finalized it (e.g. Priya, Ada, Marcus). If multiple, write "Team".
        - Identify the timestamp (MM:SS) where this decision occurred.
        - Classify the decision's impact level: High (core strategy/breaking change), Medium (workflow adjustment), or Low (small detail/administrative).
        
        Transcript:
        \"\"\"
        {transcript_text}
        \"\"\"
        
        Respond ONLY with a JSON object in this format:
        {{
          "decisions": [
            {{
              "text": "Description of the decision made",
              "speaker": "Speaker Name",
              "timestamp": "MM:SS",
              "impact": "High"
            }}
          ]
        }}
        """
        return self._execute_analysis(prompt, "decisions")
