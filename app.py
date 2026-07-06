# app.py

import os
import time
import json
import copy
import tempfile
import streamlit as st
import google.generativeai as genai

# Import helper utilities
from utils.helpers import load_css, ensure_directories, format_seconds, build_brand_lockup
from utils.sample_data import SAMPLE_REPORT
from utils.ui import (
    render_html,
    esc,
    build_brief_card,
    build_decisions_card,
    build_action_item_row,
    build_meeting_arc_card,
    build_airtime_card,
    build_risks_card,
    build_changes_card,
    build_questions_card,
    build_followup_email_preview,
    build_transcript_entries_html,
    build_recent_meeting_card,
)

# Import backend modules
from media.audio_extractor import prepare_audio_file
from media.transcriber import transcribe_audio, get_api_key
from coordinator.orchestrator import CoordinatorOrchestrator

# Import exporters
from exports.pdf_exporter import generate_pdf_report
from exports.md_exporter import generate_markdown_report
from exports.ics_exporter import generate_ics_calendar

# Set Streamlit page configuration
st.set_page_config(
    page_title="MeetInsight — Meeting Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure folders exist
ensure_directories()

# Load custom styling
load_css("assets/style.css")

# --- Initialize Session State ---
if "current_report" not in st.session_state:
    st.session_state.current_report = None
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "New meeting"  # Default home page is upload
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "email_body" not in st.session_state:
    st.session_state.email_body = ""
if "email_tone" not in st.session_state:
    st.session_state.email_tone = "Concise"
if "email_to" not in st.session_state:
    st.session_state.email_to = "growth-pod@company.com"
if "email_cc" not in st.session_state:
    st.session_state.email_cc = ""
if "email_subject" not in st.session_state:
    st.session_state.email_subject = "Q3 Roadmap Review — decisions & next steps"
if "email_suggestion_added" not in st.session_state:
    st.session_state.email_suggestion_added = False
if "transcript_search" not in st.session_state:
    st.session_state.transcript_search = ""
if "selected_speakers" not in st.session_state:
    st.session_state.selected_speakers = []
if "only_ai_events" not in st.session_state:
    st.session_state.only_ai_events = False
if "chat_input_val" not in st.session_state:
    st.session_state.chat_input_val = ""
if "dash_export_select" not in st.session_state:
    st.session_state.dash_export_select = "Export format"
if "upload_reset_key" not in st.session_state:
    st.session_state.upload_reset_key = 0

# --- Helper Callback Functions ---
def load_sample_report():
    report = copy.deepcopy(SAMPLE_REPORT)
    st.session_state.current_report = report
    st.session_state.email_body = report["email"]["tones"]["Concise"]
    st.session_state.email_to = report["email"]["to"]
    st.session_state.email_cc = report["email"]["cc"]
    st.session_state.email_subject = report["email"]["subject"]
    st.session_state.email_tone = "Concise"
    st.session_state.active_tab = "Dashboard"
    st.session_state.chat_history = []
    st.session_state.transcript_search = ""
    st.session_state.selected_speakers = [s["speaker"] for s in report["airtime"]]
    st.session_state.only_ai_events = False
    st.session_state.dash_export_select = "Export format"
    st.toast("Loaded Q3 Roadmap Review sample report!", icon="✅")

def set_tab(tab_name):
    st.session_state.active_tab = tab_name

def render_clickable_recent_meeting(title: str, meta: str, *, container_key: str, button_key: str, status: str = "Ready"):
    """Render a recent-meeting card with a full-card invisible click target."""
    with st.container(key=container_key):
        render_html(build_recent_meeting_card(title, meta, status=status))
        if st.button(f"Open {title}", key=button_key, use_container_width=True):
            load_sample_report()
            st.rerun()

# --- Custom Navigation Bar Rendering ---
def render_navbar():
    col_brand, col_dash, col_trans, col_email, col_upload, col_spacer, col_profile = st.columns([3, 1.2, 1.2, 1.2, 1.5, 3, 1])
    
    with col_brand:
        render_html(build_brand_lockup(compact=True, show_tagline=True))
        
    with col_dash:
        is_active = st.session_state.active_tab == "Dashboard"
        disabled = st.session_state.current_report is None
        if st.button("Dashboard", key="nav_dash", disabled=disabled, use_container_width=True, type="primary" if is_active else "secondary"):
            set_tab("Dashboard")
            st.rerun()
            
    with col_trans:
        is_active = st.session_state.active_tab == "Transcript"
        disabled = st.session_state.current_report is None
        if st.button("Transcript", key="nav_trans", disabled=disabled, use_container_width=True, type="primary" if is_active else "secondary"):
            set_tab("Transcript")
            st.rerun()
            
    with col_email:
        is_active = st.session_state.active_tab == "Follow-up"
        disabled = st.session_state.current_report is None
        if st.button("Follow-up", key="nav_email", disabled=disabled, use_container_width=True, type="primary" if is_active else "secondary"):
            set_tab("Follow-up")
            st.rerun()
            
    with col_upload:
        is_active = st.session_state.active_tab == "New meeting"
        if st.button("New meeting", key="nav_upload", use_container_width=True, type="primary" if is_active else "secondary"):
            set_tab("New meeting")
            st.rerun()
            
    with col_profile:
        render_html("<div style='display:flex;justify-content:flex-end;align-items:center;'><div class='mi-profile-avatar'>PS</div></div>")

# Render navigation bar top of the app
render_navbar()
st.markdown("<hr class='mi-brand-bar' />", unsafe_allow_html=True)

# --- Sidebar "Ask This Meeting" chat component ---
def render_chat_sidebar():
    if not st.session_state.current_report:
        return
        
    report = st.session_state.current_report
    
    render_html("""
    <div class='chat-container'>
        <div class='chat-title'>Ask this meeting</div>
        <div class='chat-prompt'>"What did we decide about pricing, and who owns the next step?"</div>
    </div>
    """)
    
    # Query input
    query = st.text_input("Ask a question about the meeting:", key="chat_input", label_visibility="collapsed", placeholder="Type your question...")
    
    # Prompt Shortcuts
    shortcuts = [
        "Summarize risks for exec review",
        "Draft a Slack post for #product-updates",
        "List commitments made by Marcus"
    ]
    
    selected_shortcut = None
    for idx, prompt_text in enumerate(shortcuts):
        col_btn, col_arr = st.columns([9, 1])
        with col_btn:
            if st.button(prompt_text, key=f"shortcut_{idx}", use_container_width=True):
                selected_shortcut = prompt_text
                
    render_html(
        f"<div style='font-size:12px; color:#e0d0f0; margin-bottom:4px; margin-top:16px;'>"
        f"Transcript clarity {report['metadata']['clarity_score']}%</div>"
    )
    st.progress(report["metadata"]["clarity_score"] / 100)
    
    # Handle user query or shortcut selection
    run_query = None
    if query:
        run_query = query
        # Clear input field
        st.session_state.chat_input_val = ""
    elif selected_shortcut:
        run_query = selected_shortcut
        
    if run_query:
        st.markdown("---")
        st.markdown(f"**Q: {run_query}**")
        
        with st.spinner("AI is thinking..."):
            try:
                # Format transcript for context
                transcript_text = "\n".join([f"[{e.get('timestamp')}] {e.get('speaker')}: {e.get('text')}" for e in report["transcript"]])
                
                try:
                    api_key = get_api_key()
                except ValueError:
                    st.error("🔑 Gemini API key is missing or invalid. Please configure a valid API key in the 'New meeting' tab.")
                    return
                    
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                
                full_prompt = f"""
                You are MeetInsight, an enterprise meeting assistant. Answer the user's question accurately using only the provided meeting transcript.
                If the answer is not found in the transcript, politely state that it wasn't discussed.
                Keep your answer structured, clear, and professional.
                
                Transcript:
                \"\"\"
                {transcript_text}
                \"\"\"
                
                Question:
                {run_query}
                """
                response = model.generate_content(full_prompt)
                ans = response.text.strip()
                
                st.session_state.chat_history.append({"q": run_query, "a": ans})
            except Exception as e:
                st.error(f"Error answering question: {e}")
                
    # Display historical chat conversations
    if st.session_state.chat_history:
        st.markdown("### Conversation History")
        for chat in reversed(st.session_state.chat_history):
            st.markdown(f"**Question**: *{chat['q']}*")
            st.markdown(chat['a'])
            st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px dotted #ccc;' />", unsafe_allow_html=True)

# Render Chat Sidebar in the actual Streamlit Sidebar
with st.sidebar:
    render_html(f'<div class="mi-sidebar-brand">{build_brand_lockup(show_tagline=True)}</div>')
    with st.container(border=True):
        render_html("<div style='font-weight: 700; color: #7A1636; font-size: 14px; margin-bottom: 8px;'>Gemini API Key</div>")
        
        active_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if active_key and active_key not in ["", "YOUR_API_KEY_HERE"]:
            masked_key = active_key[:6] + "..." + active_key[-4:] if len(active_key) > 10 else "Active Key"
            render_html(f"<div style='font-size: 12px; color: #16a34a; font-weight: 600; margin-bottom: 8px;'>● Active: {esc(masked_key)}</div>")
        else:
            render_html("<div style='font-size: 12px; color: #dc2626; font-weight: 600; margin-bottom: 8px;'>● Missing API Key</div>")
            
        user_key = st.text_input("Change Key:", type="password", key="input_sidebar_api_key", label_visibility="collapsed", placeholder="Paste new key...")
        
        if st.button("Save & Test Key", key="btn_save_sidebar_key", use_container_width=True, type="primary"):
            if user_key:
                from utils.helpers import save_api_key_to_env, verify_gemini_connectivity
                with st.spinner("Testing connectivity..."):
                    if verify_gemini_connectivity(user_key):
                        if save_api_key_to_env(user_key):
                            st.success("Success! Key updated.")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Failed to save key.")
                    else:
                        st.error("Invalid API Key!")
            else:
                st.error("Key cannot be empty.")
    
    render_chat_sidebar()


# ==============================================================================
# VIEW: NEW MEETING (UPLOAD / UPLOAD STATE / SAMPLE REPORT SELECTOR)
# ==============================================================================
if st.session_state.active_tab == "New meeting":
    st.markdown("<div style='max-width: 900px; margin: 0 auto;'>", unsafe_allow_html=True)
    
    col_hdr, col_sample = st.columns([6, 3])
    with col_hdr:
        render_html("<span class='mi-step-label'>STEP 1 OF 3</span>")
        st.markdown("<h1 style='margin-top:0;'>Upload a meeting</h1>", unsafe_allow_html=True)
        render_html("<p class='mi-meta-text' style='font-size:16px; margin-top:-10px;'>We'll transcribe, diarise, and extract every decision, action and risk.</p>")
    with col_sample:
        st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
        if st.button("See a sample report →", key="btn_see_sample", use_container_width=True, type="secondary"):
            load_sample_report()
            st.rerun()

    uploaded_file = st.file_uploader(
        "Drop a recording to start",
        type=["mp3", "wav", "m4a", "mp4"],
        accept_multiple_files=False,
        key=f"meeting_file_uploader_{st.session_state.upload_reset_key}",
        help="MP3, WAV, M4A, MP4 · up to 4 hours · 2 GB max · your files never leave your workspace",
    )
    render_html(
        "<p class='mi-meta-text mi-upload-hint'>"
        "Select or drag a file above to begin transcription and analysis."
        "</p>"
    )
    
    # Grid of Features
    col_feat1, col_feat2, col_feat3 = st.columns(3)
    with col_feat1:
        st.markdown("<div class='mi-card' style='padding: 16px;'><div style='font-size:18px; margin-bottom:6px; color:#A67CFF;'>◆</div><div style='font-weight:600; font-size:14px; color:#2D2D2D;'>SOC 2 encrypted</div><div class='mi-meta-text' style='font-size:12px; margin-top:2px;'>Files never leave your workspace.</div></div>", unsafe_allow_html=True)
    with col_feat2:
        st.markdown("<div class='mi-card' style='padding: 16px;'><div style='font-size:18px; margin-bottom:6px; color:#7A1636;'>◆</div><div style='font-weight:600; font-size:14px; color:#2D2D2D;'>60-second brief</div><div class='mi-meta-text' style='font-size:12px; margin-top:2px;'>Decisions in under a minute.</div></div>", unsafe_allow_html=True)
    with col_feat3:
        st.markdown("<div class='mi-card' style='padding: 16px;'><div style='font-size:18px; margin-bottom:6px; color:#A67CFF;'>◆</div><div style='font-weight:600; font-size:14px; color:#2D2D2D;'>Any format</div><div class='mi-meta-text' style='font-size:12px; margin-top:2px;'>MP3, WAV, M4A, MP4 supported.</div></div>", unsafe_allow_html=True)
        
    # Start Processing Logic
    if uploaded_file is not None:
        st.markdown("---")
        col_back, col_proc = st.columns([7, 3])
        with col_back:
            if st.button("← Back", key="btn_upload_back"):
                st.session_state.upload_reset_key += 1
                st.rerun()
        with col_proc:
            if st.button("Start processing", key="btn_start_proc", use_container_width=True, type="primary"):
                env_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
                if not env_key:
                    st.error("❌ Missing Gemini API Key! Please configure and verify your key in the section below.")
                else:
                    # Save file to temp location
                    with tempfile.TemporaryDirectory() as temp_dir:
                        input_path = os.path.join(temp_dir, uploaded_file.name)
                        with open(input_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        status_placeholder = st.empty()
                        progress_bar = st.progress(0)
                        
                        try:
                            # Step 1: Normalize audio (extract/convert to MP3)
                            status_placeholder.info("Step 1/3: Preparing audio for transcription...")
                            progress_bar.progress(10)
                            audio_path = prepare_audio_file(input_path, temp_dir)

                            # Step 2: Speech-to-Text with Speaker Identification
                            status_placeholder.info("Step 2/3: Transcribing audio with speaker diarization...")
                            progress_bar.progress(40)
                            diarized_transcript = transcribe_audio(audio_path)
                            
                            # Step 3: Run parallel AI analyzers
                            status_placeholder.info("Step 3/3: Running parallel AI intelligence agents...")
                            progress_bar.progress(75)
                            
                            title_clean = os.path.splitext(uploaded_file.name)[0].replace("_", " ").title()
                            coordinator = CoordinatorOrchestrator()
                            report = coordinator.process_transcript(diarized_transcript, title=title_clean)
                            
                            # Add dynamic length estimation based on transcript timestamps
                            if len(diarized_transcript) > 0:
                                # Estimate duration based on last timestamp
                                last_ts = diarized_transcript[-1].get("timestamp", "00:00")
                                report["metadata"]["duration"] = f"{last_ts} mins"
                            else:
                                report["metadata"]["duration"] = "0 min"
                                
                            # Save to session state
                            st.session_state.current_report = report
                            st.session_state.email_body = report["email"]["tones"]["Concise"]
                            st.session_state.email_to = report["email"]["to"]
                            st.session_state.email_cc = report["email"]["cc"]
                            st.session_state.email_subject = report["email"]["subject"]
                            st.session_state.email_tone = "Concise"
                            st.session_state.chat_history = []
                            st.session_state.transcript_search = ""
                            st.session_state.selected_speakers = list(set([entry["speaker"] for entry in report["transcript"]]))
                            st.session_state.only_ai_events = False
                            st.session_state.active_tab = "Dashboard"
                            
                            progress_bar.progress(100)
                            status_placeholder.success("Processing completed successfully!")
                            time.sleep(1)
                            st.rerun()
                            
                        except Exception as pe:
                            st.error(f"Failed to process meeting recording: {pe}")
                            status_placeholder.empty()
                            progress_bar.empty()



    # Recent meetings card
    st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
    st.markdown("### Recent meetings")
    
    col_meet1, col_meet2 = st.columns([6, 3])
    with col_meet1:
        render_clickable_recent_meeting(
            "Q3 Roadmap Review — Growth Pod",
            "Today · 10:04 · 5 speakers · 58m",
            container_key="recent_meeting_q3",
            button_key="btn_recent_1",
            status="Ready",
        )
        render_clickable_recent_meeting(
            "Design review — Checkout v3",
            "Yesterday · 15:20 · 4 speakers · 42m",
            container_key="recent_meeting_design",
            button_key="btn_recent_2",
            status="Ready",
        )
            
    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# VIEW: DASHBOARD
# ==============================================================================
elif st.session_state.active_tab == "Dashboard":
    if not st.session_state.current_report:
        st.warning("No report loaded. Please upload a meeting first or load the sample.")
        st.stop()
        
    report = st.session_state.current_report
    meta = report["metadata"]
    metrics = report["metrics"]
    
    # Header Info
    render_html("<span class='mi-status-ready'>● REPORT READY</span>")
    col_title, col_actions = st.columns([7, 3])
    
    with col_title:
        st.markdown(f"<h1 style='margin-top:0; margin-bottom:8px;'>{meta['title']}</h1>", unsafe_allow_html=True)
        render_html(f"<p class='mi-meta-text'>📅 {meta['date']} · {meta['time']} | ⏱️ {meta['duration']} | 👥 {meta['speakers_count']} speakers | 🤖 {meta['engine']} | ⚡ {meta['processed_time']}</p>")
        
    with col_actions:
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        col_t, col_exp, col_em = st.columns([1, 1, 1.2])
        with col_t:
            if st.button("Open transcript", key="dash_btn_trans", type="secondary"):
                set_tab("Transcript")
                st.rerun()
        with col_exp:
            # Custom styled Export selector (PDF, Markdown, ICS Calendar)
            export_format = st.selectbox(
                "Export",
                options=["Export format", "PDF Report", "Markdown", "Calendar (.ics)"],
                label_visibility="collapsed",
                key="dash_export_select"
            )
            
            # Export handler
            if export_format == "PDF Report":
                pdf_path = os.path.join("exports", "MeetInsight_Report.pdf")
                generate_pdf_report(report, pdf_path)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download PDF",
                        data=f,
                        file_name="MeetInsight_Report.pdf",
                        mime="application/pdf",
                        key="btn_dl_pdf"
                    )
            elif export_format == "Markdown":
                md_path = os.path.join("exports", "MeetInsight_Report.md")
                generate_markdown_report(report, md_path)
                with open(md_path, "r", encoding="utf-8") as f:
                    st.download_button(
                        "⬇️ Download Markdown",
                        data=f.read(),
                        file_name="MeetInsight_Report.md",
                        mime="text/markdown",
                        key="btn_dl_md"
                    )
            elif export_format == "Calendar (.ics)":
                ics_path = os.path.join("exports", "MeetInsight_Tasks.ics")
                generate_ics_calendar(report["action_items"], ics_path)
                with open(ics_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download Calendar",
                        data=f,
                        file_name="MeetInsight_Tasks.ics",
                        mime="text/calendar",
                        key="btn_dl_ics"
                    )
        with col_em:
            if st.button("Send follow-up", key="dash_btn_email", type="primary"):
                set_tab("Follow-up")
                st.rerun()

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    
    # 4 Metric Cards Row
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        render_html(f"""
        <div class='mi-metric-card'>
            <div class='mi-metric-label'>Decisions</div>
            <div class='mi-metric-val'>{metrics['decisions_total']}</div>
            <div class='mi-metric-sub'>{metrics['decisions_high_impact']} high-impact</div>
        </div>
        """)
    with col_m2:
        render_html(f"""
        <div class='mi-metric-card'>
            <div class='mi-metric-label'>Actions</div>
            <div class='mi-metric-val'>{metrics['actions_total']}</div>
            <div class='mi-metric-sub'>{metrics['actions_due_this_week']} due this week</div>
        </div>
        """)
    with col_m3:
        render_html(f"""
        <div class='mi-metric-card'>
            <div class='mi-metric-label'>Risks</div>
            <div class='mi-metric-val'>{metrics['risks_total']}</div>
            <div class='mi-metric-sub'>{metrics['risks_unresolved']} unresolved</div>
        </div>
        """)
    with col_m4:
        render_html(f"""
        <div class='mi-metric-card'>
            <div class='mi-metric-label'>Clarity</div>
            <div class='mi-metric-val'>{meta['clarity_score']}%</div>
            <div class='mi-metric-sub'>Speech quality</div>
        </div>
        """)

    # The 60-Second Brief Card
    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
    render_html(build_brief_card(report["brief"]))

    # Decisions and Actions side-by-side
    col_c1, col_c2 = st.columns([5, 5])
    
    with col_c1:
        _, link_col = st.columns([8, 2])
        with link_col:
            if st.button("View all →", key="link_all_decisions"):
                set_tab("Transcript")
                st.session_state.only_ai_events = True
                st.rerun()
        render_html(build_decisions_card(report["decisions"], limit=4))
        
    with col_c2:
        _, link_col = st.columns([8, 2])
        with link_col:
            if st.button("View all →", key="link_all_actions"):
                set_tab("Transcript")
                st.session_state.only_ai_events = True
                st.rerun()
        with st.container(border=True):
            render_html(
                f"<div class='mi-card-title'>Action items "
                f"<span class='pill pill-tag' style='margin-left:8px;'>{metrics['actions_total']}</span></div>"
            )
            for idx, a in enumerate(report["action_items"][:5]):
                st_col_chk, st_col_det = st.columns([1, 9])
                with st_col_chk:
                    comp = st.checkbox("Complete", value=a.get("completed", False), key=f"chk_act_{a['id']}", label_visibility="collapsed")
                    report["action_items"][idx]["completed"] = comp
                with st_col_det:
                    render_html(build_action_item_row(a, comp))

    render_html(build_meeting_arc_card(report["timeline"], meta.get("duration", "")))
    render_html(build_airtime_card(report["airtime"]))

    # Risks, Change requests, Open questions Row
    col_b1, col_b2, col_b3 = st.columns(3)
    
    with col_b1:
        render_html(build_risks_card(report["risks"]))
        
    with col_b2:
        render_html(build_changes_card(report["changes"]))
        
    with col_b3:
        render_html(build_questions_card(report["questions"]))

    # Follow-up Email Card
    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
    _, email_btn_col = st.columns([8, 2])
    with email_btn_col:
        if st.button("Open email tab", key="btn_open_email_tab", use_container_width=True):
            set_tab("Follow-up")
            st.rerun()
    render_html(
        build_followup_email_preview(
            st.session_state.email_to,
            st.session_state.email_subject,
            st.session_state.email_body,
        )
    )


# ==============================================================================
# VIEW: TRANSCRIPT
# ==============================================================================
elif st.session_state.active_tab == "Transcript":
    if not st.session_state.current_report:
        st.warning("No report loaded. Please upload a meeting first.")
        st.stop()
        
    report = st.session_state.current_report
    
    render_html(f"<span class='mi-section-label'>TRANSCRIPT · {esc(report['metadata']['duration'])}</span>")
    st.markdown(f"<h1 style='margin-top:0;'>{report['metadata']['title']}</h1>", unsafe_allow_html=True)
    
    col_sidebar, col_content = st.columns([3, 7])
    
    # Sidebar Filters
    with col_sidebar:
        with st.container(border=True):
            st.markdown("### Filters")
            
            search_query = st.text_input("Search transcript...", value=st.session_state.transcript_search, placeholder="Search words...")
            st.session_state.transcript_search = search_query
            
            only_ai = st.checkbox("Only AI-detected events", value=st.session_state.only_ai_events)
            st.session_state.only_ai_events = only_ai
            
            st.markdown("---")
            st.markdown("### Speakers")
            
            all_speakers = list(set([entry["speaker"] for entry in report["transcript"]]))
            if not st.session_state.selected_speakers:
                st.session_state.selected_speakers = all_speakers
                
            selected_sps = []
            for sp in all_speakers:
                chk_sp = st.checkbox(f"● {sp}", value=(sp in st.session_state.selected_speakers), key=f"filter_sp_{sp}")
                if chk_sp:
                    selected_sps.append(sp)
            st.session_state.selected_speakers = selected_sps
            
            st.markdown("---")
            st.markdown("### Jump to")
            
            for entry in report["transcript"]:
                if entry.get("tag"):
                    lbl_jump = f"{entry['timestamp']} {entry['tag']}"
                    if st.button(lbl_jump, key=f"jump_btn_{entry['timestamp']}_{entry['tag']}", use_container_width=True):
                        st.session_state.transcript_search = entry["text"][:20]
                        st.rerun()

    # Transcript Main Area
    with col_content:
        filtered_entries = []
        for entry in report["transcript"]:
            if entry["speaker"] not in st.session_state.selected_speakers:
                if not any(entry["speaker"] in sp or sp in entry["speaker"] for sp in st.session_state.selected_speakers):
                    continue
                
            if st.session_state.only_ai_events and not entry.get("tag"):
                continue
                
            if st.session_state.transcript_search and st.session_state.transcript_search.lower() not in entry["text"].lower():
                continue
                
            filtered_entries.append(entry)
            
        if not filtered_entries:
            st.info("No transcript segments match the active filters.")
        else:
            render_html(
                build_transcript_entries_html(
                    filtered_entries,
                    report["airtime"],
                    st.session_state.transcript_search,
                )
            )


# ==============================================================================
# VIEW: FOLLOW-UP EMAIL
# ==============================================================================
elif st.session_state.active_tab == "Follow-up":
    if not st.session_state.current_report:
        st.warning("No report loaded. Please upload a meeting first.")
        st.stop()
        
    report = st.session_state.current_report
    
    render_html("<span class='mi-section-label'>FOLLOW-UP EMAIL</span>")
    st.markdown(f"<h1 style='margin-top:0;'>{report['metadata']['title']} — decisions & next steps</h1>", unsafe_allow_html=True)
    
    col_email_editor, col_email_meta = st.columns([7, 3])
    
    with col_email_editor:
        with st.container(border=True):
            email_to_input = st.text_input("To", value=st.session_state.email_to)
            st.session_state.email_to = email_to_input
            
            email_cc_input = st.text_input("CC", value=st.session_state.email_cc, placeholder="Add stakeholders...")
            st.session_state.email_cc = email_cc_input
            
            email_subj_input = st.text_input("Subject", value=st.session_state.email_subject)
            st.session_state.email_subject = email_subj_input
            
            email_body_input = st.text_area("Email Body", value=st.session_state.email_body, height=400)
            st.session_state.email_body = email_body_input
            
            st.markdown("---")
            col_regen, col_copy, col_send = st.columns([2, 2, 3])
            with col_regen:
                if st.button("🔄 Regenerate", key="btn_regen_email"):
                    st.session_state.email_body = report["email"]["tones"][st.session_state.email_tone]
                    st.session_state.email_suggestion_added = False
                    st.toast("Restored tone template!", icon="🔄")
                    st.rerun()
            with col_copy:
                if st.button("📋 Copy to clipboard", key="btn_copy_email"):
                    st.toast("Email copied to clipboard!", icon="📋")
            with col_send:
                if st.button("Send email", key="btn_send_email", use_container_width=True, type="primary"):
                    st.success("Follow-up email sent successfully!")
        
    with col_email_meta:
        with st.container(border=True):
            st.markdown("### Tone selector")
            
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                if st.button("Concise", key="tone_btn_concise", type="primary" if st.session_state.email_tone == "Concise" else "secondary"):
                    st.session_state.email_tone = "Concise"
                    st.session_state.email_body = report["email"]["tones"]["Concise"]
                    st.session_state.email_suggestion_added = False
                    st.rerun()
                if st.button("Warm", key="tone_btn_warm", type="primary" if st.session_state.email_tone == "Warm" else "secondary"):
                    st.session_state.email_tone = "Warm"
                    st.session_state.email_body = report["email"]["tones"]["Warm"]
                    st.session_state.email_suggestion_added = False
                    st.rerun()
            with col_t2:
                if st.button("Executive", key="tone_btn_exec", type="primary" if st.session_state.email_tone == "Executive" else "secondary"):
                    st.session_state.email_tone = "Executive"
                    st.session_state.email_body = report["email"]["tones"]["Executive"]
                    st.session_state.email_suggestion_added = False
                    st.rerun()
                if st.button("Detailed", key="tone_btn_detailed", type="primary" if st.session_state.email_tone == "Detailed" else "secondary"):
                    st.session_state.email_tone = "Detailed"
                    st.session_state.email_body = report["email"]["tones"]["Detailed"]
                    st.session_state.email_suggestion_added = False
                    st.rerun()
        
        with st.container(border=True):
            st.markdown("### Includes")
            render_html(f"""
            <ul style='font-size:14px; color:#4b5563; padding-left:20px; line-height:1.8; margin:0;'>
                <li>● {report['metrics']['decisions_total']} decisions</li>
                <li>● {report['metrics']['actions_total']} action items</li>
                <li>● {report['metrics']['risks_total']} open risks</li>
                <li>● {len(report['changes'])} change requests</li>
            </ul>
            """)
        
        render_html(
            f"""
            <div class='chat-container'>
                <div class='chat-title'>Suggested by MeetInsight</div>
                <div style='font-size:13px; line-height:1.5; margin-bottom:16px;'>{esc(report['email']['suggestion'])}</div>
            </div>
            """
        )
        if not st.session_state.email_suggestion_added:
            if st.button("Insert into email →", key="btn_insert_sugg", use_container_width=True):
                st.session_state.email_body += f"\n\nNote: {report['email']['suggestion']}"
                st.session_state.email_suggestion_added = True
                st.toast("Inserted suggestion into email body!", icon="📝")
                st.rerun()
        else:
            render_html("<div style='font-size:12px; color:#10b981; font-weight:bold;'>✅ Suggestion inserted</div>")
