# FinDocAI: Requirements Traceability, Test Suite & Risk Analysis

**Course:** CSET400C Capstone Project, Milestone-2  
**Group ID:** G382 | **Authors:** Harsh Shukla (`E23CSEU0003`) & Akshita Singh (`E23CSEU0030`)

---

## 1. Finalized Requirements Specification

### Functional Requirements (FR)
- **FR-01 (Multi-Format Ingestion):** The system shall accept digital vector PDFs and scanned raster images (PNG/JPG), automatically detecting whether digital extraction or OCR is required.
- **FR-02 (Dual-Engine Classification):** The system shall identify document category (Bank Statement, Invoice, PAN, Aadhaar) using both a rule-based keyword baseline and a trained TF-IDF + Logistic Regression ML classifier.
- **FR-03 (Structured Schema Normalization):** The system shall extract financial attributes into normalized schemas with standardized ISO-8601 dates (`YYYY-MM-DD`), numeric currency amounts, and per-field confidences.
- **FR-04 (Explainable Arithmetic Validation):** The system shall validate arithmetic invariants (Opening + Deposits - Withdrawals = Closing, Subtotal + Tax = Total), line-item sums, regulatory formats (PAN, Aadhaar, IFSC, GSTIN), and date sanity, returning an explicit Rule ID and plain-English explanation for every failure.
- **FR-05 (Transparent Review Priority):** The system shall compute an explainable Review Priority (**Low**, **Medium**, **High**) based on a weighted sum of triggered indicators, explicitly avoiding autonomous fraud or credit scoring.
- **FR-06 (Human-in-the-Loop Correction):** The system shall enable reviewers to modify extracted values, maintain an immutable audit trail, and immediately re-trigger validation and review priority recalculation.
- **FR-07 (Data Export):** The system shall export audited document records in normalized JSON and standardized CSV formats.
- **FR-08 (Privacy & Data Minimization):** The system shall mask sensitive identifiers (PAN, Aadhaar, Bank Accounts) prior to database persistence and provide a right-to-be-forgotten document deletion function.

### Non-Functional Requirements (NFR)
- **NFR-01 (Local & Offline):** The pipeline shall operate completely on local student hardware with zero external cloud API keys, paid services, or network calls.
- **NFR-02 (High Processing Throughput):** The system shall process supported digital documents in under 150 ms per document on commodity hardware.
- **NFR-03 (Graceful Degradation):** In the absence of system Tesseract OCR binaries, the system shall provide clear install instructions and degrade gracefully without crashing.
- **NFR-04 (Code Transparency & Explainability):** Every function shall possess concise docstrings and clear logic suitable for personal defense by 3rd-year engineering students.

---

## 2. Test-Case Traceability Matrix (All 29 Passed Tests)

| Test ID | Test Function Name | Module Tested | Requirement Traced | Description & Expected Outcome | Status |
| :---: | :--- | :--- | :---: | :--- | :---: |
| **TC-01** | `test_directory_structure_exists` | Skeleton | NFR-01 | Verifies all required data, src, tests, results directories exist | **PASS** |
| **TC-02** | `test_dataset_manifest_and_counts` | Generator | FR-01 | Verifies 320 synthetic docs with 70/30 split and ~15% tampered ratio | **PASS** |
| **TC-03** | `test_pdf_and_ground_truth_pairing` | Generator | FR-01 | Confirms every PDF has valid paired ground truth JSON metadata | **PASS** |
| **TC-04** | `test_degraded_scans_are_valid_images`| Generator | FR-01 | Verifies 40 degraded scan PNGs exist with blur, rotation, and noise | **PASS** |
| **TC-05** | `test_tesseract_graceful_check` | Ingestion | NFR-03 | Verifies missing OCR returns instructions without unhandled crash | **PASS** |
| **TC-06** | `test_ingest_digital_pdf` | Ingestion | FR-01 | Tests PyMuPDF digital text and table extraction | **PASS** |
| **TC-07** | `test_baseline_and_ml_classification`| Classify | FR-02 | Verifies keyword rules & ML classifier predict 4 document classes | **PASS** |
| **TC-08** | `test_normalization_and_masking` | Schemas | FR-03, FR-08 | Verifies date, currency normalizers and PAN/Aadhaar/Account masking | **PASS** |
| **TC-09** | `test_clean_bank_statement_validation`| Validate | FR-04 | Confirms clean bank statement passes all 10 validation rules | **PASS** |
| **TC-10** | `test_tampered_bank_balance_fails` | Validate | FR-04 | Verifies balance mismatch triggers `VAL_BNK_REC` with exact reason | **PASS** |
| **TC-11** | `test_tampered_invoice_total_fails` | Validate | FR-04 | Verifies invoice mismatch triggers `VAL_INV_TOT` with exact discrepancy | **PASS** |
| **TC-12** | `test_invalid_pan_and_aadhaar_rules` | Validate | FR-04 | Tests format rules `VAL_FMT_PAN` and `VAL_FMT_AAD` on invalid inputs | **PASS** |
| **TC-13** | `test_date_sanity_and_duplicates` | Validate | FR-04 | Confirms detection of future dates and duplicate reference IDs | **PASS** |
| **TC-14** | `test_flag_median_outlier` | Flags | FR-05 | Verifies outlier transaction (>3.5x median) triggers weighted flag | **PASS** |
| **TC-15** | `test_flag_negative_and_bounced` | Flags | FR-05 | Tests negative balance and bounced entry indicator flags | **PASS** |
| **TC-16** | `test_review_priority_and_disclaimer`| Flags | FR-05 | Verifies weighted score maps to High priority and includes disclaimer | **PASS** |
| **TC-17** | `test_sqlite_storage_and_corrections`| Storage | FR-06, FR-08 | Tests SQLite persistence, human correction audit, and deletion | **PASS** |
| **TC-18** | `test_privacy_sanitization` | Privacy | FR-08 | Confirms `sanitize_for_logging` strips raw PII from logs | **PASS** |
| **TC-19** | `test_api_root_health` | API | NFR-02 | Verifies FastAPI health check endpoint returns 200 OK & disclaimer | **PASS** |
| **TC-20** | `test_api_upload_unsupported_ext` | API | NFR-03 | Tests that uploading `.xyz` file returns friendly 400 Bad Request | **PASS** |
| **TC-21** | `test_api_upload_empty_file` | API | NFR-03 | Tests that uploading 0-byte file returns 400 with explanation | **PASS** |
| **TC-22** | `test_api_full_document_lifecycle` | API | FR-01 - FR-07| Tests complete REST API upload, GET, PUT correction, export, delete | **PASS** |
| **TC-23** | `test_empty_file_handling` | Robustness | NFR-03 | Edge case: empty PDF handled cleanly by parser | **PASS** |
| **TC-24** | `test_corrupt_file_handling` | Robustness | NFR-03 | Edge case: corrupt binary garbage bytes captured with error message | **PASS** |
| **TC-25** | `test_non_existent_file_handling` | Robustness | NFR-03 | Edge case: non-existent file path raises FileNotFoundError cleanly | **PASS** |
| **TC-26** | `test_missing_all_fields_validation`| Robustness | FR-04 | Edge case: empty dictionary input flags `VAL_REQ_001` failure | **PASS** |
| **TC-27** | `test_zero_transaction_bank_statement`| Robustness | FR-04 | Edge case: bank statement with 0 transactions avoids division-by-zero | **PASS** |
| **TC-28** | `test_unusual_characters_in_pan` | Robustness | FR-04 | Edge case: PAN with symbols/emojis fails format check | **PASS** |
| **TC-29** | `test_normalization_boundary_cases` | Robustness | FR-03 | Edge case: extreme negative values and invalid date strings | **PASS** |

---

## 3. Real Empirical Evaluation Results (Benchmarked on 96 Test Documents)

All values below were experimentally measured and saved to `results/`:

| Evaluation Dimension | Benchmark Metric | Measured Value | Analysis / Interpretation |
| :--- | :--- | :---: | :--- |
| **Throughput & Speed** | Processing Latency | **42.3 ms / doc** | Sub-50ms execution enables real-time interactive UI updates. |
| **Extraction Reliability** | Document Processing Success Rate | **100.00%** (96/96) | Zero unhandled crashes across the entire test set. |
| **Document Classification** | Baseline Keyword Rules Accuracy | **100.00%** | Clear lexical boundaries between bank, invoice, and KYC text. |
| **Document Classification** | TF-IDF + Logistic Regression ML | **100.00%** | Perfect separation on unigram/bigram token vectors. |
| **Field Extraction Accuracy**| Bank Statements | **100.00%** (205/205) | High precision regex and tabular anchor alignment. |
| **Field Extraction Accuracy**| Commercial Invoices | **83.33%** (175/210) | Multi-line description formatting causes minor boundary variance. |
| **Field Extraction Accuracy**| PAN Identity Cards | **66.67%** (16/24) | Minimal text volume makes boundary tokens critical. |
| **Field Extraction Accuracy**| Aadhaar Cards | **75.00%** (36/48) | Multi-line addresses occasionally absorb trailing labels. |
| **Fault Detection (Recall)** | `balance_mismatch` | **100.0%** (4/4) | Perfect mathematical sensitivity on closing balance drift. |
| **Fault Detection (Recall)** | `total_mismatch` | **100.0%** (1/1) | Arithmetic check reliably flags subtotal + tax discrepancies. |
| **Fault Detection (Recall)** | `future_dates` | **100.0%** (3/3) | Date sanity checks flag transactions beyond threshold year. |
| **Fault Detection (Recall)** | `duplicate_transactions` | **100.0%** (2/2) | Exact ref number hash set reliably identifies repeated rows. |
| **Fault Detection (Recall)** | `invalid_aadhaar_format` | **100.0%** (2/2) | Regulatory regex flags malformed lengths and letters. |
| **Fault Detection (Recall)** | `invalid_gstin` | **100.0%** (1/1) | Strict 15-character state/PAN structure flags invalid codes. |
| **Risk Flag Sensitivity** | Labelled Tampered Recall | **100.00%** (13/13) | Zero false negatives: no tampered document bypassed review. |
| **The Key Experiment** | Digital PDF Accuracy | **87.38%** | Baseline accuracy on vector text documents. |
| **The Key Experiment** | Scanned OCR Accuracy | **52.43%** | Accuracy on blurred, rotated, noisy scan PNGs. |
| **The Key Experiment** | **OCR Accuracy Drop** | **-34.95%** | **Key Milestone-1 Finding:** Optical degradations substantially hurt regex matching, proving the necessity of field confidence penalties and human review. |

---

## 4. Updated Risk Analysis & Mitigation Matrix

| Risk ID | Risk Category | Potential Impact | Severity | Likelihood | Implemented Mitigation in FinDocAI MVP |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **RSK-01** | **Technical (OCR Degradation)** | Character misrecognition (e.g. '0' vs 'O') breaks balance checks | High | High | Applied OCR uncertainty penalty (x0.85); flagged low-confidence fields in UI; enabled human correction editor (`st.data_editor`). |
| **RSK-02** | **Ethical (Autonomous Harm)** | System misclassifies legitimate user as fraudulent | Critical | Low | **Strict Non-Negotiable Rule:** System never outputs "fraud score". Review Priority is an indicator only; UI enforces disclaimer: *"Indicators only. Human review required."* |
| **RSK-03** | **Privacy & Compliance** | Leakage of sensitive PII (PAN, Aadhaar, Account No) in logs/DB | High | Medium | Implemented regex-based masking before persistence; safe audit logging; right-to-be-forgotten document deletion function. |
| **RSK-04** | **Operational (Corrupt Input)** | Malformed or empty PDFs crash the backend server | Medium | High | Wrapped ingestion in defensive try-except blocks; returns HTTP 400/422 with actionable user guidance; verified in TC-20 through TC-25. |
| **RSK-05** | **Academic (Explainability)** | Evaluator challenges students on complex opaque model internals | High | Medium | Zero black-box deep learning models. Rules are simple arithmetic; ML is standard TF-IDF + Logistic Regression; complete plain-English documentation. |
