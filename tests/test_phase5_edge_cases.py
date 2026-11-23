"""Edge Case and Robustness Tests for Phase 5.

Verifies system resilience under corrupt files, empty inputs, missing fields,
and boundary conditions.
Group G382: Harsh Shukla, Akshita Singh.
"""

from pathlib import Path
import pytest

from findoc.ingest.pdf_parser import extract_text_and_tables
from findoc.validate.validator import validate_document
from findoc.validate.rules import check_required_fields, check_identifier_formats
from findoc.flags.engine import evaluate_review_priority
from findoc.extract.schemas import normalize_amount, normalize_date

BASE_DIR = Path(__file__).resolve().parent.parent


def test_empty_file_handling(tmp_path):
    """Verify empty 0-byte file is handled gracefully without uncaught exceptions."""
    empty_file = tmp_path / "empty_doc.pdf"
    empty_file.write_bytes(b"")

    res = extract_text_and_tables(empty_file)
    assert res is not None
    # PyMuPDF fails gracefully on empty file and records error message
    assert res["error"] is not None or len(res["text"]) == 0


def test_corrupt_file_handling(tmp_path):
    """Verify corrupt binary data with .pdf extension degrades gracefully with error explanation."""
    corrupt_file = tmp_path / "corrupted_statement.pdf"
    corrupt_file.write_bytes(b"%PDF-1.4 CORRUPT_RANDOM_GARBAGE_BYTES\x00\xff\xfe\x12\x34\x56")

    res = extract_text_and_tables(corrupt_file)
    assert res is not None
    # Must capture error without crashing the server
    assert res["error"] is not None or res["page_count"] == 0


def test_non_existent_file_handling():
    """Verify missing file raises FileNotFoundError with explicit path message."""
    fake_path = BASE_DIR / "data" / "does_not_exist_9999.pdf"
    with pytest.raises(FileNotFoundError):
        extract_text_and_tables(fake_path)


def test_missing_all_fields_validation():
    """Verify validation engine on completely empty extracted dictionary returns clear failure."""
    empty_payload = {"document_type": "bank_statement"}
    val_report = validate_document(empty_payload)

    assert val_report["overall_status"] == "FAIL"
    assert val_report["failed_count"] >= 1
    # Check that required fields rule caught it
    req_fail = next((r for r in val_report["rules"] if r["rule_id"] == "VAL_REQ_001"), None)
    assert req_fail is not None
    assert req_fail["status"] == "FAIL"
    assert "account_number" in req_fail["details"]["missing_fields"]


def test_zero_transaction_bank_statement():
    """Verify bank statement with zero transactions reconciles without division-by-zero errors."""
    zero_tx_data = {
        "document_type": "bank_statement",
        "account_number": "1234567890",
        "opening_balance": 10000.0,
        "closing_balance": 10000.0,
        "total_deposits": 0.0,
        "total_withdrawals": 0.0,
        "transactions": []
    }
    val = validate_document(zero_tx_data)
    # Opening (10k) + 0 - 0 == Closing (10k) -> PASS
    rec_rule = next((r for r in val["rules"] if r["rule_id"] == "VAL_BNK_REC"), None)
    assert rec_rule is not None
    assert rec_rule["status"] == "PASS"

    # Review priority handles empty transaction list cleanly
    pri = evaluate_review_priority(zero_tx_data, val)
    assert pri["review_priority"] == "Low"


def test_unusual_characters_and_emojis_in_pan():
    """Verify PAN with special characters or emojis fails regulatory format check."""
    bad_pan_data = {"id_number": "ABC@#1234F"}
    results = check_identifier_formats(bad_pan_data, "pan_card")
    pan_rule = next((r for r in results if r["rule_id"] == "VAL_FMT_PAN"), None)
    assert pan_rule is not None
    assert pan_rule["status"] == "FAIL"
    assert "does not match the 10-character standard" in pan_rule["reason"]


def test_normalization_extreme_boundary_cases():
    """Verify normalizers on extreme boundary inputs."""
    assert normalize_amount(None) is None
    assert normalize_amount("") == 0.0
    assert normalize_amount("N/A") == 0.0
    assert normalize_amount("INR -5,250.75") == -5250.75

    assert normalize_date(None) is None
    assert normalize_date("") is None
    assert normalize_date("INVALID_DATE_STRING") == "INVALID_DATE_STRING"
