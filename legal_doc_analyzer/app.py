from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import tempfile
import os

from legal_doc_analyzer.agents.parser_agent import ParserAgent
from legal_doc_analyzer.agents.segmenter_agent import ClauseSegmenterAgent
from legal_doc_analyzer.agents.classifier_agent import ClauseClassifierAgent
from legal_doc_analyzer.agents.summarizer_agent import SummarizerAgent
from legal_doc_analyzer.agents.risk_analyzer_agent import RiskAnalyzerAgent
from legal_doc_analyzer.agents.missing_clause_detector import MissingClauseDetectorAgent
from legal_doc_analyzer.agents.obligation_extractor import ObligationExtractorAgent
from legal_doc_analyzer.agents.consolidator_agent import ConsolidatorAgent

from legal_doc_analyzer.utils.logger import get_logger
from legal_doc_analyzer.utils.pdf_generator import generate_pdf

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
logger = get_logger("app")

# 🚦 Rate limiter setup
limiter = Limiter(key_func=get_remote_address, default_limits=["20/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ✅ PDF validation
def is_valid_pdf(upload_file: UploadFile, max_size_mb: int = 5) -> bool:
    if not upload_file.filename.endswith(".pdf"):
        return False
    contents = upload_file.file.read()
    if len(contents) > max_size_mb * 1024 * 1024 or not contents.startswith(b"%PDF"):
        return False
    upload_file.file.seek(0)
    return True

# ⚙️ Agents
parser_agent = ParserAgent()
segmenter_agent = ClauseSegmenterAgent()
classifier_agent = ClauseClassifierAgent()
summarizer_agent = SummarizerAgent()
risk_analyzer_agent = RiskAnalyzerAgent()
missing_clause_detector = MissingClauseDetectorAgent()
obligation_extractor = ObligationExtractorAgent()
consolidator_agent = ConsolidatorAgent()

# 🧠 Helper to process PDF
def process_document(file_path):
    text = parser_agent.process(file_path)
    clauses = segmenter_agent.process(text)

    results = []
    all_obligations = []

    for clause in clauses:
        clause_type = classifier_agent.classify(clause)
        summary = summarizer_agent.summarize(clause)
        risk_flag = risk_analyzer_agent.analyze(clause)
        obligations = obligation_extractor.extract(clause)
        all_obligations.extend(obligations)
        results.append({
            "clause": clause,
            "type": clause_type,
            "summary": summary,
            "risk": risk_flag,
            "obligations": obligations,
        })

    missing = missing_clause_detector.detect(clauses)
    consolidated = consolidator_agent.consolidate(results, missing, all_obligations)
    consolidated["details"] = results
    return consolidated, clauses

# 🧾 Main results
@app.post("/results")
@limiter.limit("10/minute")
async def get_results(request: Request, file: UploadFile = File(...)):
    if not file or not is_valid_pdf(file):
        raise HTTPException(status_code=400, detail="Invalid or corrupted PDF")

    try:
        logger.info("🔄 Received file: %s", file.filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        data, _ = process_document(tmp_path)
        logger.info("✅ Document processed successfully.")
        return JSONResponse(content=data)
    except Exception as e:
        logger.error("❌ Error: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if os.path.exists(tmp_path): os.remove(tmp_path)

# 🧾 Single PDF report
@app.post("/download")
@limiter.limit("5/minute")
async def download_pdf(request: Request, file: UploadFile = File(...)):
    if not file or not is_valid_pdf(file):
        raise HTTPException(status_code=400, detail="Invalid or corrupted PDF")

    try:
        logger.info("⬇️ Generating PDF for: %s", file.filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            path = tmp.name

        data, _ = process_document(path)
        pdf_path = generate_pdf(data)
        logger.info(f"✅ PDF written successfully to: {pdf_path}")
    except Exception as e:
        logger.error("❌ PDF error: %s", str(e))
        raise HTTPException(status_code=500, detail="PDF generation failed")
    finally:
        if os.path.exists(path): os.remove(path)

    return FileResponse(pdf_path, filename="legal_report.pdf", media_type="application/pdf")

# 🆚 Compare two documents
@app.post("/compare")
@limiter.limit("10/minute")
async def compare_documents(request: Request, file1: UploadFile = File(...), file2: UploadFile = File(...)):
    if not file1 or not is_valid_pdf(file1):
        raise HTTPException(status_code=400, detail="First file is invalid.")
    if not file2 or not is_valid_pdf(file2):
        raise HTTPException(status_code=400, detail="Second file is invalid.")

    try:
        logger.info("🔍 Comparing: %s vs %s", file1.filename, file2.filename)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp1:
            tmp1.write(file1.file.read())
            path1 = tmp1.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp2:
            tmp2.write(file2.file.read())
            path2 = tmp2.name

        doc1_data, doc1_clauses = process_document(path1)
        doc2_data, doc2_clauses = process_document(path2)

        return {
            "doc1_name": file1.filename,
            "doc2_name": file2.filename,
            "doc1": doc1_data,
            "doc2": doc2_data,
            "unique_doc1": list(set(doc1_clauses) - set(doc2_clauses)),
            "unique_doc2": list(set(doc2_clauses) - set(doc1_clauses)),
        }
    except Exception as e:
        logger.error("❌ Comparison error: %s", str(e))
        raise HTTPException(status_code=500, detail="Comparison failed")
    finally:
        for path in [path1, path2]:
            if os.path.exists(path): os.remove(path)

# 🧾 Download comparison report
@app.post("/compare/download")
@limiter.limit("5/minute")
async def download_comparison_pdf(request: Request, file1: UploadFile = File(...), file2: UploadFile = File(...)):
    if not file1 or not is_valid_pdf(file1):
        raise HTTPException(status_code=400, detail="First file is invalid.")
    if not file2 or not is_valid_pdf(file2):
        raise HTTPException(status_code=400, detail="Second file is invalid.")

    try:
        logger.info("⬇️ Generating comparison PDF...")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp1:
            tmp1.write(file1.file.read())
            path1 = tmp1.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp2:
            tmp2.write(file2.file.read())
            path2 = tmp2.name

        doc1_data, doc1_clauses = process_document(path1)
        doc2_data, doc2_clauses = process_document(path2)

        comparison_data = {
            "doc1_name": file1.filename,
            "doc2_name": file2.filename,
            "doc1": doc1_data,
            "doc2": doc2_data,
            "unique_doc1": list(set(doc1_clauses) - set(doc2_clauses)),
            "unique_doc2": list(set(doc2_clauses) - set(doc1_clauses)),
        }

        pdf_path = generate_pdf(comparison_data, mode="comparison")
        logger.info(f"✅ PDF written successfully to: {pdf_path}")
    except Exception as e:
        logger.error("❌ Comparison PDF failed: %s", str(e))
        raise HTTPException(status_code=500, detail="PDF generation failed")
    finally:
        for path in [path1, path2]:
            if os.path.exists(path): os.remove(path)

    return FileResponse(pdf_path, filename="comparison_report.pdf", media_type="application/pdf")
