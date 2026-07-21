from __future__ import annotations

import requests
import streamlit as st

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="Mobile Test Automation Generator", page_icon="📱")
st.title("AI Powered Mobile Test Automation Generator")
st.caption("Upload one or more screenshots, generate Appium scripts, and review them with a richer, more dynamic workflow")

st.info("Optional demo mode: click below to run a one-click sample flow using predefined demo screens.")

col1, col2 = st.columns([1, 1])
with col1:
    uploaded_files = st.file_uploader("Upload one or more mobile screenshots", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)
with col2:
    app_name = st.text_input("App name", value="Demo App")

if st.button("Run demo mode", type="primary"):
    st.session_state["demo_mode"] = True

if st.session_state.get("demo_mode"):
    st.subheader("Demo mode")
    st.write("This runs a predefined sample flow for management presentation purposes.")
    demo_screens = [
        ("Login Screen", "Login Screen", "image/png"),
        ("Cart Screen", "Cart Screen", "image/png"),
    ]
    demo_files = []
    for name, label, content_type in demo_screens:
        demo_files.append(("files", (f"{name.lower().replace(' ', '_')}.png", b"fake image bytes", content_type)))
    response = requests.post(f"{API_BASE}/upload_batch", files=demo_files, timeout=30)
    if response.ok:
        analyses = response.json().get("analyses", [])
        st.success(f"Demo processed {len(analyses)} screens")
        for analysis in analyses:
            st.write(f"**{analysis.get('screen_name', 'Screen')}**")
            st.dataframe([{"label": elem.get("label", ""), "type": elem.get("type", ""), "actions": ", ".join(elem.get("actions", []))} for elem in analysis.get("elements", [])])
        generate_response = requests.post(f"{API_BASE}/generate_batch", json={"analyses": analyses}, timeout=30)
        if generate_response.ok:
            generated_scripts = generate_response.json().get("scripts", [])
            for item in generated_scripts:
                st.subheader(item["screen_name"])
                st.code(item["script"], language="python")
        else:
            st.error("Demo generation failed")
    else:
        st.error("Demo upload failed")

if uploaded_files:
    st.subheader("Uploaded screenshots")
    for uploaded_file in uploaded_files:
        st.image(uploaded_file, caption=uploaded_file.name)

    if st.button("Generate, Review, and Execute"):
        files = [("files", (item.name, item.getvalue(), item.type)) for item in uploaded_files]
        response = requests.post(f"{API_BASE}/upload_batch", files=files, timeout=30)
        if response.ok:
            analyses = response.json().get("analyses", [])
            st.success(f"Processed {len(analyses)} screens")
            if analyses:
                for analysis in analyses:
                    st.write(f"**{analysis.get('screen_name', 'Screen')}**")
                    st.write(f"Detected elements: {len(analysis.get('elements', []))}")
                    st.dataframe([{"label": elem.get("label", ""), "type": elem.get("type", ""), "actions": ", ".join(elem.get("actions", []))} for elem in analysis.get("elements", [])])

                generate_response = requests.post(
                    f"{API_BASE}/generate_batch",
                    json={"analyses": analyses},
                    timeout=30,
                )
                if generate_response.ok:
                    generated_scripts = generate_response.json().get("scripts", [])
                    for item in generated_scripts:
                        st.subheader(item["screen_name"])
                        st.code(item["script"], language="python")

                        review_response = requests.post(
                            f"{API_BASE}/review",
                            json={"script": item["script"], "app_name": app_name},
                            timeout=30,
                        )
                        if review_response.ok:
                            review_payload = review_response.json()
                            st.metric("Review score", review_payload["overall_score"])
                            st.write(review_payload["summary"])

                        execute_response = requests.post(
                            f"{API_BASE}/execute",
                            json={"script": item["script"], "app_name": app_name},
                            timeout=30,
                        )
                        if execute_response.ok:
                            exec_payload = execute_response.json()
                            st.info(exec_payload["summary"])
                else:
                    st.error("Batch generation request failed")
        else:
            st.error("Batch upload request failed")

st.subheader("Execution history")
try:
    history = requests.get(f"{API_BASE}/history", timeout=30).json()
    if history:
        st.dataframe(history)
    else:
        st.caption("No reports yet")
except Exception:
    st.caption("History endpoint unavailable")
