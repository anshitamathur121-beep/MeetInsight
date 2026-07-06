# agents/risks_agent.py

from agents.base_agent import BaseAgent

class RisksAgent(BaseAgent):
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        super().__init__(model_name)
        
    def analyze(self, transcript: list) -> dict:
        transcript_text = self.format_transcript_as_text(transcript)
        
        prompt = f"""
        You are a risk management specialist. Analyze the following meeting transcript.
        Extract all risks, blockers, concerns, and unresolved dependencies mentioned.
        
        For each risk item:
        - Provide a short title summarizing the risk (e.g. "Stripe migration timing").
        - Write a detailed description of why it is a concern and what it depends on (e.g. "Depends on infra team's Q3 capacity").
        - Determine the severity (High, Medium, Low).
        - Determine the impact (High, Medium, Low).
        
        Transcript:
        \"\"\"
        {transcript_text}
        \"\"\"
        
        Respond ONLY with a JSON object in this format:
        {{
          "risks": [
            {{
              "title": "Risk Title",
              "description": "Description of the blocker/risk",
              "severity": "High",
              "impact": "High"
            }}
          ]
        }}
        """
        return self._execute_analysis(prompt, "risks")
