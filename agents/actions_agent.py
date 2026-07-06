# agents/actions_agent.py

from agents.base_agent import BaseAgent

class ActionsAgent(BaseAgent):
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        super().__init__(model_name)
        
    def analyze(self, transcript: list) -> dict:
        transcript_text = self.format_transcript_as_text(transcript)
        
        prompt = f"""
        You are a project manager agent. Analyze the following meeting transcript.
        Extract all action items, tasks, and follow-ups assigned during the meeting.
        
        For each action item:
        - Extract the specific task description.
        - Identify the assignee (the person responsible for the task, e.g. Priya, Ada, Marcus). If not clear, assign to "Unassigned".
        - Identify the deadline / due date. Express the due date in a user-friendly way such as "due Jul 8" or "due Today" or "due Friday" based on references in the meeting. If no deadline is mentioned, estimate a reasonable timeline or write "TBD".
        - Assess the task priority: High (critical for next milestones), Medium (necessary but not immediate), or Low (nice to have).
        - Mark "completed" as false by default.
        
        Transcript:
        \"\"\"
        {transcript_text}
        \"\"\"
        
        Respond ONLY with a JSON object in this format:
        {{
          "action_items": [
            {{
              "text": "Task description",
              "assignee": "Assignee Name",
              "due_date": "due Jul 8",
              "priority": "High",
              "completed": false
            }}
          ]
        }}
        """
        return self._execute_analysis(prompt, "actions")
