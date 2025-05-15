import pdfplumber
import docx2txt

class ParserAgent:
    def process(self, file_path):
        if file_path.endswith(".pdf"):
            return self._extract_pdf(file_path)
        elif file_path.endswith(".docx"):
            return self._extract_docx(file_path)
        else:
            raise ValueError("Unsupported file type")

    def _extract_pdf(self, file_path):
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text

    def _extract_docx(self, file_path):
        return docx2txt.process(file_path)
