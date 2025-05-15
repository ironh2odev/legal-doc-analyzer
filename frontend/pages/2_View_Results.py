# 2_View_Results.py

import streamlit as st
import requests
import io
import matplotlib.pyplot as plt
from collections import Counter

BACKEND_URL = "http://127.0.0.1:8000"

st.title("📊 View Results")

if "analysis_result" not in st.session_state or "uploaded_file" not in st.session_state:
    st.warning("⛔ Upload and analyze a document first.")
    st.stop()

result = st.session_state["analysis_result"]
file = st.session_state["uploaded_file"]

st.subheader("📋 Summary")
st.write(f"**Total Clauses:** {result['summary']['total_clauses']}")
st.write(f"**Total Obligations:** {result['summary']['total_obligations']}")
st.write("**Missing Clauses:**", ", ".join(result["summary"]["missing_clauses"]))

# 📊 Charts Section
st.markdown("### 📊 Clause Type Distribution")
types = [clause["type"] for clause in result["details"]]
type_counts = Counter(types)
fig1, ax1 = plt.subplots()
ax1.pie(type_counts.values(), labels=type_counts.keys(), autopct="%1.1f%%")
ax1.axis("equal")
st.pyplot(fig1)

st.markdown("### ⚠️ Risk Level Breakdown")
risks = [clause["risk"] for clause in result["details"]]
risk_counts = Counter(risks)
fig2, ax2 = plt.subplots()
ax2.bar(risk_counts.keys(), risk_counts.values())
ax2.set_xlabel("Risk Level")
ax2.set_ylabel("Number of Clauses")
ax2.set_title("Risk Distribution")
st.pyplot(fig2)

# 📄 Clause Details
st.subheader("📄 Clause Details")
for clause in result["details"]:
    with st.expander(clause["clause"][:100]):
        st.write(f"**Type:** {clause['type']}")
        st.write(f"**Risk:** {clause['risk']}")
        st.write(f"**Summary:** {clause['summary']}")
        if clause["obligations"]:
            st.write("**Obligations:**")
            for ob in clause["obligations"]:
                st.markdown(f"- {ob}")

# 📥 PDF Download
st.subheader("📥 Download PDF Report")

with st.spinner("Generating PDF..."):
    try:
        file_obj = io.BytesIO(st.session_state["uploaded_file"].getvalue())  # 🧠 Reset file pointer

        files = {"file": (st.session_state["uploaded_file_name"], file_obj, "application/pdf")}
        response = requests.post(f"{BACKEND_URL}/download", files=files)

        if response.status_code == 200:
            st.download_button(
                label="⬇️ Download Report",
                data=response.content,
                file_name="legal_analysis_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.error("❌ Failed to generate report.")
    except Exception as e:
        st.error(f"🚨 Error generating report: {e}")

