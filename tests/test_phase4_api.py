"""Unit and Integration Tests for Phase 4: FastAPI Endpoints.

Tests document upload, error handling, corrections re-validation, export, and deletion.
Group G382: Harsh Shukla, Akshita Singh.
"""

import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from findoc.api.app import app
from findoc.flags.engine import DISCLAIMER_TEXT

client = TestClient(app)
BASE_DIR = Path(__file__).resolve().parent.parent


def test_api_root_health():
    """Verify API root endpoint returns status online and required disclaimer."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert DISCLAIMER_TEXT in data["disclaimer"]


def test_api_upload_unsupported_extension():
    """Verify upload fails gracefully with 400 when file extension is unsupported."""
    response = client.post(
        "/upload",
        files={"file": ("test_unsupported.xyz", b"dummy content", "text/plain")}
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_api_upload_empty_file():
    """Verify upload fails gracefully with 400 when uploaded file is empty."""
    response = client.post(
        "/upload",
        files={"file": ("empty.pdf", b"", "application/pdf")}
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"]


def test_api_full_document_lifecycle():
    """Verify full REST workflow: upload PDF -> get by ID -> list -> correction -> export -> delete."""
    manifest_path = BASE_DIR / "data" / "dataset_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Use first test bank statement
    sample = manifest["test"][0]
    pdf_path = BASE_DIR / sample["pdf_path"]

    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    # 1. POST /upload
    upload_resp = client.post(
        "/upload",
        files={"file": (pdf_path.name, file_bytes, "application/pdf")}
    )
    assert upload_resp.status_code == 201
    upload_data = upload_resp.json()
    doc_id = upload_data["doc_id"]
    assert doc_id.startswith("doc_")
    assert upload_data["document_type"] in ("bank_statement", "invoice", "pan_card", "aadhaar_card")
    assert "validation" in upload_data
    assert "review_priority" in upload_data
    assert DISCLAIMER_TEXT in upload_data["disclaimer"]

    # 2. GET /documents
    list_resp = client.get("/documents?limit=10")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["count"] >= 1
    assert any(d["doc_id"] == doc_id for d in list_data["documents"])

    # 3. GET /documents/{doc_id}
    detail_resp = client.get(f"/documents/{doc_id}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["doc_id"] == doc_id
    assert "extracted_data" in detail_data

    # 4. PUT /documents/{doc_id}/corrections (Human-in-the-loop update)
    corr_payload = {
        "field_name": "closing_balance",
        "new_value": 75000.0,
        "old_value": detail_data["extracted_data"].get("closing_balance", 0.0),
        "corrected_by": "evaluator_test"
    }
    corr_resp = client.put(f"/documents/{doc_id}/corrections", json=corr_payload)
    assert corr_resp.status_code == 200
    corr_data = corr_resp.json()
    assert corr_data["new_value"] == 75000.0
    assert "validation" in corr_data
    assert "review_priority" in corr_data

    # 5. GET /documents/{doc_id}/export?format=json
    exp_json_resp = client.get(f"/documents/{doc_id}/export?format=json")
    assert exp_json_resp.status_code == 200
    assert exp_json_resp.json()["export_metadata"]["system"] == "FinDocAI"

    # 6. GET /documents/{doc_id}/export?format=csv
    exp_csv_resp = client.get(f"/documents/{doc_id}/export?format=csv")
    assert exp_csv_resp.status_code == 200
    assert "text/csv" in exp_csv_resp.headers["content-type"]
    assert "FinDocAI Document Export" in exp_csv_resp.text

    # 7. DELETE /documents/{doc_id}
    del_resp = client.delete(f"/documents/{doc_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["deleted"] is True

    # Confirm 404 after deletion
    get_after_del = client.get(f"/documents/{doc_id}")
    assert get_after_del.status_code == 404
