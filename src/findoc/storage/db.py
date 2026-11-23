"""SQLite Storage and Audit Persistence for FinDocAI.

Stores document records, extracted fields (with masked sensitive identifiers),
validation rule results, explainable review priority flags, and human correction history.
Group G382: Harsh Shukla, Akshita Singh.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from findoc.extract.schemas import mask_sensitive_value

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "findoc.db"


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Create a connection with foreign keys enabled."""
    path = db_path or DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[Path] = None):
    """Initialize database tables with schema migrations."""
    conn = get_connection(db_path)
    with conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            doc_id TEXT PRIMARY KEY,
            file_name TEXT NOT NULL,
            doc_type TEXT NOT NULL,
            is_scanned BOOLEAN DEFAULT 0,
            processing_status TEXT NOT NULL,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS extracted_data (
            doc_id TEXT PRIMARY KEY,
            data_json TEXT NOT NULL,
            confidences_json TEXT NOT NULL,
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS validations (
            doc_id TEXT PRIMARY KEY,
            overall_status TEXT NOT NULL,
            passed_count INTEGER NOT NULL,
            failed_count INTEGER NOT NULL,
            rules_json TEXT NOT NULL,
            validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS review_flags (
            doc_id TEXT PRIMARY KEY,
            review_priority TEXT NOT NULL,
            priority_score INTEGER NOT NULL,
            flags_json TEXT NOT NULL,
            disclaimer TEXT NOT NULL,
            flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS corrections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id TEXT NOT NULL,
            field_name TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            corrected_by TEXT DEFAULT 'reviewer',
            corrected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE
        );
        """)
    conn.close()


def save_processed_document(
    doc_id: str,
    file_name: str,
    doc_type: str,
    is_scanned: bool,
    extracted_data: Dict[str, Any],
    validation_results: Dict[str, Any],
    review_priority_results: Dict[str, Any],
    processing_status: str = "PROCESSED",
    error_message: Optional[str] = None,
    db_path: Optional[Path] = None
) -> str:
    """Atomically persist complete document processing lifecycle records."""
    conn = get_connection(db_path)
    now = datetime.now().isoformat()

    # Apply privacy masking to sensitive fields before storage
    safe_data = dict(extracted_data)
    if "account_number" in safe_data and safe_data["account_number"]:
        safe_data["account_number_masked"] = mask_sensitive_value(safe_data["account_number"], "account")
    if safe_data.get("document_type") == "pan_card" and safe_data.get("id_number"):
        safe_data["id_number_masked"] = mask_sensitive_value(safe_data["id_number"], "pan")
    if safe_data.get("document_type") == "aadhaar_card" and safe_data.get("id_number"):
        safe_data["id_number_masked"] = mask_sensitive_value(safe_data["id_number"], "aadhaar")

    confidences = safe_data.pop("field_confidences", {})

    with conn:
        conn.execute("""
            INSERT OR REPLACE INTO documents 
            (doc_id, file_name, doc_type, is_scanned, processing_status, error_message, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (doc_id, file_name, doc_type, 1 if is_scanned else 0, processing_status, error_message, now))

        conn.execute("""
            INSERT OR REPLACE INTO extracted_data (doc_id, data_json, confidences_json, extracted_at)
            VALUES (?, ?, ?, ?)
        """, (doc_id, json.dumps(safe_data), json.dumps(confidences), now))

        conn.execute("""
            INSERT OR REPLACE INTO validations (doc_id, overall_status, passed_count, failed_count, rules_json, validated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            doc_id,
            validation_results.get("overall_status", "UNKNOWN"),
            validation_results.get("passed_count", 0),
            validation_results.get("failed_count", 0),
            json.dumps(validation_results.get("rules", [])),
            now
        ))

        conn.execute("""
            INSERT OR REPLACE INTO review_flags (doc_id, review_priority, priority_score, flags_json, disclaimer, flagged_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            doc_id,
            review_priority_results.get("review_priority", "Low"),
            review_priority_results.get("priority_score", 0),
            json.dumps(review_priority_results.get("flags", [])),
            review_priority_results.get("disclaimer", ""),
            now
        ))

    conn.close()
    return doc_id


def get_document(doc_id: str, db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Retrieve full details of a processed document."""
    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.execute("SELECT * FROM documents WHERE doc_id = ?", (doc_id,))
    doc_row = cur.fetchone()
    if not doc_row:
        conn.close()
        return None

    cur.execute("SELECT * FROM extracted_data WHERE doc_id = ?", (doc_id,))
    ext_row = cur.fetchone()

    cur.execute("SELECT * FROM validations WHERE doc_id = ?", (doc_id,))
    val_row = cur.fetchone()

    cur.execute("SELECT * FROM review_flags WHERE doc_id = ?", (doc_id,))
    flg_row = cur.fetchone()

    cur.execute("SELECT * FROM corrections WHERE doc_id = ? ORDER BY corrected_at DESC", (doc_id,))
    corr_rows = cur.fetchall()

    conn.close()

    return {
        "doc_id": doc_row["doc_id"],
        "file_name": doc_row["file_name"],
        "doc_type": doc_row["doc_type"],
        "is_scanned": bool(doc_row["is_scanned"]),
        "processing_status": doc_row["processing_status"],
        "error_message": doc_row["error_message"],
        "created_at": doc_row["created_at"],
        "updated_at": doc_row["updated_at"],
        "extracted_data": json.loads(ext_row["data_json"]) if ext_row else {},
        "field_confidences": json.loads(ext_row["confidences_json"]) if ext_row else {},
        "validation": {
            "overall_status": val_row["overall_status"] if val_row else "UNKNOWN",
            "passed_count": val_row["passed_count"] if val_row else 0,
            "failed_count": val_row["failed_count"] if val_row else 0,
            "rules": json.loads(val_row["rules_json"]) if val_row else []
        },
        "review_priority": {
            "review_priority": flg_row["review_priority"] if flg_row else "Low",
            "priority_score": flg_row["priority_score"] if flg_row else 0,
            "flags": json.loads(flg_row["flags_json"]) if flg_row else [],
            "disclaimer": flg_row["disclaimer"] if flg_row else ""
        },
        "corrections": [dict(r) for r in corr_rows]
    }


def list_documents(limit: int = 100, offset: int = 0, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """List documents with processing status and review priority."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT d.doc_id, d.file_name, d.doc_type, d.is_scanned, d.processing_status,
               v.overall_status, rf.review_priority, rf.priority_score, d.created_at
        FROM documents d
        LEFT JOIN validations v ON d.doc_id = v.doc_id
        LEFT JOIN review_flags rf ON d.doc_id = rf.doc_id
        ORDER BY d.created_at DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def record_field_correction(
    doc_id: str,
    field_name: str,
    new_value: Any,
    old_value: Any,
    corrected_by: str = "reviewer",
    db_path: Optional[Path] = None
) -> Dict[str, Any]:
    """Record an audit entry for a human correction and update the stored extracted data."""
    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.execute("SELECT data_json FROM extracted_data WHERE doc_id = ?", (doc_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise ValueError(f"Document {doc_id} not found in database")

    data = json.loads(row["data_json"])
    data[field_name] = new_value

    with conn:
        # 1. Insert audit trail
        conn.execute("""
            INSERT INTO corrections (doc_id, field_name, old_value, new_value, corrected_by)
            VALUES (?, ?, ?, ?, ?)
        """, (doc_id, field_name, str(old_value), str(new_value), corrected_by))

        # 2. Update extracted data
        conn.execute("""
            UPDATE extracted_data SET data_json = ?, extracted_at = CURRENT_TIMESTAMP WHERE doc_id = ?
        """, (json.dumps(data), doc_id))

        # 3. Update document status
        conn.execute("""
            UPDATE documents SET processing_status = 'CORRECTED', updated_at = CURRENT_TIMESTAMP WHERE doc_id = ?
        """, (doc_id,))

    conn.close()
    return data


def delete_document(doc_id: str, db_path: Optional[Path] = None) -> bool:
    """Delete document and all associated records from SQLite database for privacy compliance."""
    conn = get_connection(db_path)
    with conn:
        cur = conn.execute("DELETE FROM documents WHERE doc_id = ?", (doc_id,))
        deleted = cur.rowcount > 0
    conn.close()
    return deleted
