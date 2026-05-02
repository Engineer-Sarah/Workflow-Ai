import streamlit as st
from groq import Groq
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go # Fixed missing import
from datetime import datetime
import time

# 1. LUXURY PAGE CONFIG
st.set_page_config(page_title="WorkFlow AI ", page_icon="💎", layout="wide")

# 2. INITIALIZE SESSION STATES (Prevents Errors)
for key in ["tasks", "emails", "meetings", "reports"]:
    if key not in st.session_state:
        st.session_state[key] = []

# 3. PREMIUM CSS (Midnight Glassmorphism)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #050810; color: #f8fafc; }
.stApp { background: radial-gradient(circle at top right, #0f172a, #050810); }

/* Sidebar Styling */
[data-testid="stSidebar"] { background-color: rgba(15, 23, 42, 0.9) !important; border-right: 1px solid rgba(99, 102, 241, 0.2); backdrop-filter: blur(15px); }

/* Metric Cards */
.metric-card {
    background: rgba(30, 41, 59, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 1.2rem;
    text-align: center;
    transition: all 0.3s ease;
}
.metric-card:hover { border-color: #6366f1; transform: translateY(-3px); }
.metric-number { font-size: 2rem; font-weight: 800; color: #f1f5f9; }
.metric-label { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }

/* AI Output Box */
.ai-output {
    background: rgba(15, 23, 42, 0.6);
    border-left: 4px solid #6366f1;
    padding: 1.5rem;
    border-radius: 0 12px 12px 0;
    color: #cbd5e1;
    line-height: 1.6;
    margin: 1rem 0;
}

/* Custom Buttons */
.stButton > button {
    background: linear-gradient(90deg, #6366f1, #a855f7) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# 4. CORE LOGIC (Keeping your Groq command)
def get_client():
    key = st.secrets.get("GROQ_API_KEY") # This command remains unchanged
    return Groq(api_key=key) if key else None

client = get_client()

def ask_ai(prompt, system="You are WorkFlow AI, an elite executive assistant."):
    if not client: return "⚠️ Error: API Key not detected in Secrets."
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
    
    # Live Clock
    t = datetime.now().strftime("%I:%M:%S %p")
    st.markdown(f"<div style='text-align:center; color:#6366f1; font-weight:800; font-size:1.2rem;'>{t}</div>", unsafe_allow_html=True)
    
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
    if client:
        st.success("AI Engine Online")
    else:
        st.error("Engine Disconnected")

# 6. DASHBOARD
if current_page == "Dashboard":
    st.markdown(f"## Welcome back, {datetime.now().strftime('%A')}!")
    
    # Top Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown("<div class='metric-card'><div class='metric-number'>47</div><div class='metric-label'>Tasks Done</div></div>", unsafe_allow_html=True)
    c2.markdown("<div class='metric-card'><div class='metric-number'>12</div><div class='metric-label'>AI Drafts</div></div>", unsafe_allow_html=True)
    c3.markdown("<div class='metric-card'><div class='metric-number'>5</div><div class='metric-label'>Meetings</div></div>", unsafe_allow_html=True)
    c4.markdown("<div class='metric-card'><div class='metric-number'>98%</div><div class='metric-label'>Efficiency</div></div>", unsafe_allow_html=True)

    # Charts
    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([3, 2])
    with col_l:
        df = pd.DataFrame({"Dept": ["Sales", "HR", "Support", "Dev"], "Hours Saved": [10, 15, 20, 25]})
        fig = px.bar(df, x="Dept", y="Hours Saved", title="Productivity Gains (Hours)", template="plotly_dark")
        fig.update_traces(marker_color='#6366f1')
        st.plotly_chart(fig, use_container_width=True)
    with col_r:
        pie_df = pd.DataFrame({"Feature": ["Email", "Task", "Summary"], "Usage": [40, 30, 30]})
        fig2 = px.pie(pie_df, names="Feature", values="Usage", hole=0.4, title="Feature Usage", template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

# 7. AI EMAIL WRITER
elif current_page == "AI Email Writer":
    st.markdown("## ✉️ AI Email Writer")
    with st.container():
        recipient = st.text_input("Recipient")
        subject = st.text_input("Subject / Purpose")
        tone = st.selectbox("Tone", ["Professional", "Urgent", "Friendly"])
        points = st.text_area("Key Points")
        
        if st.button("Generate Email"):
            with st.spinner("Drafting..."):
                res = ask_ai(f"Subject: {subject}. Tone: {tone}. Points: {points}")
                st.markdown(f"<div class='ai-output'>{res}</div>", unsafe_allow_html=True)
                st.session_state.emails.append({"subject": subject, "content": res})

# (Other pages like Task Manager follow same logic...)
elif current_page == "Smart Task Manager":
    st.markdown("## ✅ Smart Task Manager")
    t_in = st.text_input("New Task")
    if st.button("Add"):
        st.session_state.tasks.append({"task": t_in, "done": False})
    
    for t in st.session_state.tasks:
        st.checkbox(t["task"], value=t["done"])

st.markdown("<br><br><p style='text-align:center; color:#475569;'>Built for HEC GenAI Hackathon</p>", unsafe_allow_html=True)
