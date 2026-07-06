# agents/changes_agent.py

from agents.base_agent import BaseAgent

class ChangesAgent(BaseAgent):
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        super().__init__(model_name)
        
    def analyze(self, transcript: list) -> dict:
        transcript_text = self.format_transcript_as_text(transcript)
        
        prompt = f"""
        You are a product management agent. Analyze the following meeting transcript.
        Extract all requests to change project scope, feature requirements, timelines, or roles.
        
        For each change request:
        - Summarize the change request in a short title (e.g. "Move loyalty tier out of Q3").
        - Identify who requested the change (e.g., Marcus L., Priya S.).
        - Identify the timestamp (MM:SS) where this was requested.
        - Classify the priority (P1 for immediate/critical, P2 for medium/necessary, P3 for low/nice-to-have).
        - Classify the impact (High, Medium, Low).
        
        Transcript:
        \"\"\"
        {transcript_text}
        \"\"\"
        
        Respond ONLY with a JSON object in this format:
        {{
          "changes": [
            {{
              "title": "Change request description",
              "requestor": "Name of Requestor",
              "timestamp": "MM:SS",
              "priority": "P1",
              "impact": "High"
            }}
          ]
        }}
        """
        return self._execute_analysis(prompt, "changes")
