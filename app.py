import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="WorkFlow AI", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); border-right: 1px solid #334155; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
.metric-card { background: linear-gradient(135deg, #1e293b, #0f172a); border: 1px solid #334155; border-radius: 16px; padding: 1.25rem 1.5rem; position: relative; overflow: hidden; margin-bottom: 0.5rem; }
.metric-card.purple::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #6366f1, #8b5cf6); }
.metric-number { font-size: 2.2rem; font-weight: 700; color: #f1f5f9; line-height: 1.1; }
.metric-label { font-size: 0.78rem; font-weight: 500; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 0.25rem; }
.ai-output { background: linear-gradient(135deg, #0f172a, #1e1b4b); border: 1px solid #4f46e5; border-radius: 12px; padding: 1.25rem; color: #e2e8f0; font-size: 0.92rem; line-height: 1.7; margin-top: 0.75rem; white-space: pre-wrap; }
.stButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 10px !important; padding: 0.55rem 1.4rem !important; font-weight: 600 !important; transition: all 0.2s !important; box-shadow: 0 4px 14px rgba(99,102,241,0.35) !important; }
.stApp { background: #0b1120; }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if "api_key_valid" not in st.session_state:
    st.session_state.update({
        "tasks": [], "emails": [], "meetings": [], "reports": [],
        "api_key_valid": False, "model": None, "last_api_key": ""
    })

# --- CORE UTILITY FUNCTIONS ---
def try_init_model(api_key):
    """Attempts to initialize the Gemini model with the provided key."""
    if not api_key: return None, None
    try:
        genai.configure(api_key=api_key)
        # We try 1.5 Flash as it is the most reliable for hackathons
        model = genai.GenerativeModel("gemini-1.5-flash")
        # Test connection
        model.generate_content("ping")
        return model, "gemini-1.5-flash"
    except Exception:
        return None, None

def get_api_key():
    """Retrieves the key from Streamlit Secrets or Environment."""
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.environ.get("GEMINI_API_KEY", "")

def ask_ai(prompt):
    """General function to handle AI generation calls."""
    if not st.session_state.api_key_valid or not st.session_state.model:
        return "⚠️ AI not connected. Please check your API key."
    try:
        response = st.session_state.model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"

# --- SIDEBAR & NAVIGATION ---
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 0.5rem;'>
        <div style='font-size:2rem;'>🚀</div>
        <div style='font-size:1.2rem; font-weight:700; color:#f1f5f9;'>WorkFlow AI</div>
        <div style='font-size:0.7rem; color:#64748b; letter-spacing:0.1em; text-transform:uppercase; margin-top:0.2rem;'>Premium Productivity Suite</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # AUTO-CONNECT ONLY (No manual input box for judges)
    if not st.session_state.api_key_valid:
        # Check secrets
        secret_key = get_api_key()
        if secret_key:
            model, name = try_init_model(secret_key)
            if model:
                st.session_state.model = model
                st.session_state.api_key_valid = True
                st.rerun()
        else:
            st.warning("⚙️ System: Waiting for API Secret...")

    if st.session_state.api_key_valid:
        st.markdown("""
        <div style='background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3);
        border-radius:10px; padding:0.6rem 1rem; color:#34d399; font-size:0.82rem; font-weight:600;'>
            ✅ AI System Active
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div style='font-size:0.75rem; color:#64748b; font-weight:600; text-transform:uppercase; margin-bottom:0.5rem;'>Navigation</div>", unsafe_allow_html=True)
    
    pages = {
        "📊  Dashboard": "Dashboard",
        "✉️  AI Email Writer": "AI Email Writer",
        "🎙️  Meeting Summarizer": "Meeting Summarizer",
        "✅  Smart Task Manager": "Smart Task Manager",
        "💬  Customer Reply": "Customer Reply",
        "📈  Weekly Report": "Weekly Report",
    }
    
    page_choice = st.radio("", list(pages.keys()), label_visibility="collapsed", key="main_nav")
    current_page = pages[page_choice]
    
    st.markdown("---")
    st.markdown("<div style='font-size:0.7rem; color:#475569; text-align:center;'>Powered by Google Gemini AI</div>", unsafe_allow_html=True)
# --- PAGE CONTENT ROUTING ---
if current_page == "Dashboard":
    st.markdown("<div style='font-size:1.7rem; font-weight:800; color:#f1f5f9;'>Main Dashboard</div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown("<div class='metric-card purple'><div class='metric-number'>47</div><div class='metric-label'>Tasks Completed</div></div>", unsafe_allow_html=True)
    # (Other columns would follow same pattern)

elif current_page == "AI Email Writer":
    st.markdown("<div style='font-size:1.6rem; font-weight:800; color:#f1f5f9;'>✉️ AI Email Writer</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: recipient = st.text_input("Recipient")
    with c2: subject = st.text_input("Subject")
    points = st.text_area("Key Points")
    if st.button("Generate Email"):
        with st.spinner("Writing..."):
            res = ask_ai(f"Write a professional email to {recipient} about {subject}. Points: {points}")
            st.markdown(f"<div class='ai-output'>{res}</div>", unsafe_allow_html=True)

elif current_page == "Meeting Summarizer":
    st.markdown("<div style='font-size:1.6rem; font-weight:800; color:#f1f5f9;'>🎙️ Meeting Summarizer</div>", unsafe_allow_html=True)
    notes = st.text_area("Paste Transcript", height=200)
    if st.button("Summarize"):
        with st.spinner("Analyzing..."):
            res = ask_ai(f"Summarize these meeting notes and provide action items: {notes}")
            st.markdown(f"<div class='ai-output'>{res}</div>", unsafe_allow_html=True)

elif current_page == "Smart Task Manager":
    st.markdown("<div style='font-size:1.6rem; font-weight:800; color:#f1f5f9;'>✅ Task Manager</div>", unsafe_allow_html=True)
    new_task = st.text_input("Add New Task")
    if st.button("Add"):
        st.session_state.tasks.append(new_task)
    for t in st.session_state.tasks:
        st.checkbox(t)

elif current_page == "Customer Reply":
    st.markdown("<div style='font-size:1.6rem; font-weight:800; color:#f1f5f9;'>💬 Customer Reply</div>", unsafe_allow_html=True)
    msg = st.text_area("Customer Message")
    if st.button("Generate Reply"):
        with st.spinner("Thinking..."):
            res = ask_ai(f"Draft a helpful support reply for: {msg}")
            st.markdown(f"<div class='ai-output'>{res}</div>", unsafe_allow_html=True)

elif current_page == "Weekly Report":
    st.markdown("<div style='font-size:1.6rem; font-weight:800; color:#f1f5f9;'>📈 Weekly Report</div>", unsafe_allow_html=True)
    done = st.text_area("What did you achieve?")
    if st.button("Create Report"):
        with st.spinner("Generating..."):
            res = ask_ai(f"Create a formal weekly status report based on these achievements: {done}")
            st.markdown(f"<div class='ai-output'>{res}</div>", unsafe_allow_html=True)
