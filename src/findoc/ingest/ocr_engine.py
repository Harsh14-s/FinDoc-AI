"""OCR Engine for FinDocAI.

Provides graceful OCR integration using Tesseract OCR via pytesseract.
Checks for Tesseract binary presence; if missing, provides clear Windows install
instructions and degrades gracefully without crashing the application.
Group G382: Harsh Shukla, Akshita Singh.
"""

import shutil
import os
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from PIL import Image
import pytesseract


COMMON_WINDOWS_TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
]


def check_tesseract_installed() -> Tuple[bool, Optional[str], str]:
    """Check if Tesseract binary is available on the system PATH or default Windows directories.

    Returns:
        (is_installed, executable_path, message)
    """
    # 1. Check if 'tesseract' is on the system PATH
    which_path = shutil.which("tesseract")
    if which_path:
        pytesseract.pytesseract.tesseract_cmd = which_path
        return True, which_path, f"Tesseract found on PATH: {which_path}"

    # 2. Check standard Windows installation directories
    for path_str in COMMON_WINDOWS_TESSERACT_PATHS:
        if os.path.isfile(path_str):
            pytesseract.pytesseract.tesseract_cmd = path_str
            return True, path_str, f"Tesseract found at: {path_str}"

    install_instructions = (
        "Tesseract OCR is not installed or not in PATH.\n"
        "To enable scanned image OCR on Windows:\n"
        "  1. Download the official installer from UB-Mannheim:\n"
        "     https://github.com/UB-Mannheim/tesseract/wiki\n"
        "  2. Run the installer (default path: C:\\Program Files\\Tesseract-OCR)\n"
        "  3. Restart terminal or add C:\\Program Files\\Tesseract-OCR to PATH.\n"
        "Note: Digital PDF processing remains fully functional without OCR."
    )
    return False, None, install_instructions


def extract_text_from_image(image_path: Path) -> Dict[str, Any]:
    """Extract text from a scanned image using Tesseract OCR with graceful fallback.

    Args:
        image_path: Path to PNG, JPG, or TIFF image file.

    Returns:
        Dictionary containing extracted text, ocr_available status, and confidence info.
    """
    is_installed, exec_path, msg = check_tesseract_installed()

    if not is_installed:
        return {
            "text": "",
            "ocr_available": False,
            "error": "Tesseract OCR binary not found",
            "install_instructions": msg,
            "source_type": "scanned_image"
        }

    try:
        image = Image.open(image_path)
        # Convert to RGB if palette or alpha
        if image.mode not in ("L", "RGB"):
            image = image.convert("RGB")

        # Extract text using pytesseract
        text = pytesseract.image_to_string(image, config="--psm 6")
        
        # Get OCR word confidence data if available
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        confidences = [int(c) for c in data.get("conf", []) if int(c) >= 0]
        avg_conf = (sum(confidences) / len(confidences) / 100.0) if confidences else 0.70

        return {
            "text": text,
            "ocr_available": True,
            "average_confidence": round(avg_conf, 3),
            "source_type": "scanned_image",
            "executable_path": exec_path
        }
    except Exception as e:
        return {
            "text": "",
            "ocr_available": True,
            "error": f"OCR processing failure: {str(e)}",
            "source_type": "scanned_image"
        }
