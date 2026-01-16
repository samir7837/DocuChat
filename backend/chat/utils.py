import pypdf
from pdfplumber import open as pdf_open
from typing import Dict, Any, List

def parse_pdf_with_pypdf(file_path: str) -> Dict[str, Any]:
    """Parse PDF using pypdf and extract structured content."""
    with open(file_path, 'rb') as file:
        pdf = pypdf.PdfReader(file)
        content = {}
        
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text = page.extract_text()
            
            # Simple section detection (basic heuristic)
            sections = []
            lines = text.split('\n')
            current_section = {"title": "General", "content": "", "page": page_num + 1}
            
            for line in lines:
                line = line.strip()
                if line and len(line) < 100 and line[0].isupper():  # Potential header
                    if current_section["content"]:
                        sections.append(current_section)
                    current_section = {"title": line, "content": "", "page": page_num + 1}
                else:
                    current_section["content"] += line + " "
            
            if current_section["content"]:
                sections.append(current_section)
            
            content[str(page_num + 1)] = {"text": text, "sections": sections}
        
        return content

def parse_pdf_with_pdfplumber(file_path: str) -> Dict[str, Any]:
    """Parse PDF using pdfplumber for better text extraction."""
    with pdf_open(file_path) as pdf:
        content = {}
        
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            
            # Similar section detection
            sections = []
            lines = text.split('\n')
            current_section = {"title": "General", "content": "", "page": page_num + 1}
            
            for line in lines:
                line = line.strip()
                if line and len(line) < 100 and line[0].isupper():
                    if current_section["content"]:
                        sections.append(current_section)
                    current_section = {"title": line, "content": "", "page": page_num + 1}
                else:
                    current_section["content"] += line + " "
            
            if current_section["content"]:
                sections.append(current_section)
            
            content[str(page_num + 1)] = {"text": text, "sections": sections}
        
        return content

def parse_pdf(file_path: str) -> Dict[str, Any]:
    """Main parsing function, try pdfplumber first."""
    try:
        return parse_pdf_with_pdfplumber(file_path)
    except:
        return parse_pdf_with_pypdf(file_path)