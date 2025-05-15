FROM python:3.11-slim

# Install required system packages for WeasyPrint
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libpango1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    shared-mime-info \
    fonts-liberation \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port and run the app
EXPOSE 8000
CMD ["uvicorn", "legal_doc_analyzer.app:app", "--host", "0.0.0.0", "--port", "8000"]
