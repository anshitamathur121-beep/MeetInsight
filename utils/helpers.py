# utils/helpers.py

import os
import streamlit as st

def format_seconds(seconds: int) -> str:
    """Format seconds to MM:SS or HH:MM:SS."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def parse_timestamp_to_seconds(ts: str) -> int:
    """Convert timestamp format (MM:SS or HH:MM:SS) to total seconds."""
    parts = list(map(int, ts.split(":")))
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    elif len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    return 0

def load_css(css_file_path: str):
    """Load and inject custom CSS from a file into Streamlit."""
    if os.path.exists(css_file_path):
        with open(css_file_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"CSS file not found at {css_file_path}")


def build_brand_lockup(*, compact: bool = False, show_tagline: bool = False) -> str:
    """Typography logo: MEET serif + diagonal Insight script + lavender orbit."""
    size_classes = ["mi-logo-lockup"]
    if compact:
        size_classes.append("mi-logo-lockup--compact")
        if show_tagline:
            size_classes.append("mi-logo-lockup--compact-tagline")
    else:
        size_classes.append("mi-logo-lockup--full")

    tagline_block = ""
    if show_tagline:
        tagline_block = '<div class="mi-logo-tagline">From conversations to clarity.</div>'
        if not compact:
            tagline_block += '<div class="mi-logo-divider" aria-hidden="true"></div>'

    size_class = " ".join(size_classes)

    return f"""
    <div class="{size_class}">
        <div class="mi-logo-mark" aria-hidden="true">
            <svg class="mi-logo-orbit" viewBox="0 0 128 72" xmlns="http://www.w3.org/2000/svg">
                <ellipse cx="64" cy="36" rx="56" ry="28" fill="none" stroke="#A67CFF" stroke-width="1.25" stroke-opacity="0.35"/>
                <path d="M12 44 C36 8, 92 8, 116 34" fill="none" stroke="#A67CFF" stroke-width="1.75" stroke-linecap="round" stroke-opacity="0.55"/>
            </svg>
            <div class="mi-logo-type">
                <span class="mi-logo-meet">MEET</span>
                <span class="mi-logo-insight">Insight</span>
            </div>
        </div>
        {tagline_block}
    </div>
    """

def ensure_directories():
    """Ensure that the necessary system directories exist."""
    directories = [
        "uploads",
        "assets",
        "exports"
    ]
    for d in directories:
        os.makedirs(d, exist_ok=True)

def load_env_file():
    """Load environment variables from a .env file in the workspace root if it exists."""
    env_path = ".env"
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.strip().strip("'\"")
                        os.environ[key] = val
        except Exception as e:
            pass

# Load environment variables on helper import
load_env_file()

def save_api_key_to_env(api_key: str) -> bool:
    """Save the Gemini API key to a .env file in the workspace root."""
    try:
        lines = []
        key_exists = False
        if os.path.exists(".env"):
            with open(".env", "r", encoding="utf-8") as f:
                lines = f.readlines()
        
        new_lines = []
        for line in lines:
            if line.strip().startswith("GEMINI_API_KEY") or line.strip().startswith("GOOGLE_API_KEY"):
                new_lines.append(f"GEMINI_API_KEY={api_key}\n")
                key_exists = True
            else:
                new_lines.append(line)
        
        if not key_exists:
            new_lines.append(f"GEMINI_API_KEY={api_key}\n")
            
        with open(".env", "w", encoding="utf-8") as f:
            f.writelines(new_lines)
            
        os.environ["GEMINI_API_KEY"] = api_key
        return True
    except Exception as e:
        return False

def verify_gemini_connectivity(api_key: str) -> bool:
    """Verify Gemini API connectivity by making a simple request."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Say hi")
        return bool(response.text.strip())
    except Exception as e:
        return False

