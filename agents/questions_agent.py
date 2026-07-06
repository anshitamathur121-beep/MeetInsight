# agents/questions_agent.py

from agents.base_agent import BaseAgent

class QuestionsAgent(BaseAgent):
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        super().__init__(model_name)
        
    def analyze(self, transcript: list) -> dict:
        transcript_text = self.format_transcript_as_text(transcript)
        
        prompt = f"""
        You are a team facilitator agent. Analyze the following meeting transcript.
        Extract all open, unanswered questions or outstanding points of inquiry raised during the meeting.
        
        For each open question:
        - Extract the specific question text.
        - Identify who asked the question (e.g. Marcus, Ada, Priya).
        
        Transcript:
        \"\"\"
        {transcript_text}
        \"\"\"
        
        Respond ONLY with a JSON object in this format:
        {{
          "questions": [
            {{
              "text": "The open question asked?",
              "speaker": "Speaker Name"
            }}
          ]
        }}
        """
        return self._execute_analysis(prompt, "questions")
