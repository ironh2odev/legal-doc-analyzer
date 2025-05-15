# 3_Compare_Documents.py

import streamlit as st
import requests
import pandas as pd

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(layout="wide")
st.title("🆚 Compare Legal Documents")

# Upload files
left_col, right_col = st.columns(2)
with left_col:
    doc1 = st.file_uploader("Upload First Document", type=["pdf"], key="doc1")
with right_col:
    doc2 = st.file_uploader("Upload Second Document", type=["pdf"], key="doc2")

# Analyze and store file bytes
if doc1 and doc2:
    if st.button("🔍 Analyze and Compare"):
        with st.spinner("Analyzing both documents..."):
            doc1_bytes = doc1.read()
            doc2_bytes = doc2.read()

            files = [
                ("file1", (doc1.name, doc1_bytes, "application/pdf")),
                ("file2", (doc2.name, doc2_bytes, "application/pdf")),
            ]
            response = requests.post(f"{BACKEND_URL}/compare", files=files)

            if response.status_code == 200:
                comparison = response.json()
                st.session_state["comparison_result"] = comparison
                st.session_state["doc1_bytes"] = doc1_bytes
                st.session_state["doc2_bytes"] = doc2_bytes
                st.session_state["doc1_name"] = doc1.name
                st.session_state["doc2_name"] = doc2.name
            else:
                st.error("❌ Comparison failed.")

# Show results if available
if "comparison_result" in st.session_state:
    result = st.session_state["comparison_result"]
    doc1_name = result.get("doc1_name", "Document 1")
    doc2_name = result.get("doc2_name", "Document 2")

    st.subheader("📋 Summary Comparison")
    st.markdown("""
        <style>
            .sticky-header th { position: sticky; top: 0; background: #f0f2f6; }
            .diff-green { background-color: #e6ffed; padding: 5px; }
            .diff-red { background-color: #ffe6e6; padding: 5px; }
            .risk-icon { font-size: 1.2em; }
        </style>
    """, unsafe_allow_html=True)

    # Use pandas DataFrame to avoid pyarrow errors
    summary_df = pd.DataFrame({
        "Metric": ["Total Clauses", "Total Obligations", "Missing Clauses"],
        doc1_name: [
            str(result["doc1"]["summary"]["total_clauses"]),
            str(result["doc1"]["summary"]["total_obligations"]),
            ", ".join(result["doc1"]["summary"]["missing_clauses"]),
        ],
        doc2_name: [
            str(result["doc2"]["summary"]["total_clauses"]),
            str(result["doc2"]["summary"]["total_obligations"]),
            ", ".join(result["doc2"]["summary"]["missing_clauses"]),
        ]
    })

    st.dataframe(summary_df, use_container_width=True)

    st.markdown("### ⚖️ Clause Differences (Experimental)")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"📄 **Unique to {doc1_name}**")
        for clause in result["unique_doc1"]:
            st.markdown(f'<div class="diff-green">✅ {clause}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f"📄 **Unique to {doc2_name}**")
        for clause in result["unique_doc2"]:
            st.markdown(f'<div class="diff-green">✅ {clause}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📎 Download Comparison")

    if st.button("📥 Download PDF Summary"):
        doc1_bytes = st.session_state.get("doc1_bytes")
        doc2_bytes = st.session_state.get("doc2_bytes")
        doc1_name = st.session_state.get("doc1_name", "document1.pdf")
        doc2_name = st.session_state.get("doc2_name", "document2.pdf")

        if doc1_bytes and doc2_bytes:
            with st.spinner("📄 Generating PDF..."):
                try:
                    files = [
                        ("file1", (doc1_name, doc1_bytes, "application/pdf")),
                        ("file2", (doc2_name, doc2_bytes, "application/pdf")),
                    ]
                    resp = requests.post(f"{BACKEND_URL}/compare/download", files=files)
                    if resp.status_code == 200:
                        st.success("✅ PDF report ready!")
                        st.download_button(
                            label="⬇️ Click to Download PDF",
                            data=resp.content,
                            file_name="comparison_report.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error("❌ PDF generation failed.")
                except Exception as e:
                    st.error(f"🚨 Error during PDF generation: {e}")
        else:
            st.error("📎 Please re-upload both documents before downloading the PDF.")
