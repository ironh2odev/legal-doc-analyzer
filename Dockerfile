FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "legal_doc_analyzer.app:app", "--host", "0.0.0.0", "--port", "8000"]