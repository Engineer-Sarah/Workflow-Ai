import streamlit as st
import os

st.title("🔍 Secrets Debug Test")

st.write("### Checking st.secrets:")
try:
    key = st.secrets["GEMINI_API_KEY"]
    st.success(f"✅ st.secrets works! Key starts with: {key[:8]}...")
except Exception as e:
    st.error(f"❌ st.secrets failed: {e}")

st.write("### Checking os.environ:")
try:
    key2 = os.environ.get("GEMINI_API_KEY", "")
    if key2:
        st.success(f"✅ os.environ works! Key starts with: {key2[:8]}...")
    else:
        st.warning("⚠️ os.environ is empty")
except Exception as e:
    st.error(f"❌ os.environ failed: {e}")

st.write("### All available secrets keys:")
try:
    st.write(list(st.secrets.keys()))
except Exception as e:
    st.error(f"❌ Cannot list secrets: {e}")
