# agents/email_agent.py

from agents.base_agent import BaseAgent

class EmailAgent(BaseAgent):
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        super().__init__(model_name)
        
    def analyze(self, transcript: list) -> dict:
        transcript_text = self.format_transcript_as_text(transcript)
        
        prompt = f"""
        You are a business communications specialist. Analyze the following meeting transcript.
        Generate a professional follow-up email for the meeting.
        
        Generate the email in 4 distinct tones:
        1. Concise: Short, direct, bullet-pointed, focusing only on the absolute essentials.
        2. Warm: Friendly, collaborative, encouraging, maintaining high team morale.
        3. Executive: High-level overview, strategic summaries, structured for senior leadership.
        4. Detailed: Full recap, including detailed lists of decisions, assigned owners, and specific timelines.
        
        Also output:
        - A default "to" recipient field (deduced from the team/company context or "team@company.com").
        - A default "cc" field (optional).
        - A subject line (e.g., "Roadmap Review — decisions & next steps").
        - A single "suggestion" (a smart tip, like "Consider adding a line asking Marcus to confirm the Stripe migration window by Friday — this is the meeting's only unresolved dependency.").
        
        Transcript:
        \"\"\"
        {transcript_text}
        \"\"\"
        
        Respond ONLY with a JSON object in this format:
        {{
          "to": "growth-pod@company.com",
          "cc": "",
          "subject": "Subject of the email",
          "tones": {{
            "Concise": "Email body in concise tone...",
            "Warm": "Email body in warm tone...",
            "Executive": "Email body in executive tone...",
            "Detailed": "Email body in detailed tone..."
          }},
          "suggestion": "Smart suggestion text..."
        }}
        """
        return self._execute_analysis(prompt, "email")
