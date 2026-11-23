"""Unit tests for Phase 3: Flags, Review Priority, SQLite Storage, and Privacy.
Group G382: Harsh Shukla, Akshita Singh.
"""

import os
from pathlib import Path
import pytest

from findoc.flags.rules import (
    flag_median_outliers,
    flag_repeated_identical_transactions,
    flag_negative_balances,
    flag_large_cash_withdrawals,
    flag_bounced_entries,
    flag_invoice_anomalies
)
from findoc.flags.engine import evaluate_review_priority, DISCLAIMER_TEXT
from findoc.storage.db import (
    init_db,
    save_processed_document,
    get_document,
    list_documents,
    record_field_correction,
    delete_document
)
from findoc.storage.privacy import sanitize_for_logging
from findoc.extract.schemas import mask_sensitive_value


TEST_DB_PATH = Path(__file__).resolve().parent / "test_findoc.db"


@pytest.fixture(autouse=True)
def clean_test_db():
    """Setup and teardown a temporary test SQLite database."""
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    init_db(TEST_DB_PATH)
    yield
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


def test_flag_median_outlier():
    """Verify median outlier flag detects transaction significantly above median."""
    txns = [
        {"ref_no": "TXN1", "debit": 1000.0, "credit": 0.0},
        {"ref_no": "TXN2", "debit": 1200.0, "credit": 0.0},
        {"ref_no": "TXN3", "debit": 1100.0, "credit": 0.0},
        {"ref_no": "TXN4", "debit": 950.0, "credit": 0.0},
        {"ref_no": "TXN5", "debit": 45000.0, "credit": 0.0},  # Giant outlier
    ]
    flags = flag_median_outliers(txns)
    assert len(flags) == 1
    assert flags[0]["flag_id"] == "FLAG_MEDIAN_OUTLIER"
    assert flags[0]["weight"] == 15
    assert "higher than the account median" in flags[0]["reason"]


def test_flag_negative_balance_and_bounced_entry():
    """Verify negative balance and bounced transaction entry flags."""
    txns = [
        {"ref_no": "TXN1", "balance": -2500.0, "date": "2025-05-10", "description": "ECS-RETURN-INSUFFICIENT-FUNDS"},
        {"ref_no": "TXN2", "balance": 15000.0, "date": "2025-05-11", "description": "SALARY"}
    ]
    neg_flags = flag_negative_balances(txns)
    assert len(neg_flags) == 1
    assert neg_flags[0]["flag_id"] == "FLAG_NEGATIVE_BALANCE"
    assert neg_flags[0]["weight"] == 25

    bounce_flags = flag_bounced_entries(txns)
    assert len(bounce_flags) == 1
    assert bounce_flags[0]["flag_id"] == "FLAG_FAILED_BOUNCED_ENTRY"
    assert bounce_flags[0]["weight"] == 20


def test_review_priority_and_disclaimer():
    """Verify Review Priority computes weighted sum and always provides required disclaimer."""
    extracted = {
        "document_type": "bank_statement",
        "transactions": [
            {"ref_no": "TXN1", "balance": -1000.0, "debit": 30000.0, "description": "ATM CASH WITHDRAWAL"},
            {"ref_no": "TXN2", "balance": 500.0, "debit": 500.0, "description": "BOUNCE CHARGE"}
        ]
    }
    validation_fail = {
        "overall_status": "FAIL",
        "rules": [{"rule_id": "VAL_BNK_REC", "rule_name": "Balance Rec", "status": "FAIL", "reason": "Discrepancy"}]
    }

    result = evaluate_review_priority(extracted, validation_fail)
    # Check wording compliance: never "fraud score" or "credit score"
    assert "fraud score" not in str(result).lower()
    assert "credit score" not in str(result).lower()
    assert result["review_priority"] in ("Low", "Medium", "High")
    assert result["priority_score"] >= 50
    assert result["review_priority"] == "High"
    assert DISCLAIMER_TEXT in result["disclaimer"]
    assert len(result["flags"]) >= 2


def test_sqlite_storage_crud_and_corrections():
    """Verify SQLite CRUD, audit logging of corrections, and deletion."""
    doc_id = "doc_test_1001"
    ext_data = {
        "document_type": "bank_statement",
        "account_number": "123456789012",
        "closing_balance": 50000.0,
        "field_confidences": {"closing_balance": 0.95}
    }
    val_data = {"overall_status": "PASS", "passed_count": 5, "failed_count": 0, "rules": []}
    pri_data = {"review_priority": "Low", "priority_score": 10, "flags": [], "disclaimer": DISCLAIMER_TEXT}

    # 1. Save document
    save_processed_document(
        doc_id=doc_id,
        file_name="statement_may.pdf",
        doc_type="bank_statement",
        is_scanned=False,
        extracted_data=ext_data,
        validation_results=val_data,
        review_priority_results=pri_data,
        db_path=TEST_DB_PATH
    )

    # 2. Retrieve document
    doc = get_document(doc_id, db_path=TEST_DB_PATH)
    assert doc is not None
    assert doc["doc_id"] == doc_id
    assert doc["processing_status"] == "PROCESSED"
    # Ensure sensitive account number was masked in storage
    assert "XXXXXXXX9012" in doc["extracted_data"].get("account_number_masked", "")

    # 3. List documents
    docs_list = list_documents(db_path=TEST_DB_PATH)
    assert len(docs_list) == 1
    assert docs_list[0]["doc_id"] == doc_id

    # 4. Human field correction
    updated = record_field_correction(
        doc_id=doc_id,
        field_name="closing_balance",
        new_value=52000.0,
        old_value=50000.0,
        corrected_by="analyst_harsh",
        db_path=TEST_DB_PATH
    )
    assert updated["closing_balance"] == 52000.0

    reloaded = get_document(doc_id, db_path=TEST_DB_PATH)
    assert reloaded["processing_status"] == "CORRECTED"
    assert len(reloaded["corrections"]) == 1
    assert reloaded["corrections"][0]["field_name"] == "closing_balance"
    assert reloaded["corrections"][0]["old_value"] == "50000.0"
    assert reloaded["corrections"][0]["new_value"] == "52000.0"

    # 5. Privacy deletion
    deleted = delete_document(doc_id, db_path=TEST_DB_PATH)
    assert deleted is True
    assert get_document(doc_id, db_path=TEST_DB_PATH) is None


def test_privacy_sanitization():
    """Verify sanitize_for_logging strips raw sensitive values."""
    raw = {
        "document_type": "pan_card",
        "account_number": "98765432101",
        "id_number": "ABCDE1234F",
        "holder": "John Doe"
    }
    sanitized = sanitize_for_logging(raw)
    assert sanitized["account_number"] == "XXXXXXX2101"
    assert sanitized["id_number"] == "ABXXXXXX4F"
    assert sanitized["holder"] == "John Doe"
