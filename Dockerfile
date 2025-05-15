FROM python:3.11-slim

# Install wkhtmltopdf dependencies
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    libxrender1 \
    libxext6 \
    libfontconfig1 \
    && apt-get clean

# Set work directory
WORKDIR /app

# Copy all project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Start app
CMD ["uvicorn", "legal_doc_analyzer.app:app", "--host", "0.0.0.0", "--port", "8000"]