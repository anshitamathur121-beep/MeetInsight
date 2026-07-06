# agents/brief_agent.py

from agents.base_agent import BaseAgent

class BriefAgent(BaseAgent):
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        super().__init__(model_name)
        
    def analyze(self, transcript: list) -> dict:
        transcript_text = self.format_transcript_as_text(transcript)
        
        prompt = f"""
        You are a senior executive brief writer. Analyze the following meeting transcript.
        Generate a high-quality "60-second brief" and 4 short keyword tags (each 1-3 words max).
        
        The brief should be a concise summary paragraph (approx. 2-3 sentences) detailing:
        1. Key objectives/agreements met.
        2. Core decisions or topics discussed.
        3. Major outstanding blockers or critical deadlines.
        Make the brief direct, engaging, and professional.
        
        Transcript:
        \"\"\"
        {transcript_text}
        \"\"\"
        
        Respond ONLY with a JSON object in this format:
        {{
          "summary": "A concise executive summary paragraph...",
          "tags": ["tag1", "tag2", "tag3", "tag4"]
        }}
        """
        return self._execute_analysis(prompt, "brief")
