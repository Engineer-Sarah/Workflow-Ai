import streamlit as st
from groq import Groq  # Updated for Groq
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# 1. PAGE SETUP
st.set_page_config(page_title="WorkFlow AI (Groq)", page_icon="⚡", layout="wide")

# 2. UI/UX STYLING (Same as before)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0b1120; color: #e2e8f0; }
.metric-card { background: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 1.5rem; text-align: center; }
.metric-number { font-size: 2rem; font-weight: 700; color: #6366f1; }
.ai-output { background: #0f172a; border-left: 4px solid #6366f1; border-radius: 8px; padding: 1.5rem; white-space: pre-wrap; margin-top: 10px; }
.stButton > button { background: linear-gradient(90deg, #6366f1, #8b5cf6) !important; color: white !important; border-radius: 8px !important; width: 100%; height: 3rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. SESSION STATE
if "tasks" not in st.session_state: st.session_state.tasks = []

# 4. GROQ AI ENGINE
def get_groq_client():
    # Looks for 'GROQ_API_KEY' in Streamlit Secrets
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

client = get_groq_client()

def ask_groq(prompt, system_msg="You are an elite productivity assistant."):
    if not client:
        return "❌ Missing GROQ_API_KEY in Streamlit Secrets."
    try:
        # Using Llama-3-70b via Groq for high-quality responses
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# 5. SIDEBAR NAVIGATION
with st.sidebar:
    st.title("🚀 WorkFlow AI")
    if client: st.success("⚡ Groq Engine Active")
    else: st.error("⚠️ Add GROQ_API_KEY to Secrets")
    
    page = st.radio("MENU", ["📊 Dashboard", "✉️ AI Email", "🎙️ Summarizer", "✅ Task Manager"])

# 6. DASHBOARD
if page == "📊 Dashboard":
    st.markdown("## Global Overview")
    c1, c2, c3 = st.columns(3)
    c1.markdown("<div class='metric-card'><div class='metric-number'>500+</div><div>Tokens/Sec</div></div>", unsafe_allow_html=True)
    c2.markdown("<div class='metric-card'><div class='metric-number'>12</div><div>Tasks Pending</div></div>", unsafe_allow_html=True)
    c3.markdown("<div class='metric-card'><div class='metric-number'>99%</div><div>AI Accuracy</div></div>", unsafe_allow_html=True)
    
    df = pd.DataFrame({"Day": ["Mon", "Tue", "Wed", "Thu", "Fri"], "Workload": [5, 8, 4, 10, 7]})
    fig = px.area(df, x="Day", y="Workload", title="Efficiency Trend")
    st.plotly_chart(fig, use_container_width=True)

# 7. AI EMAIL WRITER
elif page == "✉️ AI Email":
    st.markdown("## ✉️ Smart Email Writer")
    to = st.text_input("To (Client/Manager)")
    topic = st.text_input("Purpose")
    notes = st.text_area("Bullet points to include")
    
    if st.button("Generate Email"):
        with st.spinner("Groq is thinking..."):
            res = ask_groq(f"Draft a professional email to {to} about {topic}. Details: {notes}")
            st.markdown(f"<div class='ai-output'>{res}</div>", unsafe_allow_html=True)

# 8. MEETING SUMMARIZER
elif page == "🎙️ Summarizer":
    st.markdown("## 🎙️ Meeting Summarizer")
    transcript = st.text_area("Paste meeting transcript here...", height=300)
    
    if st.button("Summarize Now"):
        with st.spinner("Extracting action items..."):
            res = ask_groq(f"Summarize this into: 1. Decisions, 2. Action Items, 3. Next Steps. Transcript: {transcript}")
            st.markdown(f"<div class='ai-output'>{res}</div>", unsafe_allow_html=True)

# 9. TASK MANAGER
elif page == "✅ Task Manager":
    st.markdown("## ✅ Smart Tasks")
    new_task = st.text_input("What needs to be done?")
    if st.button("Add Task") and new_task:
        st.session_state.tasks.append(new_task)
    
    for i, t in enumerate(st.session_state.tasks):
        col_l, col_r = st.columns([4, 1])
        col_l.write(f"- {t}")
        if col_r.button("Done", key=f"t_{i}"):
            st.session_state.tasks.pop(i)
            st.rerun()
