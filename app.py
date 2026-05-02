import streamlit as st
from groq import Groq
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. LUXURY PAGE CONFIG
st.set_page_config(page_title="WorkFlow AI Pro", page_icon="💎", layout="wide")

# 2. INITIALIZE SESSION STATES
# This is crucial to prevent the "KeyError" and blank screens
for key in ["tasks", "emails", "meetings", "reports"]:
    if key not in st.session_state:
        st.session_state[key] = []

# 3. PREMIUM CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #050810; color: #f8fafc; }
.stApp { background: radial-gradient(circle at top right, #0f172a, #050810); }
[data-testid="stSidebar"] { background-color: rgba(15, 23, 42, 0.9) !important; border-right: 1px solid rgba(99, 102, 241, 0.2); backdrop-filter: blur(15px); }
.metric-card { background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 16px; padding: 1.2rem; text-align: center; }
.ai-output { background: rgba(15, 23, 42, 0.6); border-left: 4px solid #6366f1; padding: 1.5rem; border-radius: 0 12px 12px 0; color: #cbd5e1; line-height: 1.6; margin: 1rem 0; }
.stButton > button { background: linear-gradient(90deg, #6366f1, #a855f7) !important; color: white !important; border: none !important; border-radius: 10px !important; width: 100%; }
</style>
""", unsafe_allow_html=True)

# 4. CORE LOGIC (Groq Key Unchanged)
def get_client():
    key = st.secrets.get("GROQ_API_KEY")
    return Groq(api_key=key) if key else None

client = get_client()

def ask_ai(prompt, system="You are WorkFlow Pro, an elite executive assistant."):
    if not client: return "⚠️ Error: API Key not detected."
    try:
        chat = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":system}, {"role":"user","content":prompt}]
        )
        return chat.choices[0].message.content
    except Exception as e: return f"System Error: {str(e)}"

# 5. SIDEBAR NAVIGATION
with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:white;'>💎 WorkFlow AI</h1>", unsafe_allow_html=True)
    t = datetime.now().strftime("%I:%M:%S %p")
    st.markdown(f"<div style='text-align:center; color:#6366f1; font-weight:800; font-size:1.2rem; margin-bottom:20px;'>{t}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    pages = {
        "📊 Dashboard": "Dashboard",
        "✉️ AI Email Writer": "AI Email Writer",
        "🎙️ Meeting Summarizer": "Meeting Summarizer",
        "✅ Smart Task Manager": "Smart Task Manager",
        "💬 Customer Reply": "Customer Reply Assistant",
        "📈 Weekly Report": "Weekly Report Generator",
    }
    page_selection = st.radio("MAIN MENU", list(pages.keys()))
    current_page = pages[page_selection]
    
    st.markdown("---")
    st.info("AI Engine Online" if client else "Engine Disconnected")
    st.caption("Built for HEC GenAI Hackathon")

# 6. PAGE ROUTING
# Dashboard
if current_page == "Dashboard":
    st.title("📊 Executive Dashboard")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown("<div class='metric-card'><h3>47</h3><p>Tasks Done</p></div>", unsafe_allow_html=True)
    c2.markdown("<div class='metric-card'><h3>12</h3><p>Emails Sent</p></div>", unsafe_allow_html=True)
    c3.markdown("<div class='metric-card'><h3>5</h3><p>Reports</p></div>", unsafe_allow_html=True)
    c4.markdown("<div class='metric-card'><h3>98%</h3><p>Efficiency</p></div>", unsafe_allow_html=True)
    
    df = pd.DataFrame({"Dept": ["Sales", "HR", "Support", "Dev"], "Gains": [10, 15, 20, 25]})
    st.plotly_chart(px.bar(df, x="Dept", y="Gains", template="plotly_dark", color_discrete_sequence=['#6366f1']), use_container_width=True)

# Email Writer
elif current_page == "AI Email Writer":
    st.title("✉️ AI Email Writer")
    rec = st.text_input("To:")
    sub = st.text_input("Subject:")
    pts = st.text_area("Bullet Points:")
    if st.button("Generate Email"):
        with st.spinner("Writing..."):
            res = ask_ai(f"Write a professional email to {rec} about {sub}. Points: {pts}")
            st.markdown(f"<div class='ai-output'>{res}</div>", unsafe_allow_html=True)

# Meeting Summarizer
elif current_page == "Meeting Summarizer":
    st.title("🎙️ Meeting Summarizer")
    notes = st.text_area("Paste Transcript / Notes:", height=250)
    if st.button("Summarize"):
        with st.spinner("Analyzing..."):
            res = ask_ai(f"Summarize these notes into bullet points and action items: {notes}")
            st.markdown(f"<div class='ai-output'>{res}</div>", unsafe_allow_html=True)

# Task Manager
elif current_page == "Smart Task Manager":
    st.title("✅ Smart Task Manager")
    t_in = st.text_input("Add a new task:")
    if st.button("Add Task"):
        st.session_state.tasks.append({"task": t_in, "done": False})
    for i, t in enumerate(st.session_state.tasks):
        st.checkbox(t["task"], key=f"t_{i}")

# Customer Reply
elif current_page == "Customer Reply Assistant":
    st.title("💬 Customer Reply Assistant")
    msg = st.text_area("Customer Message:")
    mood = st.select_slider("Tone Strategy", options=["Empathetic", "Professional", "Casual"])
    if st.button("Draft Reply"):
        with st.spinner("Crafting..."):
            res = ask_ai(f"Draft a {mood} customer service reply to: {msg}")
            st.markdown(f"<div class='ai-output'>{res}</div>", unsafe_allow_html=True)

# Weekly Report
elif current_page == "Weekly Report Generator":
    st.title("📈 Weekly Report Generator")
    col1, col2 = st.columns(2)
    with col1:
        wins = st.text_area("Weekly Accomplishments:")
    with col2:
        blocks = st.text_area("Blockers / Challenges:")
    if st.button("Generate Report"):
        with st.spinner("Compiling..."):
            res = ask_ai(f"Create a professional weekly report. Wins: {wins}. Blockers: {blocks}")
            st.markdown(f"<div class='ai-output'>{res}</div>", unsafe_allow_html=True)
    
    for t in st.session_state.tasks:
        st.checkbox(t["task"], value=t["done"])

st.markdown("<br><br><p style='text-align:center; color:#475569;'>Built for HEC GenAI Hackathon</p>", unsafe_allow_html=True)
