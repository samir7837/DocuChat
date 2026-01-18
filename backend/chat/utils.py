import pypdf
import pdfplumber
from typing import Dict, Any


def parse_pdf(path: str) -> Dict[str, Any]:
    try:
        return parse_with_pdfplumber(path)
    except:
        return parse_with_pypdf(path)


def parse_with_pdfplumber(path: str):
    content = {}
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            content[str(i + 1)] = page.extract_text() or ""
    return content


def parse_with_pypdf(path: str):
    content = {}
    with open(path, "rb") as f:
        reader = pypdf.PdfReader(f)
        for i, page in enumerate(reader.pages):
            content[str(i + 1)] = page.extract_text() or ""
    return content
