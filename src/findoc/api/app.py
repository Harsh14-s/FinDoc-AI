"""FastAPI Application Endpoints for FinDocAI.

Provides REST API routes for:
- POST /upload: Upload PDF or image, run pipeline, return extracted data + validation + review flags.
- GET /documents: List all processed documents.
- GET /documents/{id}: Retrieve full document details, confidences, rules, and history.
- PUT /documents/{id}/corrections: Human-in-the-loop field correction and instant re-validation.
- GET /documents/{id}/export: Export reviewed data in JSON or CSV format.
- DELETE /documents/{id}: Privacy deletion of document records.
Group G382: Harsh Shukla, Akshita Singh.
"""

import os
import io
import csv
import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel

from fastapi import FastAPI, UploadFile, File, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from findoc.ingest.pdf_parser import extract_text_and_tables
from findoc.classify.classifier_service import classify_document
from findoc.extract.extractor_service import extract_document
from findoc.validate.validator import validate_document
from findoc.flags.engine import evaluate_review_priority, DISCLAIMER_TEXT
from findoc.storage.db import (
    init_db,
    save_processed_document,
    get_document,
    list_documents,
    record_field_correction,
    delete_document
)
from findoc.storage.privacy import delete_document_record


# Ensure storage is initialized
init_db()

app = FastAPI(
    title="FinDocAI API",
    description="Intelligent Financial Document Extraction, Validation and Risk Insights API",
    version="1.0.0"
)

# Enable CORS for local Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_TEMP_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "uploads"
UPLOAD_TEMP_DIR.mkdir(parents=True, exist_ok=True)


class CorrectionPayload(BaseModel):
    field_name: str
    new_value: Any
    old_value: Optional[Any] = None
    corrected_by: Optional[str] = "reviewer"


@app.get("/")
def root():
    """Health check and API root metadata."""
    return {
        "project": "FinDocAI",
        "description": "Financial Document Extraction, Validation and Risk Insights",
        "status": "online",
        "disclaimer": DISCLAIMER_TEXT
    }


@app.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a financial document (PDF or scanned image).

    Executes full pipeline: Ingest -> Classify -> Extract -> Validate -> Flags & Review Priority -> Store.
    """
    allowed_exts = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{file_ext}'. Allowed formats: PDF, PNG, JPG, JPEG, TIFF."
        )

    doc_id = f"doc_{uuid.uuid4().hex[:10]}"
    temp_file_path = UPLOAD_TEMP_DIR / f"{doc_id}_{file.filename}"

    try:
        # Save file to disk
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes).")

        with open(temp_file_path, "wb") as f:
            f.write(contents)

        # 1. Ingest
        parsed = extract_text_and_tables(temp_file_path)
        if parsed.get("error"):
            # Handle corrupt file gracefully
            save_processed_document(
                doc_id=doc_id,
                file_name=file.filename,
                doc_type="unknown",
                is_scanned=parsed.get("is_scanned", False),
                extracted_data={},
                validation_results={"overall_status": "ERROR", "rules": []},
                review_priority_results={"review_priority": "High", "flags": [], "disclaimer": DISCLAIMER_TEXT},
                processing_status="ERROR",
                error_message=parsed["error"]
            )
            return JSONResponse(
                status_code=422,
                content={
                    "doc_id": doc_id,
                    "status": "ERROR",
                    "error": parsed["error"],
                    "install_instructions": parsed.get("install_instructions", "")
                }
            )

        # 2. Classify (Baseline Rules + TF-IDF ML)
        classification = classify_document(parsed["text"])
        doc_type = classification["final_prediction"]

        # 3. Extract Normalized Schema
        extracted_data = extract_document(doc_type, parsed)

        # 4. Validate Predefined Rules
        validation = validate_document(extracted_data)

        # 5. Evaluate Flags and Review Priority
        review_priority = evaluate_review_priority(extracted_data, validation)

        # 6. Persist to SQLite
        save_processed_document(
            doc_id=doc_id,
            file_name=file.filename,
            doc_type=doc_type,
            is_scanned=parsed["is_scanned"],
            extracted_data=extracted_data,
            validation_results=validation,
            review_priority_results=review_priority,
            processing_status="PROCESSED"
        )

        return {
            "doc_id": doc_id,
            "file_name": file.filename,
            "document_type": doc_type,
            "classification": classification,
            "is_scanned": parsed["is_scanned"],
            "ocr_used": parsed["ocr_used"],
            "install_instructions": parsed.get("install_instructions", ""),
            "extracted_data": extracted_data,
            "validation": validation,
            "review_priority": review_priority,
            "disclaimer": DISCLAIMER_TEXT
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal processing failure: {str(e)}")
    finally:
        # Keep uploaded file or clean up if needed
        pass


@app.get("/documents")
def get_documents_list(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    """Retrieve list of processed documents with status, validation, and review priority summaries."""
    docs = list_documents(limit=limit, offset=offset)
    return {
        "count": len(docs),
        "limit": limit,
        "offset": offset,
        "documents": docs
    }


@app.get("/documents/{doc_id}")
def get_single_document(doc_id: str):
    """Retrieve full details of a single document including extracted fields and review flags."""
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document with ID '{doc_id}' not found.")
    return doc


@app.put("/documents/{doc_id}/corrections")
def update_document_field(doc_id: str, payload: CorrectionPayload):
    """Human-in-the-loop field correction: updates field value, re-runs validation and review priority."""
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")

    old_val = payload.old_value
    if old_val is None:
        old_val = doc["extracted_data"].get(payload.field_name)

    # 1. Record correction audit trail and update stored JSON
    updated_extracted = record_field_correction(
        doc_id=doc_id,
        field_name=payload.field_name,
        new_value=payload.new_value,
        old_value=old_val,
        corrected_by=payload.corrected_by or "reviewer"
    )

    # 2. Re-run validation with corrected data
    re_validation = validate_document(updated_extracted)

    # 3. Re-evaluate Review Priority with updated validation
    re_review_priority = evaluate_review_priority(updated_extracted, re_validation)

    # 4. Save updated results to database
    save_processed_document(
        doc_id=doc_id,
        file_name=doc["file_name"],
        doc_type=doc["doc_type"],
        is_scanned=doc["is_scanned"],
        extracted_data=updated_extracted,
        validation_results=re_validation,
        review_priority_results=re_review_priority,
        processing_status="CORRECTED"
    )

    return {
        "doc_id": doc_id,
        "field_corrected": payload.field_name,
        "old_value": old_val,
        "new_value": payload.new_value,
        "validation": re_validation,
        "review_priority": re_review_priority,
        "message": f"Field '{payload.field_name}' successfully updated. Validation and Review Priority re-calculated."
    }


@app.get("/documents/{doc_id}/export")
def export_document(doc_id: str, format: str = Query("json", pattern="^(json|csv)$")):
    """Export reviewed document data and validation insights in JSON or CSV format."""
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")

    if format.lower() == "json":
        export_payload = {
            "export_metadata": {
                "system": "FinDocAI",
                "version": "1.0.0",
                "exported_doc_id": doc_id,
                "disclaimer": DISCLAIMER_TEXT
            },
            "document": doc
        }
        return JSONResponse(content=export_payload)

    else:  # CSV format
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["FinDocAI Document Export", doc_id])
        writer.writerow(["Disclaimer", DISCLAIMER_TEXT])
        writer.writerow([])

        # Header summary
        writer.writerow(["Document Type", doc.get("doc_type")])
        writer.writerow(["File Name", doc.get("file_name")])
        writer.writerow(["Processing Status", doc.get("processing_status")])
        writer.writerow(["Review Priority", doc["review_priority"].get("review_priority")])
        writer.writerow(["Validation Status", doc["validation"].get("overall_status")])
        writer.writerow([])

        # Extracted fields
        writer.writerow(["--- EXTRACTED FIELDS ---", "VALUE", "CONFIDENCE"])
        for k, v in doc.get("extracted_data", {}).items():
            if k not in ("transactions", "line_items", "field_confidences"):
                conf = doc.get("field_confidences", {}).get(k, "N/A")
                writer.writerow([k, str(v), str(conf)])
        writer.writerow([])

        # If bank statement transactions exist
        txns = doc.get("extracted_data", {}).get("transactions", [])
        if txns:
            writer.writerow(["--- TRANSACTIONS ---"])
            writer.writerow(["Date", "Description", "Ref No", "Debit", "Credit", "Balance"])
            for t in txns:
                writer.writerow([t.get("date"), t.get("description"), t.get("ref_no"), t.get("debit"), t.get("credit"), t.get("balance")])
            writer.writerow([])

        # If invoice line items exist
        items = doc.get("extracted_data", {}).get("line_items", [])
        if items:
            writer.writerow(["--- INVOICE LINE ITEMS ---"])
            writer.writerow(["Description", "Quantity", "Unit Price", "Total"])
            for it in items:
                writer.writerow([it.get("description"), it.get("quantity"), it.get("unit_price"), it.get("total")])
            writer.writerow([])

        # Validation rules summary
        writer.writerow(["--- VALIDATION RULES ---"])
        writer.writerow(["Rule ID", "Status", "Reason"])
        for r in doc["validation"].get("rules", []):
            writer.writerow([r.get("rule_id"), r.get("status"), r.get("reason")])

        csv_content = output.getvalue()
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=findoc_export_{doc_id}.csv"}
        )


@app.delete("/documents/{doc_id}")
def delete_doc(doc_id: str):
    """Delete document for privacy and compliance."""
    res = delete_document_record(doc_id)
    if not res["deleted"]:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
    return res
