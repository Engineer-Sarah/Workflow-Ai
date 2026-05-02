import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="WorkFlow AI", page_icon="🚀", layout="wide")

# ------------------ SESSION STATE INIT ------------------
default_state = {
    "tasks": [],
    "emails": [],
    "meetings": [],
    "reports": [],
    "api_key_valid": False,
    "model": None,
    "last_api_key": ""
}
for k, v in default_state.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ------------------ GET API KEY ------------------
def get_api_key():
    try:
        return st.secrets.get("GEMINI_API_KEY", "")
    except:
        return ""

# ------------------ INIT MODEL ------------------
def try_init_model(api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        model.generate_content("Hello")
        return model
    except Exception as e:
        return None

# ------------------ LOAD API KEY ------------------
if not st.session_state.model:
    key = get_api_key()

    # DEBUG (REMOVE AFTER TEST)
    st.write("DEBUG KEY:", key)

    if key:
        model = try_init_model(key)
        if model:
            st.session_state.model = model
            st.session_state.api_key_valid = True
            st.session_state.last_api_key = key

# ------------------ UI ------------------
st.title("🚀 WorkFlow AI")

# ------------------ STATUS ------------------
if st.session_state.api_key_valid:
    st.success("✅ AI Connected & Ready")
else:
    st.error("❌ AI Not Connected")

# ------------------ TEST BUTTON ------------------
if st.button("Test AI"):
    if not st.session_state.model:
        st.warning("No AI model loaded")
    else:
        response = st.session_state.model.generate_content("Say hello")
        st.write(response.text)

# ------------------ DASHBOARD SAMPLE ------------------
st.subheader("📊 Dashboard")

col1, col2, col3 = st.columns(3)
col1.metric("Tasks", 47)
col2.metric("Emails", 8)
col3.metric("Meetings", 5)

# ------------------ FOOTER ------------------
st.markdown("---")
st.caption("WorkFlow AI · Streamlit + Gemini")
