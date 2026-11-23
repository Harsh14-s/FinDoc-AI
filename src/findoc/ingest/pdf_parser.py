"""PDF Parser for FinDocAI.

Extracts text, page layouts, and tables from digital PDF documents using PyMuPDF and pdfplumber.
Detects whether the input PDF contains digital text or requires OCR fallback.
Group G382: Harsh Shukla, Akshita Singh.
"""

from pathlib import Path
from typing import Dict, Any, List
import pymupdf
import pdfplumber

from findoc.ingest.ocr_engine import extract_text_from_image, check_tesseract_installed


def extract_text_and_tables(file_path: Path) -> Dict[str, Any]:
    """Extract full text, per-page text, and tabular structures from a PDF or image file.

    Args:
        file_path: Path to the target document (.pdf, .png, .jpg, etc.)

    Returns:
        Structured dictionary containing extracted text, table rows, and digital/scanned metadata.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = file_path.suffix.lower()

    # If direct image input, route to OCR engine
    if ext in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
        ocr_res = extract_text_from_image(file_path)
        return {
            "file_name": file_path.name,
            "text": ocr_res.get("text", ""),
            "pages": [ocr_res.get("text", "")],
            "tables": [],
            "page_count": 1,
            "is_scanned": True,
            "ocr_used": True,
            "ocr_available": ocr_res.get("ocr_available", False),
            "install_instructions": ocr_res.get("install_instructions", ""),
            "error": ocr_res.get("error")
        }

    # Otherwise process as PDF
    full_text = []
    page_texts = []
    extracted_tables: List[List[List[str]]] = []

    try:
        # 1. PyMuPDF for fast, robust digital text extraction
        doc = pymupdf.open(str(file_path))
        page_count = len(doc)
        for page_num in range(page_count):
            page = doc.load_page(page_num)
            p_text = page.get_text("text")
            page_texts.append(p_text)
            full_text.append(p_text)
        doc.close()

        combined_text = "\n".join(full_text).strip()

        # 2. Extract tables using pdfplumber if digital text exists
        try:
            with pdfplumber.open(str(file_path)) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for t in tables:
                        if t and len(t) > 1:
                            # Clean empty strings / None values
                            cleaned_table = [
                                [str(cell).strip() if cell is not None else "" for cell in row]
                                for row in t
                            ]
                            extracted_tables.append(cleaned_table)
        except Exception:
            # Table extraction is an optional enhancement; text is primary
            pass

        # 3. Detect if PDF is an image-only scan (less than 40 text characters)
        is_scanned = len(combined_text) < 40
        ocr_used = False
        install_instructions = ""

        if is_scanned:
            # Render first page to temporary image and attempt OCR
            is_installed, _, msg = check_tesseract_installed()
            install_instructions = msg
            if is_installed:
                doc = pymupdf.open(str(file_path))
                page = doc.load_page(0)
                pix = page.get_pixmap(dpi=150)
                temp_img_path = file_path.parent / f"_temp_scan_{file_path.stem}.png"
                pix.save(str(temp_img_path))
                doc.close()

                ocr_res = extract_text_from_image(temp_img_path)
                if temp_img_path.exists():
                    temp_img_path.unlink()

                combined_text = ocr_res.get("text", "")
                page_texts = [combined_text]
                ocr_used = True

        return {
            "file_name": file_path.name,
            "text": combined_text,
            "pages": page_texts,
            "tables": extracted_tables,
            "page_count": page_count,
            "is_scanned": is_scanned,
            "ocr_used": ocr_used,
            "install_instructions": install_instructions,
            "error": None
        }

    except Exception as e:
        return {
            "file_name": file_path.name,
            "text": "",
            "pages": [],
            "tables": [],
            "page_count": 0,
            "is_scanned": False,
            "ocr_used": False,
            "install_instructions": "",
            "error": f"Failed to parse document: {str(e)}"
        }
