# 🧾 Legal Document Analyzer

An AI-powered legal document analyzer and comparator built with FastAPI and Streamlit. Upload, analyze, and compare legal contracts — all with clause classification, risk analysis, and PDF export.

## Features
- Clause segmentation and classification
- Risk flagging
- Obligation extraction
- Missing clause detection
- PDF summary reports
- Document-to-document comparison
- Streamlit UI + FastAPI backend

## Run Locally

```bash
git clone https://github.com/ironh2odev/legal-doc-analyzer.git
cd legal-doc-analyzer
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn legal_doc_analyzer.app:app --reload
