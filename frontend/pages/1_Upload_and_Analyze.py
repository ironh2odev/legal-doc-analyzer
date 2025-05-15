# 1_Upload_and_Analyze.py

import streamlit as st
import requests
import time

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(layout="wide")
st.title("📤 Upload & Analyze Document")

uploaded_file = st.file_uploader("📎 Choose a legal PDF file", type=["pdf"])

if uploaded_file:
    if st.button("🔍 Analyze Document"):
        progress_text = "🔄 Starting analysis..."
        progress_bar = st.progress(0, text=progress_text)

        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}

        try:
            progress_text = "📡 Sending to server..."
            progress_bar.progress(10, text=progress_text)
            time.sleep(0.5)

            response = requests.post(f"{BACKEND_URL}/results", files=files)

            if response.status_code == 200:
                progress_text = "🧠 Processing complete."
                progress_bar.progress(100, text=progress_text)

                result = response.json()
                st.session_state["analysis_result"] = result  # ✅ Used in View Results
                st.session_state["uploaded_file"] = uploaded_file
                st.session_state["uploaded_file_name"] = uploaded_file.name

                st.success("✅ Document analyzed successfully!")
                st.balloons()

                with st.expander("🔍 See raw JSON output"):
                    st.json(result)

                st.markdown("👉 Now head to **2️⃣ View Results** to explore insights.")
            else:
                st.error("❌ Analysis failed. Please try another document.")

        except Exception as e:
            st.error(f"🚨 Error: {e}")
