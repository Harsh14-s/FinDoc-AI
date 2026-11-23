# FinDocAI: Capstone Project Log Diary

**Course:** CSET400C Capstone Project, Academic Session 2026–27  
**Group ID:** G382  
**Students:**  
- Harsh Shukla (`E23CSEU0003`)
- Akshita Singh (`E23CSEU0030`)  
**Project Guide / Evaluator:** Department of Computer Science & Engineering, Bennett University

---

## 1. Project Log Diary Entries

| Date | Phase / Sprint | Contributor(s) | Specific Activities & Deliverables Completed | Hours |
| :---: | :--- | :---: | :--- | :---: |
| **14-Oct-2026** | Milestone-1 Planning | Harsh & Akshita | Prepared Milestone-1 proposal, requirement analysis, and stakeholder definition. Aligned with SDG 9 and SDG 8. | 6 hrs |
| **18-Nov-2026** | Architecture Design | Harsh Shukla | Designed modular directory skeleton (`ingest/`, `classify/`, `extract/`, `validate/`, `storage/`, `api/`). Setup pytest configuration. | 4 hrs |
| **18-Nov-2026** | Synthetic Data & Scans | Akshita Singh | Authored `generator.py` with ReportLab and Faker. Generated 320 documents (120 bank, 120 invoices, 80 KYC) with ~15% labelled tamper injections. Rendered 40 degraded scans with blur and noise. | 6 hrs |
| **19-Nov-2026** | Ingestion & Extraction | Harsh Shukla | Built `pdf_parser.py` (PyMuPDF + pdfplumber) and `ocr_engine.py` with graceful fallback. Implemented regex & positional schema extractors for bank statements and invoices. | 6 hrs |
| **19-Nov-2026** | Classification Engines | Akshita Singh | Implemented baseline keyword rules (`rule_classifier.py`) and TF-IDF Logistic Regression ML model (`ml_classifier.py`). Created unified consensus dispatcher. | 5 hrs |
| **20-Nov-2026** | Validation Rules | Harsh Shukla | Developed 10 explainable validation checks (`rules.py`, `validator.py`) returning explicit Rule IDs, pass/fail status, and mathematical explanations for balance and total reconciliations. | 6 hrs |
| **20-Nov-2026** | Flags & Review Priority | Akshita Singh | Designed explainable unusual transaction rules (median outliers, repeated amounts, negative balances, bounced entries) and weighted review priority engine (Low/Med/High). | 5 hrs |
| **20-Nov-2026** | SQLite & Privacy | Harsh Shukla | Built relational database schema (`db.py`) with foreign keys, cascading deletes, human correction audit logging, and PII masking for PAN, Aadhaar, and Accounts (`privacy.py`). | 5 hrs |
| **21-Nov-2026** | FastAPI & Streamlit UI | Harsh & Akshita | Developed REST API (`app.py`) with upload, corrections, and export endpoints. Built interactive Streamlit dashboard (`main.py`) with demo buttons, data editor, and mandatory disclaimer. | 7 hrs |
| **21-Nov-2026** | Evaluation & Tests | Akshita Singh | Authored `evaluate.py`. Benchmarked 96 test docs and 40 degraded scans. Generated CSV reports, confusion matrix, and digital vs OCR accuracy charts in `results/`. | 5 hrs |
| **21-Nov-2026** | Robustness & Viva Prep | Harsh Shukla | Expanded automated pytest suite to 29 tests covering corrupt/empty edge cases. Authored `VIVA_GUIDE.md`, completed Milestone-2 documentation, and created one-click runner. | 5 hrs |

---

## 2. Weekly Supervisor Sign-Off Template

**Week 1 Sign-Off (Milestone-1 Approval):**  
- Supervisor Signature: _______________________ Date: _________________  
- Comments: Milestone-1 proposal reviewed. Proceed with local offline prototype.

**Week 2 Sign-Off (Milestone-2 Working MVP):**  
- Supervisor Signature: _______________________ Date: _________________  
- Comments: Working MVP verified with running Streamlit UI, SQLite audit log, real evaluation results, and 29 passed unit tests.
