"""Extraction Service Dispatcher for FinDocAI.

Routes parsed document content to the appropriate specialized extractor
(Bank Statement, Invoice, KYC PAN, KYC Aadhaar).
Group G382: Harsh Shukla, Akshita Singh.
"""

from typing import Dict, Any
from findoc.extract.bank_statement_extractor import extract_bank_statement
from findoc.extract.invoice_extractor import extract_invoice
from findoc.extract.kyc_extractor import extract_kyc


def extract_document(doc_type: str, parsed_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatch extraction based on classified document type.

    Args:
        doc_type: Classified document type (bank_statement, invoice, pan_card, aadhaar_card)
        parsed_doc: Parsed text and tables dictionary from ingest.pdf_parser

    Returns:
        Structured normalized extraction payload.
    """
    if doc_type == "bank_statement":
        data = extract_bank_statement(parsed_doc)
    elif doc_type == "invoice":
        data = extract_invoice(parsed_doc)
    elif doc_type in ("pan_card", "aadhaar_card"):
        data = extract_kyc(doc_type, parsed_doc)
    else:
        # Fallback generic extraction
        data = {
            "raw_text": parsed_doc.get("text", "")[:500],
            "field_confidences": {}
        }

    data["document_type"] = doc_type
    return data
