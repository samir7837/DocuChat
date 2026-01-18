import requests
import tempfile
import pypdf
from pdfplumber import open as pdf_open


def parse_pdf_from_url(url: str):
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Failed to download PDF: {response.status_code}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(response.content)
        tmp_path = tmp.name

    return parse_pdf(tmp_path)


def parse_pdf(file_path: str):
    try:
        with pdf_open(file_path) as pdf:
            content = {}
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                content[str(i + 1)] = {"text": text}
            return content
    except:
        reader = pypdf.PdfReader(file_path)
        content = {}
        for i, page in enumerate(reader.pages):
            content[str(i + 1)] = {"text": page.extract_text() or ""}
        return content
