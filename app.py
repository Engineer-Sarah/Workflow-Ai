import streamlit as st
from groq import Groq
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. LUXURY PAGE CONFIG
st.set_page_config(page_title="WorkFlow AI Pro", page_icon="💎", layout="wide")

# 2. PREMIUM CSS (Glassmorphism & Midnight Aesthetics)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

/* Global Reset */
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #050810; color: #f8fafc; }
.stApp { background: radial-gradient(circle at top right, #0f172a, #050810); }

/* Custom Sidebar */
[data-testid="stSidebar"] { background-color: rgba(15, 23, 42, 0.8) !important; border-right: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px); }

/* Premium Cards */
.glass-card {
    background: rgba(30, 41, 59, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 1.5rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    margin-bottom: 1rem;
}

.metric-val { font-size: 2.5rem; font-weight: 800; background: linear-gradient(90deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.metric-lbl { color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; font-size: 0.7rem; }

/* AI Output Styling */
.ai-box {
    background: linear-gradient(145deg, #0f172a, #1e293b);
    border: 1px solid #334155;
    border-left: 5px solid #6366f1;
    border-radius: 12px;
    padding: 1.5rem;
    color: #cbd5e1;
    line-height: 1.8;
}

/* Luxury Button */
.stButton > button {
    background: linear-gradient(90deg, #6366f1, #a855f7) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    padding: 0.75rem 2rem !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6) !important; }

/* Navigation Radio Styling */
div[data-testid="stSidebarNav"] { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# 3. CORE LOGIC
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

# 4. SIDEBAR
with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:white;'>💎 WorkFlow Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#64748b; font-size:0.8rem;'>PREMIUM PRODUCTIVITY SUITE</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    if client:
        st.markdown("<div style='background:rgba(16,185,129,0.1); color:#10b981; padding:10px; border-radius:10px; text-align:center; border:1px solid #10b981;'>● AI ENGINE ONLINE</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background:rgba(244,63,94,0.1); color:#f43f5e; padding:10px; border-radius:10px; text-align:center; border:1px solid #f43f5e;'>○ ENGINE DISCONNECTED</div>", unsafe_allow_html=True)

    page = st.radio("NAVIGATION", ["Dashboard", "AI Email Studio", "Meeting Intelligence", "Task Master"])

# 5. DASHBOARD
if page == "Dashboard":
    st.markdown("## 📊 Strategic Overview")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("<div class='glass-card'><div class='metric-lbl'>Efficiency Score</div><div class='metric-val'>98.2%</div></div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='glass-card'><div class='metric-lbl'>Hours Reclaimed</div><div class='metric-val'>14.5</div></div>", unsafe_allow_html=True)
    with c3: st.markdown("<div class='glass-card'><div class='metric-lbl'>AI Latency</div><div class='metric-val'>0.2s</div></div>", unsafe_allow_html=True)

    df = pd.DataFrame({"Metric": ["Emails", "Tasks", "Meetings", "Reports"], "Count": [45, 32, 12, 8]})
    fig = px.bar(df, x="Metric", y="Count", color="Count", color_continuous_scale="Blues", template="plotly_dark")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

# 6. EMAIL STUDIO
elif page == "AI Email Studio":
    st.markdown("## ✉️ AI Email Studio")
    with st.container():
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            dest = st.text_input("Recipient Profile", placeholder="e.g. Senior VP of Engineering")
        with col2:
            tone = st.selectbox("Intelligence Tone", ["Executive Formal", "Persuasive", "Diplomatic", "Direct"])
        
        goal = st.text_area("Strategic Objective", placeholder="What must this email achieve?")
        
        if st.button("Generate Executive Draft"):
            with st.spinner("Analyzing intent..."):
                res = ask_ai(f"Draft a {tone} email to {dest}. Objective: {goal}")
                st.markdown(f"<div class='ai-box'>{res}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# 7. MEETING INTELLIGENCE
elif page == "Meeting Intelligence":
    st.markdown("## 🎙️ Meeting Intelligence")
    raw_text = st.text_area("Input Transcript", height=250, placeholder="Paste your raw meeting notes or transcript here...")
    if st.button("Synthesize Action Plan"):
        with st.spinner("Processing dialogue..."):
            res = ask_ai(f"Extract key decisions and a bulleted action plan from: {raw_text}")
            st.markdown(f"<div class='ai-box'>{res}</div>", unsafe_allow_html=True)

# 8. TASK MASTER
elif page == "Task Master":
    st.markdown("## ✅ Task Master")
    if "pro_tasks" not in st.session_state: st.session_state.pro_tasks = []
    
    t_input = st.text_input("Define New Objective")
    if st.button("Inject Task") and t_input:
        st.session_state.pro_tasks.append(t_input)
        st.rerun()
    
    for i, t in enumerate(st.session_state.pro_tasks):
        st.markdown(f"<div style='background:rgba(255,255,255,0.03); padding:15px; border-radius:10px; margin-bottom:5px; border:1px solid rgba(255,255,255,0.05);'>⚡ {t}</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption("WorkFlow Pro v2.0 | High-Performance AI Backend")
