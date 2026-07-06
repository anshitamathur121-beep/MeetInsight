# exports/md_exporter.py

import os

def generate_markdown_report(report_data: dict, output_path: str) -> str:
    """
    Generates a Markdown file representing the meeting intelligence report.
    
    Args:
        report_data (dict): The complete meeting report dictionary.
        output_path (str): Filepath to save the generated Markdown.
        
    Returns:
        str: Absolute path to the Markdown file.
    """
    meta = report_data.get("metadata", {})
    brief = report_data.get("brief", {})
    decisions = report_data.get("decisions", [])
    actions = report_data.get("action_items", [])
    risks = report_data.get("risks", [])
    changes = report_data.get("changes", [])
    questions = report_data.get("questions", [])
    transcript = report_data.get("transcript", [])
    
    lines = []
    lines.append(f"# {meta.get('title', 'Meeting Intelligence Report')}")
    lines.append("")
    lines.append(f"- **Date**: {meta.get('date', 'N/A')}")
    lines.append(f"- **Time**: {meta.get('time', 'N/A')}")
    lines.append(f"- **Duration**: {meta.get('duration', 'N/A')}")
    lines.append(f"- **Speakers**: {meta.get('speakers_count', 0)}")
    lines.append(f"- **Engine**: {meta.get('engine', 'N/A')}")
    lines.append(f"- **Clarity Score**: {meta.get('clarity_score', 87)}%")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 60-Second Brief
    lines.append("## 60-Second Brief")
    lines.append(brief.get("summary", "No summary available."))
    lines.append("")
    if brief.get("tags"):
        tags_line = " ".join([f"`{t}`" for t in brief.get("tags", [])])
        lines.append(tags_line)
    lines.append("")
    
    # Key Decisions
    lines.append("## Key Decisions")
    if decisions:
        for idx, d in enumerate(decisions, 1):
            lines.append(f"{idx}. **{d.get('text', '')}**")
            lines.append(f"   - *Owner*: {d.get('speaker', 'Team')}")
            lines.append(f"   - *Timestamp*: {d.get('timestamp', '00:00')}")
            lines.append(f"   - *Impact*: {d.get('impact', 'Medium')}")
    else:
        lines.append("*No decisions detected.*")
    lines.append("")
    
    # Action Items
    lines.append("## Action Items")
    if actions:
        for idx, a in enumerate(actions, 1):
            status = "[x]" if a.get("completed") else "[ ]"
            lines.append(f"{idx}. {status} **{a.get('text', '')}**")
            lines.append(f"   - *Assignee*: {a.get('assignee', 'Unassigned')}")
            lines.append(f"   - *Due Date*: {a.get('due_date', 'TBD')}")
            lines.append(f"   - *Priority*: {a.get('priority', 'Medium')}")
    else:
        lines.append("*No action items detected.*")
    lines.append("")
    
    # Risks & Blockers
    lines.append("## Risks & Blockers")
    if risks:
        for idx, r in enumerate(risks, 1):
            lines.append(f"{idx}. **{r.get('title', '')}** (Impact: {r.get('impact', 'Medium')})")
            lines.append(f"   - *Description*: {r.get('description', '')}")
    else:
        lines.append("*No risks or blockers detected.*")
    lines.append("")
    
    # Change Requests
    lines.append("## Change Requests")
    if changes:
        for idx, c in enumerate(changes, 1):
            lines.append(f"{idx}. **{c.get('title', '')}** (Priority: {c.get('priority', 'P2')})")
            lines.append(f"   - *Requested By*: {c.get('requestor', 'N/A')}")
            lines.append(f"   - *Timestamp*: {c.get('timestamp', 'N/A')}")
    else:
        lines.append("*No change requests detected.*")
    lines.append("")
    
    # Open Questions
    lines.append("## Open Questions")
    if questions:
        for idx, q in enumerate(questions, 1):
            lines.append(f"{idx}. *\"{q.get('text', '')}\"* — asked by {q.get('speaker', 'N/A')}")
    else:
        lines.append("*No open questions detected.*")
    lines.append("")
    
    # Full Transcript
    lines.append("## Diarized Transcript")
    if transcript:
        for entry in transcript:
            tag_str = f" `[{entry.get('tag')}]`" if entry.get("tag") else ""
            lines.append(f"**[{entry.get('timestamp', '00:00')}] {entry.get('speaker', 'Unknown')}**{tag_str}:")
            lines.append(f"> {entry.get('text', '')}")
            lines.append("")
    else:
        lines.append("*No transcript entries.*")
        
    md_content = "\n".join(lines)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    return os.path.abspath(output_path)
