# FinDocAI: Comprehensive Viva & Oral Defense Guide

**Capstone Course:** CSET400C Milestone-2 (Working MVP & Validation)  
**Group ID:** G382 | **Bennett University**  
**Student A:** Harsh Shukla (`E23CSEU0003`)  
**Student B:** Akshita Singh (`E23CSEU0030`)

---

## 1. The 1-Minute Elevator Pitch

> "Respected evaluators, financial institutions and small businesses process millions of bank statements, tax invoices, and KYC documents manually every day. This manual review is slow, prone to data-entry errors, and risks missing calculation discrepancies.
> 
> **FinDocAI** is an intelligent, completely offline, explainable document processing framework. It accepts PDFs and scanned images, automatically classifies the document type using both baseline keyword rules and a TF-IDF machine learning model, extracts key fields into normalized schemas, and executes rigorous rule-based validations—such as bank statement running-balance reconciliation and invoice tax math.
> 
> Unlike opaque 'black-box' AI tools, **every single warning in FinDocAI explicitly explains WHY it failed**. Furthermore, it surfaces preliminary review indicators for human review—strictly avoiding autonomous fraud or credit scoring. In our benchmark on 96 test documents, FinDocAI achieved **100% processing success at 42 ms per document**, and our key experiment empirically demonstrated that scanner degradation causes a **34.95% drop in extraction accuracy**, proving why automated confidence penalties and human-in-the-loop correction are essential."

---

## 2. The 5-Minute Evaluator Live Demo Script

| Time | Presenter | Action / Screen | What to Say to the Evaluator |
| :---: | :---: | :--- | :--- |
| **0:00 - 0:45** | **Harsh** | Open terminal, launch Streamlit via `python -m streamlit run app/main.py`. Point to the top banner. | *"Good morning. Notice first our top disclaimer banner: 'Indicators only. Human review required.' FinDocAI supports human experts; it never makes automated credit or fraud decisions. The entire pipeline runs locally on commodity hardware without any cloud API keys."* |
| **0:45 - 1:45** | **Akshita** | Click sidebar button: **'🟢 Load Clean Bank Statement'**. | *"I'm loading a clean bank statement from our test dataset. Within 50 milliseconds, our dual classifier identifies it as a Bank Statement with 100% agreement between keyword rules and our TF-IDF Logistic Regression ML model. The validation engine checks 10 rules—including running balance continuity across all transactions—and all pass with a green banner. Review Priority is 'Low' (Score: 0/100)."* |
| **1:45 - 3:00** | **Harsh** | Click sidebar button: **'🔴 Load Tampered Bank Statement'**. | *"Now observe a tampered bank statement with an injected balance mismatch. Notice immediately: Validation status flips to a prominent Red FAIL. Under rule `VAL_BNK_REC`, the system doesn't just say 'error'; it explains: 'Closing balance of INR 99,999.00 does not match calculated balance of INR 55,000.00 (Discrepancy: INR 44,999.00)'. Because of this inconsistency, the Review Priority jumps to 'High' (Score: 65/100) with contributing flags listed."* |
| **3:00 - 4:00** | **Akshita** | Navigate to **'✏️ Human Correction & Re-Validation'** tab. Edit Closing Balance back to 55,000.00 and click **'Save Corrections & Re-Validate'**. | *"This demonstrates our human-in-the-loop workflow. When a human reviewer verifies the statement and enters the correct closing balance, our system records an immutable audit log in SQLite, re-runs the validation engine instantly, and the document status updates to 'CORRECTED', flipping validation back to PASS and dropping Review Priority to Low."* |
| **4:00 - 4:40** | **Harsh** | Click sidebar button: **'📷 Load Scanned Image (OCR)'** or **'🔬 Evaluation Metrics'** tab. | *"Here is our key empirical experiment. On clean digital PDFs, field extraction achieves 87.38% accuracy. But on realistic degraded scanned PNGs with optical blur and rotation, accuracy drops to 52.43%—a 34.95% drop. To safeguard against this, FinDocAI automatically scales down confidence scores for OCR-derived inputs."* |
| **4:40 - 5:00** | **Both** | Show export button (downloaded JSON/CSV) and wrap up. | *"Finally, the reviewer exports normalized JSON or CSV for downstream accounting systems. All 29 unit tests pass, and privacy is protected by masking PAN, Aadhaar, and account numbers. We are ready for questions."* |

---

## 3. Equal Module Ownership Split

To ensure both group members can defend their individual technical contributions independently:

### Student A: Harsh Shukla (`E23CSEU0003`)
- **Document Ingestion (`ingest/`):** PyMuPDF fast text extraction, pdfplumber tabular grid parser, and graceful Tesseract OCR fallback handling.
- **Extraction Schemas (`extract/`):** Regular expression pattern matching, boundary anchors, date (`YYYY-MM-DD`) and currency amount normalizers, and privacy masking.
- **Rule-Based Validation Engine (`validate/`):** Developed all 10 validation checks (`VAL_REQ_001`, `VAL_NUM_001`, `VAL_BNK_REC`, `VAL_BNK_RUN_BAL`, `VAL_INV_TOT`, `VAL_FMT_PAN`, `VAL_FMT_AAD`, `VAL_FMT_IFSC`, `VAL_DAT_SAN`, `VAL_DUP_TXN`) with mathematical explanation generation.
- **FastAPI REST API & SQLite Storage (`api/`, `storage/`):** Implemented all REST endpoints, SQLite relational schema migrations, cascading foreign keys, and correction audit logging.

### Student B: Akshita Singh (`E23CSEU0030`)
- **Synthetic Data Generation (`generator.py`):** Authored programmatic generation of 320 PDFs with ReportLab and Faker, fixed-seed 70/30 train/test splitting, and 15% labelled tamper injections.
- **Scanner Degradation Simulation:** Implemented optical degradation pipeline using Pillow and NumPy (rotation, Gaussian blur, speckle noise) producing 40 test PNG scans.
- **Dual Classification Engine (`classify/`):** Developed dictionary keyword baseline (`rule_classifier.py`) and TF-IDF Vectorizer + Logistic Regression model (`ml_classifier.py`).
- **Flags & Review Priority (`flags/`):** Designed explainable transaction indicators (median outliers, repeated identical amounts, negative balances, cash withdrawals, bounced entries) and weighted Review Priority aggregator.
- **Streamlit Frontend & Evaluation Suite (`app/`, `evaluate.py`):** Built interactive UI with demo triggers, data editor, and executed Milestone-1 Section 12 benchmark generating all CSVs and matplotlib charts.

---

## 4. One-Line Purpose for Every Project Dependency

| Dependency | Exact One-Line Purpose for the Evaluator |
| :--- | :--- |
| `fastapi` | Provides high-performance, asynchronous REST API endpoints for document upload, validation, and export. |
| `uvicorn` | Acts as the lightweight, production-grade ASGI web server running the FastAPI backend. |
| `streamlit` | Provides an interactive, rapid-prototyping web dashboard for document review and human-in-the-loop corrections. |
| `pandas` | Handles tabular manipulation of transaction ledgers, invoice line items, and CSV export formatting. |
| `pydantic` | Enforces data validation, type hints, and standardized JSON schemas for extracted financial attributes. |
| `pymupdf` (fitz) | Extracts text, character spans, and metadata from vector digital PDFs at high speed (sub-20ms). |
| `pdfplumber` | Reconstructs geometric tabular structures and cell bounding boxes from digital bank statements. |
| `pytesseract` | Python wrapper interfacing with the open-source Tesseract OCR optical character recognition engine. |
| `pillow` (PIL) | Manipulates images, converts color spaces, and renders realistic scanner degradation effects (blur and rotation). |
| `scikit-learn` | Powers TF-IDF text feature extraction and Logistic Regression classification for document categorization. |
| `reportlab` | Programmatically draws high-quality synthetic financial PDFs with custom fonts, tables, and colors. |
| `faker` | Generates realistic synthetic names, addresses, transaction narratives, and company names. |
| `python-multipart` | Parses multipart form data enabling file uploads in FastAPI endpoints. |
| `httpx` | Asynchronous HTTP client required by Starlette/FastAPI's TestClient for automated endpoint testing. |
| `matplotlib` | Generates publication-ready evaluation charts (confusion matrices and accuracy comparison bars) in `results/`. |
| `pytest` | Executes automated unit and integration tests across the pipeline and generates test reports. |

---

## 5. 25 Likely Evaluator Questions with Crisp, Defendable Answers

### Q1: Why did you use synthetic data instead of real financial documents?
**Answer:** Real financial documents contain confidential PII and proprietary banking data protected under privacy laws (RBI guidelines and DPDP Act). Synthetic data with Faker and ReportLab allows us to establish exact, verifiable ground truth for every field and inject controlled, labelled tamper faults (~15%) without ethical or privacy violations.

### Q2: Why use a rule-based validation engine instead of an end-to-end deep learning model?
**Answer:** Financial audits require 100% deterministic explainability. If an invoice total is wrong, an auditor needs to see the exact arithmetic: `Subtotal + Tax != Total`. Deep learning models are probabilistic black boxes that can hallucinate and cannot mathematically guarantee arithmetic reconciliation.

### Q3: Why didn't you use LayoutLM or modern vision-language models?
**Answer:** LayoutLM requires heavy GPU compute, multi-gigabyte model weights, and cloud infrastructure. Our project constraint was a lightweight, offline MVP that runs in under 50 ms on any standard student laptop while remaining completely explainable to evaluators.

### Q4: Why did you avoid cloud OCR services like AWS Textract or Google Cloud Document AI?
**Answer:** Cloud OCR services violate our local offline constraint, introduce paid per-page API costs, and require transmitting sensitive financial documents over the external internet. We prioritized open-source Tesseract OCR and PyMuPDF to guarantee zero cost and data residency.

### Q5: Why is Machine Learning used ONLY for document classification and not extraction?
**Answer:** Document classification is an open-vocabulary semantic task where TF-IDF n-grams excels at distinguishing vocabulary differences between a bank statement and an invoice. In contrast, extraction requires exact field boundaries and numbers where regex and positional anchors provide deterministic precision.

### Q6: Why do you strictly avoid the terms "fraud score" or "credit score"?
**Answer:** Milestone-1 and ethical AI principles (NIST AI RMF) mandate that the system must never make autonomous legal, fraud, or credit decisions. We output 'Review Priority (Low/Medium/High)' and 'Indicators' to empower human reviewers, accompanied by our mandatory disclaimer: *"Indicators only. Human review required."*

### Q7: How does your bank statement running balance reconciliation work?
**Answer:** Rule `VAL_BNK_REC` verifies two levels: first, `Opening Balance + Total Deposits - Total Withdrawals == Closing Balance` (within 0.05 tolerance). Second, `VAL_BNK_RUN_BAL` iterates transaction-by-transaction: `Previous Balance + Credit - Debit == Stated Balance`. Any break immediately flags the exact transaction and discrepancy.

### Q8: What was your key empirical finding in the Digital PDF vs Scanned OCR experiment?
**Answer:** On clean digital PDFs, field-level extraction achieved **87.38%** accuracy, but dropped to **52.43%** on degraded scans (a **-34.95%** drop). Optical blur and slight tilt cause OCR character confusion (e.g., mistaking '.' for commas or dropping digits), empirically demonstrating why OCR inputs require confidence penalties and human review.

### Q9: How does the system handle corrupt or empty files?
**Answer:** Ingestion functions are wrapped in defensive handlers that detect zero-byte files, invalid extensions, or malformed bytes, returning HTTP 400/422 status codes and friendly error messages rather than crashing the server (verified in TC-20 through TC-25).

### Q10: How does your human-in-the-loop correction workflow work?
**Answer:** In Streamlit or via `PUT /documents/{id}/corrections`, a reviewer edits any flawed value. FinDocAI records an immutable audit log in SQLite with the old value, new value, reviewer ID, and timestamp, immediately re-runs validation rules, updates Review Priority, and marks the record as `CORRECTED`.

### Q11: How do you enforce privacy and data minimization?
**Answer:** Rule `mask_sensitive_value` masks PAN numbers (e.g., `ABXXXXXX4F`), Aadhaar numbers (`XXXX XXXX 1234`), and bank accounts before writing to SQLite or displaying in logs. Additionally, `delete_document` provides a right-to-be-forgotten deletion feature.

### Q12: How did you ensure 70/30 train/test split reproducibility?
**Answer:** In `generator.py`, we set a fixed global random seed (`RANDOM_SEED = 42`) across Python `random`, `numpy`, and `Faker`. The split indexes 224 training documents and 96 test documents deterministically into `data/dataset_manifest.json`.

### Q13: Why does your clean document false-positive rate reach ~60% in evaluation?
**Answer:** Because our statistical outlier rule (`FLAG_MEDIAN_OUTLIER`) flags legitimate high-value transactions (such as quarterly tax payments or salary transfers) as indicators for reviewer inspection. This is deliberate: in financial audit, high recall is prioritized over precision so no suspicious transaction escapes notice.

### Q14: How does FinDocAI align with Sustainable Development Goal 9 (SDG 9)?
**Answer:** SDG 9 focuses on Industry, Innovation, and Infrastructure. FinDocAI provides open-source, accessible digital infrastructure that automates repetitive financial paperwork, upgrading technological capabilities for small enterprises without expensive software licenses.

### Q15: How does FinDocAI align with SDG 8 (Decent Work)?
**Answer:** SDG 8 promotes productive employment and decent work. By eliminating tedious manual verification and data entry, FinDocAI reduces cognitive fatigue and human error, allowing accountants and analysts to focus on higher-value advisory tasks.

### Q16: How would this architecture scale to real-world messy documents?
**Answer:** By implementing a template registry: each enterprise vendor's layout is registered with its specific anchor offsets. For un-templated documents, a lightweight layout model (like quantized LayoutLM ONNX) can serve as a fallback extractor.

### Q17: What is the purpose of field-level confidence scores?
**Answer:** Every extracted field receives a score: 0.95 for direct regex matches, 0.75 for fallback patterns, and a 0.85 multiplier penalty if derived from OCR. This visually alerts the human reviewer in Streamlit to focus their manual scrutiny on low-confidence fields.

### Q18: What is your database structure and why SQLite?
**Answer:** SQLite is serverless, zero-configuration, and ACID-compliant, ideal for local standalone prototypes. We designed relational tables for `documents`, `extracted_data`, `validations`, `review_flags`, and `corrections` with cascading foreign keys.

### Q19: What happens if Tesseract OCR is not installed on the evaluator's laptop?
**Answer:** The system checks PATH and common Windows install directories via `check_tesseract_installed()`. If missing, it prints exact UB-Mannheim download instructions, skips OCR execution, and continues processing digital PDFs without crashing.

### Q20: What are the primary failure modes of the regex extractor?
**Answer:** Multi-line invoice descriptions that wrap across lines, non-standard date formats (e.g., Hijri or Julian calendars), and skewed scanned tables where OCR merges columns together.

### Q21: How do you detect duplicate transactions?
**Answer:** Rule `VAL_DUP_TXN` hashes transaction reference numbers (`ref_no`). If duplicate reference numbers appear with identical amounts and dates in the same statement, the rule triggers a failure.

### Q22: How do you calculate Review Priority?
**Answer:** It is a transparent weighted sum of contributing flags: Validation failures (+35), Negative balances (+25), Bounced entries (+20), Median outliers (+15), and Repeated amounts (+15). Capped at 100: Score < 20 is Low, 20–50 is Medium, >= 50 is High.

### Q23: Why did both baseline rules and ML achieve 100% classification accuracy?
**Answer:** Financial documents have highly distinct lexical vocabularies. Bank statements heavily feature words like *'deposit'*, *'IFSC'*, *'balance'*; invoices feature *'GSTIN'*, *'subtotal'*, *'due date'*; and KYC documents feature *'Income Tax'* or *'UIDAI'*. Both keyword sets and TF-IDF vectors separate them cleanly.

### Q24: What are the key limitations of your Milestone-2 MVP?
**Answer:** Lack of support for multi-page balance sheets, inability to perform cross-document reconciliation (e.g. matching an invoice to a bank debit), and reliance on standard templates rather than general-purpose vision models.

### Q25: What is the single most important lesson learned during this project?
**Answer:** That in financial AI systems, **transparency and explainability are more important than algorithmic complexity**. An auditor will never trust an opaque 99% accuracy claim, but they will readily adopt an assistant that highlights the exact line where numbers fail to add up.
