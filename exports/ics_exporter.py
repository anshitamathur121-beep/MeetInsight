# exports/ics_exporter.py

import os
import uuid
import datetime

def generate_ics_calendar(action_items: list, output_path: str) -> str:
    """
    Generates an iCalendar (.ics) file containing all meeting action items as calendar events.
    
    Args:
        action_items (list): List of action items from the report.
        output_path (str): Filepath to save the .ics file.
        
    Returns:
        str: Absolute path to the .ics file.
    """
    now = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//MeetInsight//Meeting Intelligence Platform//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]
    
    # Establish a default date anchor (Jul 2, 2026) or use today's date if parsing fails
    meeting_year = 2026
    
    for item in action_items:
        task_text = item.get("text", "Action Item")
        assignee = item.get("assignee", "Unassigned")
        due_str = item.get("due_date", "").lower()
        priority = item.get("priority", "Medium")
        
        # Try to parse a date out of the due string (e.g. "due Jul 8")
        # Default to today if we cannot parse
        task_date = datetime.datetime.now()
        
        # Quick parsing logic
        months = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
        }
        
        parsed = False
        for month_name, month_num in months.items():
            if month_name in due_str:
                # Find the day number
                words = due_str.replace("due", "").strip().split()
                for word in words:
                    cleaned_word = ''.join(c for c in word if c.isdigit())
                    if cleaned_word:
                        day_num = int(cleaned_word)
                        try:
                            task_date = datetime.datetime(meeting_year, month_num, day_num, 9, 0, 0)
                            parsed = True
                            break
                        except ValueError:
                            pass
            if parsed:
                break
                
        # If "today" or not parsed, set to today
        if "today" in due_str:
            task_date = datetime.datetime.now().replace(hour=9, minute=0, second=0)
            
        start_stamp = task_date.strftime("%Y%m%dT%H%M%SZ")
        end_stamp = (task_date + datetime.timedelta(minutes=30)).strftime("%Y%m%dT%H%M%SZ")
        uid = f"{uuid.uuid4()}@meetinsight.com"
        
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{now}",
            f"DTSTART:{start_stamp}",
            f"DTEND:{end_stamp}",
            f"SUMMARY:MeetInsight Task: {task_text}",
            f"DESCRIPTION:Assignee: {assignee}\\nPriority: {priority}\\nDue: {item.get('due_date')}",
            "STATUS:CONFIRMED",
            "TRANSP:OPAQUE",
            "END:VEVENT"
        ])
        
    lines.append("END:VCALENDAR")
    
    ics_content = "\r\n".join(lines)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        f.write(ics_content)
        
    return os.path.abspath(output_path)
