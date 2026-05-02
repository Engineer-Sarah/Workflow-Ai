import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# 1. PAGE SETUP
st.set_page_config(page_title="WorkFlow AI", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

# 2. COMPLETE UI/UX STYLING
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0b1120; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); border-right: 1px solid #334155; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
.metric-card { background: linear-gradient(135deg, #1e293b, #0f172a); border: 1px solid #334155; border-radius: 16px; padding: 1.25rem 1.5rem; position: relative; overflow: hidden; margin-bottom: 0.5rem; transition: 0.3s; }
.metric-card:hover { transform: translateY(-3px); border-color: #4f46e5; }
.metric-card.purple::before { background: linear-gradient(90deg, #6366f1, #8b5cf6); content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; }
.metric-card.teal::before { background: #06b6d4; content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; }
.metric-card.green::before { background: #10b981; content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; }
.metric-card.amber::before { background: #f59e0b; content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; }
.metric-number { font-size: 2.2rem; font-weight: 700; color: #f1f5f9; line-height: 1.1; }
.metric-label { font-size: 0.78rem; font-weight: 500; color: #94a3b8; text-transform: uppercase; margin-top: 0.25rem; }
.section-header { font-size: 1.1rem; font-weight: 700; color: #f1f5f9; margin: 1.5rem 0 1rem; }
.ai-output { background: linear-gradient(135deg, #0f172a, #1e1b4b); border: 1px solid #4f46e5; border-radius: 12px; padding: 1.25rem; color: #e2e8f0; font-size: 0.92rem; line-height: 1.7; margin-top: 0.75rem; white-space: pre-wrap; }
.stButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 10px !important; padding: 0.5rem 1rem !important; font-weight: 600 !important; width: 100%; transition: 0.2s; }
.stButton > button:hover { opacity: 0.9; transform: scale(1.02); }
.task-pill { padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; }
.pill-high { background: rgba(244,63,94,0.2); color: #fb7185; }
.pill-medium { background: rgba(245,158,11,0.2); color: #fbbf24; }
.pill-low { background: rgba(16,185,129,0.2); color: #34d399; }
</style>
""", unsafe_allow_html=True)

# 3. SESSION STATE
state_defaults = {
    "tasks": [], "emails": [], "meetings": [], "reports": [], 
    "api_key_valid": False, "model": None
}
for key, val in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# 4. AI CORE ENGINE
def auto_connect():
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if api_key and not st.session_state.api_key_valid:
        try:
            genai.configure(api_key=api_key)
            st.session_state.model = genai.GenerativeModel("gemini-1.5-flash")
            st.session_state.api_key_valid = True
        except: pass
    return st.session_state.api_key_valid

is_ready = auto_connect()

def ask_ai(prompt, sys_msg="You are a professional productivity AI."):
    if not st.session_state.api_key_valid: return "⚠️ AI Disconnected."
    try:
        response = st.session_state.model.generate_content(f"{sys_msg}\n\nTask: {prompt}")
        return response.text
    except Exception as e: return f"Error: {str(e)}"

# 5. SIDEBAR
with st.sidebar:
    st.markdown("<div style='text-align:center;'><h1>🚀</h1><h2 style='color:white; margin-bottom:0;'>WorkFlow AI</h2></div>", unsafe_allow_html=True)
    st.markdown("---")
    if is_ready: st.success("✅ AI System Active")
    else: st.error("⚠️ AI Disconnected")
    
    current_page = st.radio("MAIN MENU", [
        "📊 Dashboard", "✉️ AI Email Writer", "🎙️ Meeting Summarizer", 
        "✅ Task Manager", "💬 Customer Reply", "📈 Weekly Report"
    ])
    st.markdown("---")
    st.caption("HEC GenAI Hackathon · Cohort 3")

# 6. PAGE LOGIC: DASHBOARD
if "Dashboard" in current_page:
    st.markdown(f"## Welcome Back")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown("<div class='metric-card purple'><div class='metric-number'>47</div><div class='metric-label'>Tasks Done</div></div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='metric-card teal'><div class='metric-number'>12</div><div class='metric-label'>AI Drafts</div></div>", unsafe_allow_html=True)
    with c3: st.markdown("<div class='metric-card green'><div class='metric-number'>5</div><div class='metric-label'>Meetings</div></div>", unsafe_allow_html=True)
    with c4: st.markdown("<div class='metric-card amber'><div class='metric-number'>3</div><div class='metric-label'>Reports</div></div>", unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2])
    with col_l:
        st.markdown("<div class='section-header'>📈 Productivity Trends</div>", unsafe_allow_html=True)
        df = pd.DataFrame({"Dept": ["Sales","HR","Support","Dev"], "Saved": [10,8,15,13]})
        fig = px.bar(df, x="Dept", y="Saved", color_discrete_sequence=["#6366f1"])
        fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#94a3b8")
        st.plotly_chart(fig, use_container_width=True)
    with col_r:
        st.markdown("<div class='section-header'>📂 Recent Activity</div>")
        st.code("Task: Design Logo (Completed)\nEmail: Client Follow-up (Drafted)\nReport: Q2 Planning (Pending)")

# 7. PAGE LOGIC: EMAIL WRITER
elif "Email" in current_page:
    st.markdown("## ✉️ AI Email Writer")
    c1, c2 = st.columns(2)
    with c1:
        recipient = st.text_input("Recipient")
        tone = st.selectbox("Tone", ["Professional", "Friendly", "Formal", "Urgent"])
    with c2:
        subject = st.text_input("Subject")
        key_points = st.text_area("Key Points")
    
    if st.button("✨ Draft Email"):
        with st.spinner("Writing..."):
            res = ask_ai(f"Write a {tone} email to {recipient} about {subject}. Points: {key_points}")
            st.markdown(f"<div class='ai-output'>{res}</div>", unsafe_allow_html=True)
            st.session_state.emails.append({"subj": subject, "body": res})

# 8. PAGE LOGIC: SUMMARIZER
elif "Summarizer" in current_page:
    st.markdown("## 🎙️ Meeting Summarizer")
    notes = st.text_area("Paste Transcript", height=250)
    if st.button("🚀 Generate Summary"):
        with st.spinner("Analyzing..."):
            res = ask_ai(f"Summarize these notes into Action Items and Decisions: {notes}")
            st.markdown(f"<div class='ai-output'>{res}</div>", unsafe_allow_html=True)
            st.session_state.meetings.append({"time": datetime.now(), "res": res})

# 9. PAGE LOGIC: TASK MANAGER
elif "Task" in current_page:
    st.markdown("## ✅ Smart Task Manager")
    tc1, tc2 = st.columns([3, 1])
    with tc1: t_name = st.text_input("New Task")
    with tc2: t_pri = st.selectbox("Priority", ["High", "Medium", "Low"])
    
    if st.button("Add Task"):
        st.session_state.tasks.append({"task": t_name, "priority": t_pri, "done": False})
        st.rerun()

    for i, t in enumerate(st.session_state.tasks):
        p_class = f"pill-{t['priority'].lower()}"
        col_a, col_b = st.columns([4, 1])
        col_a.markdown(f"**{t['task']}** <span class='task-pill {p_class}'>{t['priority']}</span>", unsafe_allow_html=True)
        if col_b.button("Done", key=f"btn_{i}"):
            st.session_state.tasks.pop(i)
            st.rerun()

# 10. PAGE LOGIC: CUSTOMER REPLY
elif "Reply" in current_page:
    st.markdown("## 💬 Customer Reply Assistant")
    msg = st.text_area("Customer Message")
    if st.button("Generate Response"):
        res = ask_ai(f"Draft a polite, helpful customer support response to: {msg}")
        st.markdown(f"<div class='ai-output'>{res}</div>", unsafe_allow_html=True)

# 11. PAGE LOGIC: WEEKLY REPORT
elif "Report" in current_page:
    st.markdown("## 📈 Weekly Report Generator")
    achievements = st.text_area("Key Achievements")
    blockers = st.text_area("Blockers")
    if st.button("Generate Report"):
        res = ask_ai(f"Write a professional weekly status report. Achievements: {achievements}. Blockers: {blockers}")
        st.markdown(f"<div class='ai-output'>{res}</div>", unsafe_allow_html=True)
        st.session_state.reports.append(res)

st.markdown("<br><hr><div style='text-align:center; color:#475569; font-size:0.8rem;'>WorkFlow AI © 2026</div>", unsafe_allow_html=True)
