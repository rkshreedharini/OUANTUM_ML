import fitz  # PyMuPDF
from config import PDF_DIR

def read_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        text += page.get_text()

    doc.close()
    return text