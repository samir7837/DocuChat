import requests
import tempfile
import os
import pypdf
from pdfplumber import open as pdf_open
from typing import Dict, Any


# ============================
# Local parsers (unchanged)
# ============================

def parse_pdf_with_pypdf(file_path: str) -> Dict[str, Any]:
    with open(file_path, "rb") as file:
        pdf = pypdf.PdfReader(file)
        content = {}

        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text = page.extract_text() or ""

            sections = []
            lines = text.split("\n")
            current = {"title": "General", "content": "", "page": page_num + 1}

            for line in lines:
                line = line.strip()
                if line and len(line) < 100 and line[0].isupper():
                    if current["content"]:
                        sections.append(current)
                    current = {"title": line, "content": "", "page": page_num + 1}
                else:
                    current["content"] += line + " "

            if current["content"]:
                sections.append(current)

            content[str(page_num + 1)] = {
                "text": text,
                "sections": sections
            }

        return content


def parse_pdf_with_pdfplumber(file_path: str) -> Dict[str, Any]:
    content = {}

    with pdf_open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text() or ""

            sections = []
            lines = text.split("\n")
            current = {"title": "General", "content": "", "page": page_num + 1}

            for line in lines:
                line = line.strip()
                if line and len(line) < 100 and line[0].isupper():
                    if current["content"]:
                        sections.append(current)
                    current = {"title": line, "content": "", "page": page_num + 1}
                else:
                    current["content"] += line + " "

            if current["content"]:
                sections.append(current)

            content[str(page_num + 1)] = {
                "text": text,
                "sections": sections
            }

    return content


# ============================
# CLOUDINARY-SAFE WRAPPER
# ============================

def parse_pdf(file_url: str) -> Dict[str, Any]:
    """
    Download PDF from Cloudinary → parse locally → delete temp file
    """

    response = requests.get(file_url)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(response.content)
        temp_path = tmp.name

    try:
        try:
            return parse_pdf_with_pdfplumber(temp_path)
        except Exception:
            return parse_pdf_with_pypdf(temp_path)
    finally:
        os.remove(temp_path)
