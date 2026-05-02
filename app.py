import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WorkFlow AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Global CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid #334155;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
.metric-card {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
    margin-bottom: 0.5rem;
}
.metric-card:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(99,102,241,0.2); }
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 16px 16px 0 0;
}
.metric-card.purple::before { background: linear-gradient(90deg, #6366f1, #8b5cf6); }
.metric-card.teal::before   { background: linear-gradient(90deg, #06b6d4, #0891b2); }
.metric-card.green::before  { background: linear-gradient(90deg, #10b981, #059669); }
.metric-card.amber::before  { background: linear-gradient(90deg, #f59e0b, #d97706); }
.metric-number { font-size: 2.2rem; font-weight: 700; color: #f1f5f9; line-height: 1.1; }
.metric-label  { font-size: 0.78rem; font-weight: 500; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 0.25rem; }
.metric-delta  { font-size: 0.78rem; font-weight: 600; margin-top: 0.4rem; }
.delta-up   { color: #10b981; }
.delta-down { color: #f43f5e; }
.section-header { font-size: 1.2rem; font-weight: 700; color: #f1f5f9; margin-bottom: 1rem; }
.feature-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 0.75rem;
    transition: border-color 0.2s;
}
.feature-card:hover { border-color: #6366f1; }
.ai-output {
    background: linear-gradient(135deg, #0f172a, #1e1b4b);
    border: 1px solid #4f46e5;
    border-radius: 12px;
    padding: 1.25rem;
    color: #e2e8f0;
    font-size: 0.92rem;
    line-height: 1.7;
    margin-top: 0.75rem;
    white-space: pre-wrap;
}
.task-pill {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.7rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
}
.pill-high   { background: rgba(239,68,68,0.15);  color: #f87171; border: 1px solid rgba(239,68,68,0.3); }
.pill-medium { background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }
.pill-low    { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.3); }
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.55rem 1.4rem !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.5) !important;
}
.stTextInput input, .stTextArea textarea {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}
.stApp { background: #0b1120; }
hr { border-color: #1e293b !important; }
.stProgress > div > div { background: linear-gradient(90deg, #6366f1, #8b5cf6) !important; }
.stTabs [data-baseweb="tab"] { color: #94a3b8 !important; font-weight: 500 !important; }
.stTabs [aria-selected="true"] { color: #6366f1 !important; border-bottom-color: #6366f1 !important; }
</style>
""", unsafe_allow_html=True)

# ─── Session State ────────────────────────────────────────────────────────────
for k, v in {
    "tasks": [],
    "emails": [],
    "meetings": [],
    "reports": [],
    "api_key_valid": False,
    "model": None,
    "last_api_key": ""
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── AI Functions ─────────────────────────────────────────────────────────────
def try_init_model(api_key):
    genai.configure(api_key=api_key)
    for model_name in [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-2.5-flash-lite",
    ]:
        try:
            m = genai.GenerativeModel(model_name)
            m.generate_content("Hi")
            return m, model_name
        except Exception:
            continue
    return None, None

def ask_ai(prompt, system_hint=""):
    if not st.session_state.get("model"):
        return "⚠️ Please enter a valid Gemini API key in the sidebar first."
    try:
        full = f"{system_hint}\n\n{prompt}" if system_hint else prompt
        response = st.session_state.model.generate_content(full)
        return response.text
    except Exception as e:
        err = str(e)
        if "API_KEY_INVALID" in err or "api key" in err.lower():
            return "❌ Invalid API key. Please check your Gemini API key."
        elif "quota" in err.lower():
            return "⚠️ API quota exceeded. Please wait or upgrade your plan."
        else:
            return f"⚠️ Error: {err[:300]}"

# ─── Auto-load API key ────────────────────────────────────────────────────────
if not st.session_state.get("model"):
    env_key = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else os.environ.get("GEMINI_API_KEY", "")
    if env_key and len(env_key) > 10:
        model, model_name = try_init_model(env_key)
        if model:
            st.session_state.model = model
            st.session_state.api_key_valid = True
            st.session_state.last_api_key = env_key


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 0.5rem;'>
        <div style='font-size:2rem;'>🚀</div>
        <div style='font-size:1.2rem; font-weight:700; color:#f1f5f9;'>WorkFlow AI</div>
        <div style='font-size:0.7rem; color:#64748b; letter-spacing:0.1em; text-transform:uppercase; margin-top:0.2rem;'>
            Premium Productivity Suite
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── API Key: hidden if already connected via secrets ──
    if not st.session_state.api_key_valid:
        st.markdown("<div style='font-size:0.75rem; color:#64748b; font-weight:600; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:0.3rem;'>Gemini API Key</div>", unsafe_allow_html=True)
        api_key = st.text_input("", type="password", placeholder="AIza...", label_visibility="collapsed", key="api_key_input")
        if api_key:
            if api_key != st.session_state.get("last_api_key", ""):
                with st.spinner("Connecting to Gemini..."):
                    model, model_name = try_init_model(api_key)
                if model:
                    st.session_state.model = model
                    st.session_state.api_key_valid = True
                    st.session_state.last_api_key = api_key
                    st.success(f"✅ Connected · {model_name}")
                else:
                    st.session_state.api_key_valid = False
                    st.error("❌ Could not connect. Check your key.")
    else:
        st.markdown("""
        <div style='background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3);
        border-radius:10px; padding:0.6rem 1rem; color:#34d399; font-size:0.82rem; font-weight:600;'>
            ✅ AI Connected & Ready
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div style='font-size:0.75rem; color:#64748b; font-weight:600; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:0.5rem;'>Navigation</div>", unsafe_allow_html=True)

    pages = {
        "📊  Dashboard":           "Dashboard",
        "✉️  AI Email Writer":      "AI Email Writer",
        "🎙️  Meeting Summarizer":   "Meeting Summarizer",
        "✅  Smart Task Manager":   "Smart Task Manager",
        "💬  Customer Reply":       "Customer Reply Assistant",
        "📈  Weekly Report":        "Weekly Report Generator",
    }
    page = st.radio("", list(pages.keys()), label_visibility="collapsed")
    current_page = pages[page]

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.7rem; color:#475569; text-align:center; line-height:1.6;'>
        Powered by Google Gemini AI<br>
        <span style='color:#334155;'>HEC GenAI Hackathon · Cohort 3</span>
    </div>
    """, unsafe_allow_html=True)

# ─── PAGE: Dashboard ──────────────────────────────────────────────────────────
if current_page == "Dashboard":
    hour = datetime.now().hour
    greet = "Morning 🌅" if hour < 12 else ("Afternoon ☀️" if hour < 17 else "Evening 🌙")
    st.markdown(f"""
    <div style='margin-bottom:1.5rem;'>
        <div style='font-size:1.7rem; font-weight:800; color:#f1f5f9;'>Good {greet}</div>
        <div style='color:#64748b; font-size:0.9rem; margin-top:0.2rem;'>
            {datetime.now().strftime("%A, %B %d, %Y")} — Your AI workspace is ready.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    for col, color, num, label, delta, up in [
        (c1, "purple", "47", "Tasks Completed",    "↑ 12% this week", True),
        (c2, "teal",   "8",  "Emails Drafted",     "↑ 3 today",       True),
        (c3, "green",  "5",  "Meetings Logged",    "↓ 1 from last wk",False),
        (c4, "amber",  "3",  "Reports Ready",      "↑ 2 new",         True),
    ]:
        with col:
            st.markdown(f"""
            <div class='metric-card {color}'>
                <div class='metric-number'>{num}</div>
                <div class='metric-label'>{label}</div>
                <div class='metric-delta {"delta-up" if up else "delta-down"}'>{delta}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown("<div class='section-header'>📈 Weekly Productivity Gains</div>", unsafe_allow_html=True)
        df = pd.DataFrame({
            "Department":      ["Sales", "HR", "Support", "Admin", "Marketing", "Engineering"],
            "Hours Saved":     [10, 8, 15, 6, 11, 13],
            "Tasks Automated": [22, 15, 30, 10, 20, 28],
        })
        fig = go.Figure()
        fig.add_bar(x=df["Department"], y=df["Hours Saved"],     name="Hours Saved",     marker_color="#6366f1")
        fig.add_bar(x=df["Department"], y=df["Tasks Automated"], name="Tasks Automated", marker_color="#06b6d4")
        fig.update_layout(
            barmode="group", height=280,
            plot_bgcolor="#0f172a", paper_bgcolor="#1e293b",
            font=dict(color="#94a3b8", size=12, family="Inter"),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(gridcolor="#334155"),
            yaxis=dict(gridcolor="#334155"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown("<div class='section-header'>🔥 Feature Usage</div>", unsafe_allow_html=True)
        pie_df = pd.DataFrame({
            "Feature": ["Email Writer", "Task Manager", "Summarizer", "Reports", "Customer Reply"],
            "Usage":   [32, 27, 20, 12, 9],
        })
        fig2 = px.pie(
            pie_df, names="Feature", values="Usage", hole=0.45,
            color_discrete_sequence=["#6366f1","#06b6d4","#10b981","#f59e0b","#f43f5e"]
        )
        fig2.update_layout(
            height=280,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="#1e293b",
            font=dict(color="#94a3b8", family="Inter"),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        fig2.update_traces(textfont_color="white")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-header'>⚡ Quick Access</div>", unsafe_allow_html=True)
    qa1, qa2, qa3, qa4 = st.columns(4)
    for col, icon, title, desc in [
        (qa1, "✉️", "Draft Email",        "AI-powered in seconds"),
        (qa2, "✅", "Add Task",            "Smart prioritization"),
        (qa3, "🎙️", "Summarize Meeting",  "Notes → Action items"),
        (qa4, "📈", "Generate Report",    "Weekly executive summary"),
    ]:
        with col:
            st.markdown(f"""
            <div class='feature-card'>
                <div style='font-size:1.4rem;'>{icon}</div>
                <div style='font-weight:600; color:#f1f5f9; margin-top:0.3rem;'>{title}</div>
                <div style='color:#64748b; font-size:0.8rem;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

# ─── PAGE: AI Email Writer ─────────────────────────────────────────────────────
elif current_page == "AI Email Writer":
    st.markdown("<div style='font-size:1.6rem; font-weight:800; color:#f1f5f9; margin-bottom:1.5rem;'>✉️ AI Email Writer</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div style='color:#94a3b8; font-size:0.82rem; font-weight:600; margin-bottom:0.3rem;'>RECIPIENT</div>", unsafe_allow_html=True)
        recipient = st.text_input("", placeholder="e.g. Client, Manager, Team...", key="em_to", label_visibility="collapsed")
        st.markdown("<div style='color:#94a3b8; font-size:0.82rem; font-weight:600; margin:0.8rem 0 0.3rem;'>EMAIL TONE</div>", unsafe_allow_html=True)
        tone = st.selectbox("", ["Professional", "Friendly", "Formal", "Urgent", "Apologetic", "Persuasive"], label_visibility="collapsed")
    with c2:
        st.markdown("<div style='color:#94a3b8; font-size:0.82rem; font-weight:600; margin-bottom:0.3rem;'>SUBJECT / PURPOSE</div>", unsafe_allow_html=True)
        subject = st.text_input("", placeholder="e.g. Project update, Meeting request...", key="em_subj", label_visibility="collapsed")
        st.markdown("<div style='color:#94a3b8; font-size:0.82rem; font-weight:600; margin:0.8rem 0 0.3rem;'>KEY POINTS</div>", unsafe_allow_html=True)
        key_points = st.text_area("", placeholder="Bullet points to include...", height=96, key="em_pts", label_visibility="collapsed")

    if st.button("✨ Generate Email"):
        if not subject:
            st.warning("Please enter a subject/purpose.")
        else:
            with st.spinner("Writing your email..."):
                result = ask_ai(
                    f"""Write a {tone.lower()} professional email.
To: {recipient or 'the recipient'}
Subject: {subject}
Key points: {key_points or 'None'}
Format: Subject line, then full email with greeting, body, and sign-off."""
                )
            st.markdown(f"<div class='ai-output'>{result}</div>", unsafe_allow_html=True)
            st.session_state.emails.append({
                "subject": subject,
                "tone": tone,
                "time": datetime.now().strftime("%H:%M"),
                "content": result
            })

    if st.session_state.emails:
        st.markdown("<br><div class='section-header'>📁 Email History</div>", unsafe_allow_html=True)
        for email in reversed(st.session_state.emails[-5:]):
            with st.expander(f"📧 {email['subject']} · {email['tone']} · {email['time']}"):
                st.markdown(f"<div class='ai-output'>{email['content']}</div>", unsafe_allow_html=True)

# ─── PAGE: Meeting Summarizer ─────────────────────────────────────────────────
elif current_page == "Meeting Summarizer":
    st.markdown("<div style='font-size:1.6rem; font-weight:800; color:#f1f5f9; margin-bottom:1.5rem;'>🎙️ Meeting Summarizer</div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📝 New Summary", "📋 History"])

    with tab1:
        st.markdown("<div style='color:#94a3b8; font-size:0.82rem; font-weight:600; margin-bottom:0.3rem;'>MEETING NOTES / TRANSCRIPT</div>", unsafe_allow_html=True)
        notes = st.text_area("", placeholder="Paste meeting transcript or notes here...", height=200, label_visibility="collapsed")
        c1, c2 = st.columns(2)
        with c1:
            output_fmt = st.selectbox("Output Format", ["Full Summary + Action Items", "Action Items Only", "Executive Brief"])
        with c2:
            lang = st.selectbox("Language", ["English", "Urdu", "English + Urdu"])

        if st.button("🚀 Summarize Meeting"):
            if not notes.strip():
                st.warning("Please paste meeting notes.")
            else:
                with st.spinner("Analyzing meeting..."):
                    result = ask_ai(
                        f"""Analyze this meeting and provide:
1. Executive Summary
2. Key Discussion Points
3. Action Items (with owners if mentioned)
4. Decisions Made
5. Next Steps

Format: {output_fmt}. Language: {lang}.
Meeting notes:
{notes}"""
                    )
                st.markdown(f"<div class='ai-output'>{result}</div>", unsafe_allow_html=True)
                st.session_state.meetings.append({
                    "preview": notes[:60] + "...",
                    "summary": result,
                    "time": datetime.now().strftime("%b %d, %H:%M")
                })

    with tab2:
        if not st.session_state.meetings:
            st.markdown("<div style='color:#475569; text-align:center; padding:2rem;'>No summaries yet.</div>", unsafe_allow_html=True)
        for mtg in reversed(st.session_state.meetings):
            with st.expander(f"🎙️ {mtg['preview']} · {mtg['time']}"):
                st.markdown(f"<div class='ai-output'>{mtg['summary']}</div>", unsafe_allow_html=True)

# ─── PAGE: Smart Task Manager ─────────────────────────────────────────────────
elif current_page == "Smart Task Manager":
    st.markdown("<div style='font-size:1.6rem; font-weight:800; color:#f1f5f9; margin-bottom:1.5rem;'>✅ Smart Task Manager</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        task_input = st.text_input("", placeholder="Enter a task...", key="task_inp", label_visibility="collapsed")
    with c2:
        priority = st.selectbox("", ["High", "Medium", "Low"], label_visibility="collapsed", key="task_pri")
    with c3:
        category = st.selectbox("", ["Work", "Personal", "Urgent", "Learning"], label_visibility="collapsed", key="task_cat")

    ca, cb, _ = st.columns([1, 1.5, 3])
    with ca:
        if st.button("➕ Add Task"):
            if task_input:
                st.session_state.tasks.append({
                    "task": task_input,
                    "priority": priority,
                    "category": category,
                    "done": False,
                    "added": datetime.now().strftime("%H:%M"),
                    "ai_suggestion": ""
                })
                st.rerun()
    with cb:
        if st.button("🧠 AI Prioritize All"):
            if st.session_state.tasks:
                tlist = "\n".join([f"- {t['task']} ({t['priority']})" for t in st.session_state.tasks])
                with st.spinner("AI analyzing..."):
                    result = ask_ai(
                        f"Reorder by urgency + impact, add a 1-line tip for each:\n{tlist}",
                        "You are a productivity expert."
                    )
                st.markdown(f"<div class='ai-output'>{result}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not st.session_state.tasks:
        st.markdown("<div style='color:#475569; text-align:center; padding:2.5rem; border:1px dashed #1e293b; border-radius:12px;'>No tasks yet. Add your first task above! 🎯</div>", unsafe_allow_html=True)
    else:
        total      = len(st.session_state.tasks)
        done_count = sum(1 for t in st.session_state.tasks if t["done"])
        high_count = sum(1 for t in st.session_state.tasks if t["priority"] == "High" and not t["done"])

        s1, s2, s3, s4 = st.columns(4)
        s1.markdown(f"<div class='metric-card purple'><div class='metric-number'>{total}</div><div class='metric-label'>Total</div></div>", unsafe_allow_html=True)
        s2.markdown(f"<div class='metric-card green'><div class='metric-number'>{done_count}</div><div class='metric-label'>Done</div></div>", unsafe_allow_html=True)
        s3.markdown(f"<div class='metric-card amber'><div class='metric-number'>{total - done_count}</div><div class='metric-label'>Remaining</div></div>", unsafe_allow_html=True)
        s4.markdown(f"<div class='metric-card teal'><div class='metric-number'>{high_count}</div><div class='metric-label'>High Priority</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if total > 0:
            st.progress(done_count / total, text=f"Progress: {done_count}/{total} ({int(done_count / total * 100)}%)")
        st.markdown("<br>", unsafe_allow_html=True)

        for i, task in enumerate(st.session_state.tasks):
            pri_cls = {"High": "pill-high", "Medium": "pill-medium", "Low": "pill-low"}.get(task["priority"], "pill-low")
            col_chk, col_task, col_tip, col_del = st.columns([0.4, 4, 0.8, 0.5])
            with col_chk:
                chk = st.checkbox("", value=task["done"], key=f"chk_{i}", label_visibility="collapsed")
                if chk != task["done"]:
                    st.session_state.tasks[i]["done"] = chk
                    st.rerun()
            with col_task:
                style = "text-decoration:line-through; color:#475569;" if task["done"] else "color:#e2e8f0;"
                st.markdown(f"""
                <div style='padding:0.5rem 0;'>
                    <span style='{style} font-weight:500;'>{task['task']}</span>
                    <span class='task-pill {pri_cls}' style='margin-left:0.5rem;'>{task['priority']}</span>
                    <span style='color:#475569; font-size:0.76rem; margin-left:0.5rem;'>{task['category']} · {task['added']}</span>
                </div>
                """, unsafe_allow_html=True)
            with col_tip:
                if st.button("💡", key=f"tip_{i}"):
                    with st.spinner("..."):
                        tip = ask_ai(f"Give a 1-sentence smart tip to complete this task efficiently: '{task['task']}'")
                    st.session_state.tasks[i]["ai_suggestion"] = tip
                    st.rerun()
            with col_del:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.tasks.pop(i)
                    st.rerun()

            if task.get("ai_suggestion"):
                st.markdown(f"""
                <div style='margin:0.1rem 0 0.5rem 2rem; padding:0.4rem 0.7rem;
                background:#0f172a; border-left:3px solid #6366f1;
                border-radius:0 8px 8px 0; color:#a5b4fc; font-size:0.82rem;'>
                    💡 {task['ai_suggestion']}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<hr style='margin:0.3rem 0; border-color:#1e293b;'>", unsafe_allow_html=True)

# ─── PAGE: Customer Reply Assistant ──────────────────────────────────────────
elif current_page == "Customer Reply Assistant":
    st.markdown("<div style='font-size:1.6rem; font-weight:800; color:#f1f5f9; margin-bottom:1.5rem;'>💬 Customer Reply Assistant</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([3, 1])
    with c2:
        sentiment  = st.selectbox("Customer Mood", ["Angry / Frustrated", "Confused", "Happy", "Neutral", "Urgent"])
        reply_tone = st.selectbox("Reply Style",   ["Empathetic & Professional", "Friendly & Casual", "Formal", "Brief & Direct"])
        industry   = st.selectbox("Industry",      ["E-commerce", "SaaS/Tech", "Healthcare", "Education", "Finance", "General"])
    with c1:
        st.markdown("<div style='color:#94a3b8; font-size:0.82rem; font-weight:600; margin-bottom:0.3rem;'>CUSTOMER MESSAGE</div>", unsafe_allow_html=True)
        customer_msg = st.text_area("", placeholder="Paste the customer message here...", height=160, label_visibility="collapsed")
        context = st.text_input("Company / Product Context (optional)", placeholder="e.g. Online clothing store, 7-day return policy...")

    if st.button("🚀 Generate Reply"):
        if not customer_msg.strip():
            st.warning("Please enter the customer message.")
        else:
            with st.spinner("Crafting reply..."):
                result = ask_ai(
                    f"""Customer support specialist for {industry} business.
Customer mood: {sentiment}. Reply style: {reply_tone}.
Context: {context or 'Not specified'}
Customer message: "{customer_msg}"
Write a professional, empathetic reply that acknowledges concern, provides solution, ends positively."""
                )
            st.markdown(f"<div class='ai-output'>{result}</div>", unsafe_allow_html=True)

            with st.spinner("Analyzing sentiment..."):
                analysis = ask_ai(f"2 bullet points: (1) Sentiment and (2) Key concern: \"{customer_msg}\"")
            st.markdown("<div class='section-header' style='font-size:1rem; margin-top:1rem;'>🔍 Message Analysis</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='ai-output' style='font-size:0.85rem;'>{analysis}</div>", unsafe_allow_html=True)

# ─── PAGE: Weekly Report Generator ───────────────────────────────────────────
elif current_page == "Weekly Report Generator":
    st.markdown("<div style='font-size:1.6rem; font-weight:800; color:#f1f5f9; margin-bottom:1.5rem;'>📈 Weekly Report Generator</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        team_name      = st.text_input("Team / Department", placeholder="e.g. Engineering Team...")
        week           = st.text_input("Week Period",        placeholder="e.g. April 21–27, 2026")
        accomplishments = st.text_area("✅ Accomplishments This Week", placeholder="What was completed?", height=120)
    with c2:
        blockers   = st.text_area("🚧 Blockers / Challenges", placeholder="What slowed the team?",  height=100)
        next_week  = st.text_area("🎯 Next Week Priorities",  placeholder="What's coming up?",       height=100)
        kpis       = st.text_input("Key Metrics / KPIs",      placeholder="e.g. 120 tickets closed, 95% uptime...")

    if st.button("📊 Generate Report"):
        with st.spinner("Generating professional report..."):
            result = ask_ai(
                f"""Generate a professional weekly status report:
Team: {team_name or 'Team'} | Period: {week or 'This week'}
Accomplishments: {accomplishments}
Blockers: {blockers}
Next Week: {next_week}
KPIs: {kpis}

Format with sections: Executive Summary, Achievements, Challenges, KPI Summary, Next Week Priorities, Overall Status (Green/Yellow/Red)."""
            )
        st.markdown(f"<div class='ai-output'>{result}</div>", unsafe_allow_html=True)
        st.session_state.reports.append({
            "team":    team_name or "Team",
            "week":    week or "This week",
            "content": result,
            "time":    datetime.now().strftime("%b %d")
        })
        st.success("✅ Report saved!")

    if st.session_state.reports:
        st.markdown("<br><div class='section-header'>📁 Report History</div>", unsafe_allow_html=True)
        for r in reversed(st.session_state.reports[-5:]):
            with st.expander(f"📈 {r['team']} · {r['week']} · {r['time']}"):
                st.markdown(f"<div class='ai-output'>{r['content']}</div>", unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center; color:#1e293b; font-size:0.72rem;'>
    WorkFlow AI · Built with Streamlit + Google Gemini · HEC GenAI Hackathon Cohort 3
</div>
""", unsafe_allow_html=True)
