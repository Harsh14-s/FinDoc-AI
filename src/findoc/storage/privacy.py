"""Privacy, Data Sanitization, and Masking Utilities for FinDocAI.

Implements strict privacy safeguards:
- PII masking for PAN, Aadhaar, and Bank Account Numbers.
- Safe audit logging without persisting plaintext sensitive identifiers.
- Right-to-be-forgotten document deletion utility.
Group G382: Harsh Shukla, Akshita Singh.
"""

from typing import Dict, Any
from findoc.extract.schemas import mask_sensitive_value
from findoc.storage.db import delete_document


def sanitize_for_logging(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize dictionary by masking sensitive PII values before logging or exporting.

    Ensures no raw financial account numbers, PANs, or Aadhaar numbers appear in log streams.
    """
    clean_dict = dict(data)

    if "account_number" in clean_dict and clean_dict["account_number"]:
        clean_dict["account_number"] = mask_sensitive_value(clean_dict["account_number"], "account")

    if clean_dict.get("document_type") == "pan_card" and clean_dict.get("id_number"):
        clean_dict["id_number"] = mask_sensitive_value(clean_dict["id_number"], "pan")

    if clean_dict.get("document_type") == "aadhaar_card" and clean_dict.get("id_number"):
        clean_dict["id_number"] = mask_sensitive_value(clean_dict["id_number"], "aadhaar")

    return clean_dict


def delete_document_record(doc_id: str) -> Dict[str, Any]:
    """Execute privacy deletion of all records associated with a document ID."""
    success = delete_document(doc_id)
    return {
        "doc_id": doc_id,
        "deleted": success,
        "message": f"Document {doc_id} and all related records deleted permanently." if success else f"Document {doc_id} not found."
    }
