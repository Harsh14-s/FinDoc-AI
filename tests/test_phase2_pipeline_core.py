"""Unit and Integration Tests for Phase 2: Pipeline Core.

Tests Ingestion, Keyword & ML Classification, Schema Normalization & Extraction,
and Rule-Based Validation with explicit failure explanations.
Group G382: Harsh Shukla, Akshita Singh.
"""

import json
from pathlib import Path
import pytest

from findoc.ingest.ocr_engine import check_tesseract_installed, extract_text_from_image
from findoc.ingest.pdf_parser import extract_text_and_tables
from findoc.classify.rule_classifier import classify_by_rules
from findoc.classify.ml_classifier import MLDocumentClassifier
from findoc.classify.classifier_service import classify_document
from findoc.extract.schemas import normalize_amount, normalize_date, mask_sensitive_value
from findoc.extract.extractor_service import extract_document
from findoc.validate.validator import validate_document
from findoc.validate.rules import (
    check_required_fields,
    check_bank_balance_reconciliation,
    check_invoice_totals_reconciliation,
    check_identifier_formats,
    check_date_sanity,
    check_duplicate_transactions
)

BASE_DIR = Path(__file__).resolve().parent.parent


def test_tesseract_graceful_check():
    """Verify OCR check handles missing binary gracefully without raising unhandled exceptions."""
    is_installed, path, msg = check_tesseract_installed()
    assert isinstance(is_installed, bool)
    assert isinstance(msg, str)
    if not is_installed:
        assert "Tesseract OCR is not installed" in msg


def test_ingest_digital_pdf():
    """Verify PyMuPDF extracts text and tables from a generated PDF."""
    manifest_path = BASE_DIR / "data" / "dataset_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    sample = manifest["train"][0]
    pdf_path = BASE_DIR / sample["pdf_path"]

    res = extract_text_and_tables(pdf_path)
    assert res["error"] is None
    assert len(res["text"]) > 50
    assert res["page_count"] >= 1
    assert res["is_scanned"] is False


def test_baseline_and_ml_classification():
    """Verify both baseline rules and ML classifier predict correct document types."""
    sample_texts = {
        "bank_statement": "Apex National Bank Statement Account Number: 12345 IFSC: APEX012345 Opening Balance: INR 10,000 Closing Balance: INR 15,000 Withdrawal Deposit",
        "invoice": "TAX INVOICE Invoice No: INV-1001 Date: 2025-05-10 Vendor GSTIN: 07AAAAA1234A1Z5 Subtotal: 5000 GST: 900 Grand Total: 5900 Billed To:",
        "pan_card": "INCOME TAX DEPARTMENT GOVT OF INDIA Permanent Account Number (PAN): ABCDE1234F Name: John Doe Father's Name: Bob Doe",
        "aadhaar_card": "UNIQUE IDENTIFICATION AUTHORITY OF INDIA Aadhaar Number: 2345 6789 0123 Resident Name: Alice Doe Gender: Female"
    }

    for expected_type, sample_txt in sample_texts.items():
        # Baseline rules
        r_res = classify_by_rules(sample_txt)
        assert r_res["predicted_class"] == expected_type, f"Rule failed for {expected_type}"

    # Unified service
    res = classify_document(sample_texts["bank_statement"])
    assert res["final_prediction"] == "bank_statement"
    assert "rule_based" in res
    assert "ml_based" in res


def test_normalization_and_masking_helpers():
    """Verify date, amount normalization, and privacy masking functions."""
    assert normalize_amount("INR 12,345.50") == 12345.50
    assert normalize_amount("Rs. 1,000") == 1000.0
    assert normalize_amount("(500.00)") == -500.0
    assert normalize_amount("-") == 0.0

    assert normalize_date("15/08/2025") == "2025-08-15"
    assert normalize_date("2025-10-01") == "2025-10-01"

    # Privacy masking
    assert mask_sensitive_value("ABCDE1234F", "pan") == "ABXXXXXX4F"
    assert mask_sensitive_value("2345 6789 0123", "aadhaar") == "XXXX XXXX 0123"
    assert mask_sensitive_value("987654321012", "account") == "XXXXXXXX1012"


def test_clean_bank_statement_validation_passes():
    """Verify clean bank statement passes all reconciliation checks."""
    clean_data = {
        "document_type": "bank_statement",
        "account_number": "98765432101",
        "opening_balance": 50000.0,
        "total_deposits": 20000.0,
        "total_withdrawals": 15000.0,
        "closing_balance": 55000.0,
        "ifsc": "APEX0123456",
        "transactions": [
            {"date": "2025-05-01", "description": "SALARY", "ref_no": "TXN101", "debit": 0.0, "credit": 20000.0, "balance": 70000.0},
            {"date": "2025-05-05", "description": "RENT", "ref_no": "TXN102", "debit": 15000.0, "credit": 0.0, "balance": 55000.0}
        ]
    }
    report = validate_document(clean_data)
    assert report["overall_status"] == "PASS"
    assert report["failed_count"] == 0


def test_tampered_bank_balance_fails_with_reason():
    """Verify balance mismatch triggers VAL_BNK_REC with clear mathematical explanation."""
    tampered_data = {
        "document_type": "bank_statement",
        "account_number": "98765432101",
        "opening_balance": 50000.0,
        "total_deposits": 20000.0,
        "total_withdrawals": 15000.0,
        "closing_balance": 99999.0,  # Deliberately tampered
        "ifsc": "APEX012345"
    }
    rec_results = check_bank_balance_reconciliation(tampered_data)
    assert len(rec_results) >= 1
    rec_fail = rec_results[0]
    assert rec_fail["rule_id"] == "VAL_BNK_REC"
    assert rec_fail["status"] == "FAIL"
    assert "Closing balance mismatch" in rec_fail["reason"]
    assert "Discrepancy" in rec_fail["reason"]


def test_tampered_invoice_total_fails_with_reason():
    """Verify invoice arithmetic mismatch triggers VAL_INV_TOT with exact discrepancy."""
    tampered_inv = {
        "document_type": "invoice",
        "invoice_number": "INV-2025-001",
        "invoice_date": "2025-04-10",
        "subtotal": 10000.0,
        "tax_amount": 1800.0,
        "grand_total": 15000.0,  # Should be 11,800.0
        "line_items": []
    }
    res = check_invoice_totals_reconciliation(tampered_inv)
    assert len(res) >= 1
    assert res[0]["rule_id"] == "VAL_INV_TOT"
    assert res[0]["status"] == "FAIL"
    assert "Invoice Grand Total mismatch" in res[0]["reason"]
    assert "3,200.00" in res[0]["reason"]


def test_invalid_pan_and_aadhaar_format_rules():
    """Verify PAN and Aadhaar format checks flag invalid inputs with correct rule IDs."""
    # Invalid PAN
    pan_res = check_identifier_formats({"id_number": "INVALID12"}, "pan_card")
    assert any(r["rule_id"] == "VAL_FMT_PAN" and r["status"] == "FAIL" for r in pan_res)

    # Valid PAN
    pan_valid_res = check_identifier_formats({"id_number": "ABCDE1234F"}, "pan_card")
    assert any(r["rule_id"] == "VAL_FMT_PAN" and r["status"] == "PASS" for r in pan_valid_res)

    # Invalid Aadhaar
    aad_res = check_identifier_formats({"id_number": "1234 ABCD 5678"}, "aadhaar_card")
    assert any(r["rule_id"] == "VAL_FMT_AAD" and r["status"] == "FAIL" for r in aad_res)


def test_date_sanity_and_duplicates():
    """Verify future date and duplicate transactions rules."""
    # Future date check
    future_data = {
        "document_type": "bank_statement",
        "transactions": [{"date": "2029-08-20", "ref_no": "TXN999"}]
    }
    date_res = check_date_sanity(future_data, "bank_statement")
    assert any(r["rule_id"] == "VAL_DAT_SAN" and r["status"] == "FAIL" for r in date_res)

    # Duplicate transaction check
    dup_data = {
        "transactions": [
            {"ref_no": "TXN888", "date": "2025-05-01", "debit": 500.0, "credit": 0.0},
            {"ref_no": "TXN888", "date": "2025-05-01", "debit": 500.0, "credit": 0.0}
        ]
    }
    dup_res = check_duplicate_transactions(dup_data)
    assert dup_res is not None
    assert dup_res["rule_id"] == "VAL_DUP_TXN"
    assert dup_res["status"] == "FAIL"
