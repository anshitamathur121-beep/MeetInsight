# utils/ui.py — HTML rendering helpers for Streamlit dashboard sections

import html
import re
from typing import Any

import streamlit as st


def esc(text: Any) -> str:
    """Escape text for safe HTML embedding."""
    return html.escape(str(text) if text is not None else "")


def format_inline_md(text: Any) -> str:
    """Convert **bold** markers to <strong> while escaping other content."""
    raw = str(text) if text is not None else ""
    parts = re.split(r"\*\*(.+?)\*\*", raw)
    result: list[str] = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            result.append(f"<strong>{esc(part)}</strong>")
        else:
            result.append(esc(part))
    return "".join(result)


def render_html(content: str) -> None:
    """Render a complete HTML fragment via st.html (not st.markdown)."""
    content = content.strip()
    if content:
        st.html(content)


def build_recent_meeting_card(title: str, meta: str, *, status: str = "Ready") -> str:
    """HTML for a recent-meeting row (visual layer; click handled by overlay button)."""
    return f"""
    <div class="mi-recent-meeting-card">
        <div class="mi-recent-meeting-card__body">
            <div class="mi-recent-meeting-card__icon">♪</div>
            <div>
                <div class="mi-recent-meeting-card__title">{esc(title)}</div>
                <div class="mi-recent-meeting-card__meta">{esc(meta)}</div>
            </div>
        </div>
        <div class="mi-recent-meeting-card__actions">
            <span class="mi-recent-meeting-card__status">{esc(status)}</span>
            <div class="mi-accent-arrow" aria-hidden="true">→</div>
        </div>
    </div>
    """


def impact_pill_class(impact: str) -> str:
    level = (impact or "").lower()
    if level == "high":
        return "pill-high"
    if level == "medium":
        return "pill-medium"
    return "pill-low"


def speaker_color(speaker: str, airtime: list[dict]) -> str:
    for entry in airtime:
        sp = entry.get("speaker", "")
        if sp == speaker or sp.startswith(speaker) or speaker.startswith(sp):
            return entry.get("color", "#7A1636")
    return "#7A1636"


def build_brief_card(brief: dict) -> str:
    tags = " ".join(
        f"<span class='pill pill-tag'>{esc(t)}</span>" for t in brief.get("tags", [])
    )
    return f"""
    <div class='mi-card mi-brief-card'>
        <div class='mi-brief-label'>THE 60-SECOND BRIEF</div>
        <div class='mi-brief-body'>{format_inline_md(brief.get('summary', ''))}</div>
        <div style='margin-top:12px; display:flex; gap:8px; flex-wrap:wrap;'>{tags}</div>
    </div>
    """


def build_decisions_card(decisions: list[dict], limit: int = 4) -> str:
    items: list[str] = []
    for d in decisions[:limit]:
        pill = impact_pill_class(d.get("impact", ""))
        items.append(
            f"""
            <div class='decision-item'>
                <div class='decision-num'>{esc(d.get('id', ''))}</div>
                <div class='decision-content'>
                    <div class='decision-text'>{esc(d.get('text', ''))}</div>
                    <div class='decision-meta'>
                        <span class='pill pill-tag'>{esc(d.get('speaker', ''))}</span>
                        <span>⏱️ {esc(d.get('timestamp', ''))}</span>
                        <span class='pill {pill}'>{esc(d.get('impact', ''))}</span>
                    </div>
                </div>
            </div>
            """
        )
    shown = min(len(decisions), limit)
    return f"""
    <div class='mi-card'>
        <div class='mi-card-title'>Decisions <span class='pill pill-tag' style='margin-left:8px;'>{shown}</span></div>
        {''.join(items)}
    </div>
    """


def build_action_item_row(action: dict, completed: bool) -> str:
    pill = impact_pill_class(action.get("priority", ""))
    text_decor = "text-decoration: line-through; color: #9ca3af;" if completed else ""
    return f"""
    <div style='margin-bottom:8px;'>
        <div style='font-size:14px; font-weight:500; {text_decor}'>{esc(action.get('text', ''))}</div>
        <div style='display:flex; gap:12px; font-size:11px; color:#6b7280; align-items:center; margin-top:2px;'>
            <span class='pill pill-tag'>{esc(action.get('assignee', ''))}</span>
            <span>📅 {esc(action.get('due_date', ''))}</span>
            <span class='pill {pill}'>{esc(action.get('priority', ''))}</span>
        </div>
    </div>
    """


def build_meeting_arc_card(timeline: list[dict], duration: str = "") -> str:
    chapter_count = len(timeline)
    subtitle = f"{esc(duration)} · {chapter_count} chapters" if duration else f"{chapter_count} chapters"
    nodes: list[str] = []
    for node in timeline:
        color = esc(node.get("color", "#9ca3af"))
        nodes.append(
            f"""
            <div class='meeting-arc-node'>
                <div class='meeting-arc-timestamp'>{esc(node.get('timestamp', ''))}</div>
                <div class='meeting-arc-dot' style='background-color: {color};'></div>
                <div class='meeting-arc-label'>{esc(node.get('label', ''))}</div>
            </div>
            """
        )
    return f"""
    <div class='mi-card'>
        <div class='mi-card-title'>Meeting arc <span style='font-size:12px; font-weight:normal; color:#6b7280;'>{subtitle}</span></div>
        <div class='meeting-arc-container'>
            <div class='meeting-arc-line'></div>
            {''.join(nodes)}
        </div>
    </div>
    """


def build_airtime_card(airtime: list[dict]) -> str:
    bar_segments: list[str] = []
    legend_items: list[str] = []
    for speaker in airtime:
        pct = speaker.get("percentage", 0)
        color = esc(speaker.get("color", "#9ca3af"))
        name = esc(speaker.get("speaker", ""))
        bar_segments.append(
            f"<div class='airtime-segment' style='width: {pct}%; background-color: {color};' title='{name}: {pct}%'></div>"
        )
        legend_items.append(
            f"""
            <div style='display:flex; align-items:center; gap:6px; font-size:13px; font-weight:500; color:#4b5563;'>
                <div style='width:10px; height:10px; border-radius:50%; background-color:{color};'></div>
                <span>{name} {pct}%</span>
            </div>
            """
        )
    return f"""
    <div class='mi-card'>
        <div class='mi-card-title'>Airtime</div>
        <div style='height:12px; border-radius:6px; overflow:hidden; display:flex; margin-bottom:16px;'>
            {''.join(bar_segments)}
        </div>
        <div style='display:flex; gap:24px; flex-wrap:wrap;'>
            {''.join(legend_items)}
        </div>
    </div>
    """


def build_risks_card(risks: list[dict]) -> str:
    items: list[str] = []
    for risk in risks:
        items.append(
            f"""
            <div class='risk-item'>
                <div class='risk-header'>
                    <span class='risk-title'>{esc(risk.get('title', ''))}</span>
                    <span class='pill pill-p1'>{esc(risk.get('impact', ''))}</span>
                </div>
                <div class='risk-desc'>{esc(risk.get('description', ''))}</div>
            </div>
            """
        )
    return f"""
    <div class='mi-card' style='height:100%;'>
        <div class='mi-card-title'>Risks <span class='pill pill-tag'>{len(risks)}</span></div>
        {''.join(items)}
    </div>
    """


def build_changes_card(changes: list[dict]) -> str:
    items: list[str] = []
    for change in changes:
        items.append(
            f"""
            <div class='risk-item'>
                <div class='risk-header'>
                    <span class='risk-title mi-wine-emphasis'>{esc(change.get('title', ''))}</span>
                    <span class='pill pill-p1'>{esc(change.get('priority', ''))}</span>
                </div>
                <div style='font-size:11px; color:#6b7280; margin-top:4px;'>
                    👤 {esc(change.get('requestor', ''))} · ⏱️ {esc(change.get('timestamp', ''))} · <span class='pill pill-p2'>{esc(change.get('impact', ''))}</span>
                </div>
            </div>
            """
        )
    return f"""
    <div class='mi-card' style='height:100%;'>
        <div class='mi-card-title'>Change requests <span class='pill pill-tag'>{len(changes)}</span></div>
        {''.join(items)}
    </div>
    """


def build_questions_card(questions: list[dict]) -> str:
    items: list[str] = []
    for question in questions:
        items.append(
            f"""
            <div class='question-item'>
                <div class='question-text'>"{esc(question.get('text', ''))}"</div>
                <div class='question-speaker'>— {esc(question.get('speaker', ''))}</div>
            </div>
            """
        )
    return f"""
    <div class='mi-card' style='height:100%;'>
        <div class='mi-card-title'>Open questions <span class='pill pill-tag'>{len(questions)}</span></div>
        {''.join(items)}
    </div>
    """


def build_followup_email_preview(email_to: str, email_subject: str, email_body: str) -> str:
    return f"""
    <div class='mi-card'>
        <div class='mi-card-title'>Follow-up email</div>
        <div style='border:1px solid #edeaf2; border-radius:12px; padding:16px; background:#fafafc; font-family:monospace; white-space:pre-wrap; font-size:13px; color:#1f2937; height:180px; overflow-y:auto;'>
To: {esc(email_to)}
Subject: {esc(email_subject)}

{esc(email_body)}
        </div>
    </div>
    """


def build_transcript_entries_html(
    entries: list[dict],
    airtime: list[dict],
    search_query: str = "",
) -> str:
    rows: list[str] = []
    query = search_query.lower()
    for entry in entries:
        sp_color = esc(speaker_color(entry.get("speaker", ""), airtime))
        initials = "".join(part[0] for part in entry.get("speaker", "").split() if part)[:2].upper()
        tag_pill = ""
        if entry.get("tag"):
            tag_pill = f"<span class='pill pill-medium' style='margin-left: 8px;'>🎯 {esc(entry['tag'])}</span>"

        text_display = esc(entry.get("text", ""))
        if query and query in entry.get("text", "").lower():
            text_display = re.sub(
                re.escape(query),
                f"<mark style='background:#fef08a;'>{esc(query)}</mark>",
                text_display,
                flags=re.IGNORECASE,
            )

        rows.append(
            f"""
            <div style='display: flex; gap: 16px; margin-bottom: 20px; border-left: 3px solid {sp_color}; padding-left: 12px;'>
                <div style='color: #6b7280; font-size: 12px; font-weight: 600; width: 45px; margin-top: 4px;'>{esc(entry.get('timestamp', ''))}</div>
                <div style='background-color: {sp_color}; color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px; flex-shrink: 0;'>
                    {esc(initials)}
                </div>
                <div style='flex-grow: 1;'>
                    <div style='font-weight: 700; font-size: 13px; color: var(--text-primary); display: flex; align-items: center;'>
                        {esc(entry.get('speaker', ''))}
                        {tag_pill}
                    </div>
                    <div style='font-size: 14px; color: var(--text-secondary); margin-top: 4px; line-height: 1.5;'>{text_display}</div>
                </div>
            </div>
            """
        )
    return f"""
    <div class='mi-card' style='max-height:800px; overflow-y:auto;'>
        {''.join(rows)}
    </div>
    """
