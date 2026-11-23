"""KYC Information Extractor for FinDocAI.

Extracts structured attributes from PAN and Aadhaar identity documents
using targeted regex patterns and boundary markers.
Group G382: Harsh Shukla, Akshita Singh.
"""

import re
from typing import Dict, Any
from findoc.extract.schemas import normalize_date, KYCSchema


def extract_kyc(doc_type: str, parsed_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Extract structured attributes from a KYC document (PAN or Aadhaar).

    Args:
        doc_type: Either 'pan_card' or 'aadhaar_card'
        parsed_doc: Dictionary returned by ingest.pdf_parser.extract_text_and_tables

    Returns:
        Structured KYC dictionary with normalized fields and confidences.
    """
    text = parsed_doc.get("text", "")
    is_ocr = parsed_doc.get("ocr_used", False) or parsed_doc.get("is_scanned", False)
    conf_penalty = 0.85 if is_ocr else 1.0

    confidences: Dict[str, float] = {}

    if doc_type == "pan_card":
        # 1. PAN Number
        pan_match = re.search(r"Permanent Account Number.*?:?\s*([A-Za-z0-9]+)", text, re.IGNORECASE)
        if pan_match:
            pan_num = pan_match.group(1).strip().upper()
            confidences["id_number"] = round(0.98 * conf_penalty, 2)
        else:
            pan_any = re.search(r"\b([A-Z]{5}[0-9]{4}[A-Z]{1})\b", text)
            pan_num = pan_any.group(1).strip() if pan_any else None
            confidences["id_number"] = round(0.75 * conf_penalty, 2) if pan_num else 0.0

        # 2. Name
        name_match = re.search(r"\bName:\s*([^\n\r|]+)", text, re.IGNORECASE)
        full_name = name_match.group(1).strip() if name_match else None
        confidences["full_name"] = round(0.92 * conf_penalty, 2) if full_name else 0.0

        # 3. Father's Name
        father_match = re.search(r"Father'?s Name:\s*([^\n\r|]+)", text, re.IGNORECASE)
        father_name = father_match.group(1).strip() if father_match else None
        confidences["father_name"] = round(0.90 * conf_penalty, 2) if father_name else 0.0

        # 4. DOB
        dob_match = re.search(r"Date of Birth:\s*([^\n\r|]+)", text, re.IGNORECASE)
        dob = normalize_date(dob_match.group(1).strip()) if dob_match else None
        confidences["dob"] = round(0.95 * conf_penalty, 2) if dob else 0.0

        return {
            "document_type": "pan_card",
            "full_name": full_name,
            "father_name": father_name,
            "gender": None,
            "dob": dob,
            "id_number": pan_num,
            "address": None,
            "field_confidences": confidences
        }

    else:  # Aadhaar card
        # 1. Aadhaar Number
        aadhaar_match = re.search(r"Aadhaar Number:\s*([0-9\sA-Za-z]+)", text, re.IGNORECASE)
        if aadhaar_match:
            aadhaar_num = aadhaar_match.group(1).strip()
            confidences["id_number"] = round(0.98 * conf_penalty, 2)
        else:
            aadhaar_any = re.search(r"\b(\d{4}\s\d{4}\s\d{4})\b", text)
            aadhaar_num = aadhaar_any.group(1).strip() if aadhaar_any else None
            confidences["id_number"] = round(0.75 * conf_penalty, 2) if aadhaar_num else 0.0

        # 2. Resident Name
        name_match = re.search(r"Resident Name:\s*([^\n\r|]+)", text, re.IGNORECASE)
        full_name = name_match.group(1).strip() if name_match else None
        confidences["full_name"] = round(0.92 * conf_penalty, 2) if full_name else 0.0

        # 3. Gender
        gender_match = re.search(r"Gender:\s*([A-Za-z]+)", text, re.IGNORECASE)
        gender = gender_match.group(1).strip() if gender_match else None
        confidences["gender"] = round(0.95 * conf_penalty, 2) if gender else 0.0

        # 4. DOB
        dob_match = re.search(r"Date of Birth:\s*([^\n\r|]+)", text, re.IGNORECASE)
        dob = normalize_date(dob_match.group(1).strip()) if dob_match else None
        confidences["dob"] = round(0.95 * conf_penalty, 2) if dob else 0.0

        # 5. Address
        addr_match = re.search(r"Address:\s*([^\n\r|*]+)", text, re.IGNORECASE)
        address = addr_match.group(1).strip() if addr_match else None
        confidences["address"] = round(0.85 * conf_penalty, 2) if address else 0.0

        return {
            "document_type": "aadhaar_card",
            "full_name": full_name,
            "father_name": None,
            "gender": gender,
            "dob": dob,
            "id_number": aadhaar_num,
            "address": address,
            "field_confidences": confidences
        }
