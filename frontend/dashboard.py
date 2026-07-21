from __future__ import annotations

import requests
import streamlit as st

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="Automation Dashboard", page_icon="📊")
st.title("Automation Dashboard")
st.caption("Track generated scripts, review scores, and execution outcomes")

try:
    history = requests.get(f"{API_BASE}/history", timeout=30).json()
except Exception:
    history = []

if history:
    total_reports = len(history)
    completed_runs = sum(1 for item in history if item.get("status") == "completed")
    st.metric("Total reports", total_reports)
    st.metric("Completed runs", completed_runs)
    st.dataframe(history)
else:
    st.info("No execution reports available yet.")
