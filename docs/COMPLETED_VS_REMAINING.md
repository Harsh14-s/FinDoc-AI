# FinDocAI: Completed vs. Remaining Work & Milestone-1 Deviation Log

**Course:** CSET400C Capstone Project, Milestone-2 (Design + Working MVP + Validation)  
**Group ID:** G382  
**Team Members:**  
- Harsh Shukla (`E23CSEU0003`)
- Akshita Singh (`E23CSEU0030`)  
**SDG Alignment:** Primary: **SDG 9** (Industry, Innovation & Infrastructure), Secondary: **SDG 8** (Decent Work & Economic Growth)

---

## 1. Executive Summary

Milestone-1 established the project proposal, stakeholder needs, and theoretical architecture for FinDocAI. Milestone-2 implements a working, fully explainable, offline MVP capable of ingesting PDF and image documents, classifying document types, extracting structured data into normalized schemas, running rule-based arithmetic/regulatory validations, generating review priority indicators, enabling human-in-the-loop corrections, and exporting auditable reports.

Where constraints between the academic timeline (48-hour prototype window, local offline constraints, complete student explainability) and the initial Milestone-1 proposal conflicted, **explainability and offline reliability took precedence**. Every deviation is explicitly documented below.

---

## 2. Completed MVP Capabilities (Milestone-2 Delivered)

| Capability / Module | Milestone-1 Promise | Milestone-2 Delivered Status | Verification / Artifact |
| :--- | :--- | :--- | :--- |
| **Document Ingestion** | Support digital PDFs and scanned images with OCR | **Delivered**: Dual path via PyMuPDF + pdfplumber for digital PDFs; Tesseract OCR via `pytesseract` for scanned images with graceful degradation if uninstalled. | `src/findoc/ingest/` (`pdf_parser.py`, `ocr_engine.py`) |
| **Document Classification** | Identify document type | **Delivered**: Dual classification reporting both baseline keyword heuristics and TF-IDF + Logistic Regression ML model (100% test accuracy). | `src/findoc/classify/` (`rule_classifier.py`, `ml_classifier.py`) |
| **Structured Schema Extraction** | Normalize fields, dates, and amounts | **Delivered**: Normalized JSON schemas for Bank Statements, Invoices, and KYC (PAN/Aadhaar) with ISO-8601 dates and cleaned numeric amounts. | `src/findoc/extract/` (`schemas.py`, `extractor_service.py`) |
| **Field Confidence Scores** | Confidence estimation per field | **Delivered**: Explicit per-field confidence metrics with an automatic uncertainty penalty applied to OCR-derived data. | `schemas.py`, Streamlit metrics |
| **Rule-Based Validation** | Arithmetic & regulatory checks explaining WHY | **Delivered**: 10 explicit rules (`VAL_REQ_001`, `VAL_NUM_001`, `VAL_BNK_REC`, `VAL_BNK_RUN_BAL`, `VAL_INV_TOT`, `VAL_INV_LINE_SUM`, `VAL_FMT_PAN`, `VAL_FMT_AAD`, `VAL_FMT_IFSC`, `VAL_DAT_SAN`, `VAL_DUP_TXN`) returning exact rule IDs and plain-English reasons. | `src/findoc/validate/` (`rules.py`, `validator.py`) |
| **Review Priority & Indicators** | Highlight unusual transactions for human review | **Delivered**: Transparent weighted sum yielding **Low / Medium / High** Review Priority with contributing flag rationales. Strictly avoids "fraud/credit score" wording. | `src/findoc/flags/` (`rules.py`, `engine.py`) |
| **Human Correction Workflow** | Allow analysts to correct extraction errors | **Delivered**: Interactive Streamlit UI and REST API (`PUT /documents/{id}/corrections`) that saves audit trails and re-triggers validation instantly. | `app/main.py`, `api/app.py` |
| **Persistence & Audit Trails** | Prototype storage of documents and history | **Delivered**: SQLite relational database (`data/findoc.db`) tracking documents, extracted data, validation results, flags, and human correction history. | `src/findoc/storage/` (`db.py`) |
| **Privacy Safeguards** | Data minimization and sensitive data protection | **Delivered**: Automatic masking of PAN, Aadhaar, and Bank Account numbers before database persistence, safe logging, and privacy document deletion. | `src/findoc/storage/` (`privacy.py`) |
| **Export Capabilities** | Export structured financial data | **Delivered**: Downloadable normalized JSON and standardized CSV formats via UI and REST API (`GET /documents/{id}/export`). | `app/main.py`, `api/app.py` |
| **Empirical Evaluation** | Benchmark against Section 12 criteria | **Delivered**: Real evaluation across 96 test docs and 40 degraded scans; CSVs and PNG charts generated in `results/`. | `src/findoc/evaluate.py`, `results/` |
| **Automated Test Suite** | Reliability and test coverage | **Delivered**: 29 automated pytest test cases covering clean flows, tampered flows, and boundary edge cases (empty, corrupt, non-existent files). | `tests/`, `results/pytest_test_report.txt` |

---

## 3. Explicit Milestone-1 Deviations and Rationale

| # | Milestone-1 Proposal Text | Milestone-2 Implemented Reality | Engineering & Academic Rationale |
| :---: | :--- | :--- | :--- |
| **DEV-01** | Support for Income Statements and Balance Sheets | **Deferred to Remaining Work**. Core focus on Bank Statements (deepest), Invoices, and KYC (PAN/Aadhaar). | Multi-page balance sheets require custom GAAP/Ind-AS taxonomy mappings that cannot be reliably explained by 3rd-year students in a 48-hour MVP without resorting to fragile black-box libraries. |
| **DEV-02** | Cloud OCR APIs (Amazon Textract, Google Cloud Document AI, Azure AI Document Intelligence) | **Strictly Local & Offline**: Tesseract OCR via `pytesseract` + PyMuPDF digital parser. | Project guidelines require zero paid cloud API dependencies, zero external network keys, and complete data privacy by running locally on the student workstation. |
| **DEV-03** | LayoutLM / Deep Learning Document Understanding | **Rule-Based Extractors + TF-IDF ML Classification**. | Deep layout models require GPU infrastructure, multi-gigabyte checkpoints, and opaque attention matrices. Rule-based extraction allows both students to personally explain every regex, boundary anchor, and math check to the evaluator. |
| **DEV-04** | Cross-Document Reconciliation (e.g., matching invoice to bank statement debit) | **Single-Document Deep Verification**. | Focus was directed toward rock-solid single-document verification (closing balance math, transaction running balance continuity, invoice subtotal + tax reconciliation) before cross-document state synchronization. |
| **DEV-05** | User Authentication & Role-Based Access Control (RBAC) | **Unauthenticated Local Review Session**. | Enterprise authentication (OAuth2 / JWT / LDAP) adds framework boilerplate without contributing to the core academic objectives of financial document validation and explainable AI risk indicators. |

---

## 4. Remaining Work (Future Roadmap for Milestone-3)

1. **Enterprise Financial Statement Taxonomies:**
   - Expand parser to multi-page P&L statements and balance sheets with Indian Accounting Standards (Ind-AS) schedule matching.
2. **Cross-Document 3-Way Matching:**
   - Reconcile invoice line totals against purchase orders and bank statement debit records.
3. **Advanced Layout-Aware Optical Modeling:**
   - Explore offline, quantized open-source models (e.g., Donut or LayoutLMv3 ONNX runtime) for non-standardized invoice layouts.
4. **Enhanced Statistical Outlier Baselines:**
   - Multi-month seasonal transaction modeling using moving-average z-scores rather than single-statement median thresholds.
5. **Role-Based Access Control (RBAC) & Multi-Tenant Deployment:**
   - Role separation between Junior Data Analysts (correction permissions only) and Senior Compliance Reviewers (approval permissions).
