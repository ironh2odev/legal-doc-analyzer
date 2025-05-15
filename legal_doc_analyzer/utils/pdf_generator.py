# legal_doc_analyzer/utils/pdf_generator.py

from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "output"))

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def generate_pdf(data: dict, mode: str = "single") -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{mode}_report_{timestamp}.pdf"
    output_path = os.path.join(OUTPUT_DIR, filename)

    generation_date = datetime.now().strftime("%B %d, %Y at %H:%M")

    try:
        if mode == "comparison":
            template = env.get_template("comparison_template.html")
            html_out = template.render(data=data, now=generation_date)
        else:
            template = env.get_template("report_template.html")
            html_out = template.render(data=data, generation_date=generation_date)

        HTML(string=html_out).write_pdf(output_path)

        # Log confirmation
        if os.path.exists(output_path):
            print(f"✅ PDF written successfully to: {output_path}")
        else:
            print(f"❌ PDF generation attempted but file not found: {output_path}")
            raise FileNotFoundError(f"Generated file missing at {output_path}")

        return output_path

    except Exception as e:
        print(f"❌ Error during PDF generation: {e}")
        raise
