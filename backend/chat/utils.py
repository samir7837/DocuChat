import pypdf
import pdfplumber
from typing import Dict, Any


def parse_pdf(file_obj) -> Dict[str, Any]:
    """
    Parse PDF directly from uploaded file (InMemoryUploadedFile)
    """

    content = {}

    try:
        with pdfplumber.open(file_obj) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                content[str(i + 1)] = {
                    "text": text,
                    "sections": [
                        {
                            "title": "Page Content",
                            "content": text,
                            "page": i + 1,
                        }
                    ],
                }
        return content

    except Exception:
        # fallback to pypdf
        file_obj.seek(0)

        reader = pypdf.PdfReader(file_obj)
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            content[str(i + 1)] = {
                "text": text,
                "sections": [
                    {
                        "title": "Page Content",
                        "content": text,
                        "page": i + 1,
                    }
                ],
            }

        return content
