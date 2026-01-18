import os
import requests
import tempfile
import pypdf
import pdfplumber
from typing import Dict, Any


def download_pdf(url: str) -> str:
    """
    Download PDF from Cloudinary to temp file
    """
    response = requests.get(url, timeout=30)

    if response.status_code != 200:
        raise Exception(f"Failed to download PDF: {response.status_code}")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_file.write(response.content)
    temp_file.close()

    return temp_file.name


def parse_with_pdfplumber(path: str) -> Dict[str, Any]:
    content = {}

    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            content[str(i + 1)] = text

    return content


def parse_with_pypdf(path: str) -> Dict[str, Any]:
    content = {}

    with open(path, "rb") as f:
        reader = pypdf.PdfReader(f)
        for i, page in enumerate(reader.pages):
            content[str(i + 1)] = page.extract_text() or ""

    return content


def parse_pdf(file_url: str) -> Dict[str, Any]:
    """
    SAFE production parser
    """
    temp_path = download_pdf(file_url)

    try:
        try:
            return parse_with_pdfplumber(temp_path)
        except Exception:
            return parse_with_pypdf(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
