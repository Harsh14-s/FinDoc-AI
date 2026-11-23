# FinDocAI: Intelligent Financial Document Extraction, Validation and Risk Insights

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests Passing](https://img.shields.io/badge/pytest-29%20passed-brightgreen.svg)](tests/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B.svg)](https://streamlit.io/)
[![SDG 9](https://img.shields.io/badge/SDG-9%20Industry%20%26%20Innovation-E5243B.svg)](https://sdgs.un.org/goals/goal9)
[![SDG 8](https://img.shields.io/badge/SDG-8%20Decent%20Work-A21942.svg)](https://sdgs.un.org/goals/goal8)

> **⚠️ Mandatory Ethical Disclaimer:**  
> **Indicators only. Human review required.**  
> FinDocAI supports human experts; it strictly never outputs autonomous credit scores or fraud decisions.

---

## 📌 Project Overview
- **Course:** CSET400C Capstone Project, Academic Session 2026–27 (Bennett University)
- **Milestone:** Milestone-2 (Design + Working MVP + Validation)
- **Group ID:** G382
- **Team Members:**
  - **Harsh Shukla** (`E23CSEU0003`)
  - **Akshita Singh** (`E23CSEU0030`)

**FinDocAI** is a 100% local, offline, explainable document processing framework. It accepts PDFs and scanned images, classifies them into document categories (Bank Statement, Invoice, PAN, Aadhaar) using both baseline keyword heuristics and a TF-IDF + Logistic Regression ML model, extracts structured attributes into normalized JSON schemas, and executes rigorous rule-based validations—such as bank statement running-balance reconciliation and invoice tax arithmetic.

Every single warning explicitly explains **WHY** it was triggered.

---

## ⚡ Quickstart: One-Command Run

### 1. Clone & Install Dependencies
```powershell
git clone <repo-url>
cd "FinDoc AI"
pip install -r requirements.txt
pip install -e . --no-deps
```

### 2. Single Command Pipeline Execution
Run the orchestrator to automatically generate synthetic data, train the classifier, run benchmarks, execute tests, and launch the UI:
```powershell
python run_pipeline.py
```
The Streamlit dashboard will open automatically in your browser at `http://localhost:8501`.

---

## 🚀 Individual Service Commands

### Run FastAPI Backend Server
```powershell
python -m uvicorn findoc.api.app:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation (Swagger UI): `http://localhost:8000/docs`

### Run Streamlit Review Dashboard
```powershell
python -m streamlit run app/main.py
```

### Run Comprehensive Evaluation Suite
```powershell
python src/findoc/evaluate.py
```

### Run Automated Pytest Suite (29 Tests)
```powershell
python -m pytest tests/ -v
```

---

## 🔍 5-Minute Evaluator Live Demo Steps

1. **Launch Dashboard:** Run `python -m streamlit run app/main.py`.
2. **Observe Disclaimer:** Notice the top amber banner enforcing: *"Indicators only. Human review required."*
3. **Clean Bank Statement Test:** Click sidebar button **'🟢 Load Clean Bank Statement'**.
   - Model classification matches 100% across Keyword Rules and TF-IDF ML.
   - All 10 validation checks pass (green banner). Review Priority is **Low (Score: 0/100)**.
4. **Tampered Bank Statement Test:** Click sidebar button **'🔴 Load Tampered Bank Statement'**.
   - Validation flips to red **FAIL**. Rule `VAL_BNK_REC` explicitly explains:
     *"Closing balance of INR 99,999.00 does not match calculated balance of INR 55,000.00 (Discrepancy: INR 44,999.00)."*
   - Review Priority escalates to **High (Score: 65/100)** with contributing flags listed.
5. **Human-in-the-Loop Correction:** Go to tab **'✏️ Human Correction & Re-Validation'**.
   - Change Closing Balance back to `55,000.00` and click **'Save Corrections & Re-Validate'**.
   - System audits the change into SQLite, immediately re-validates, and flips status to **PASS** and Review Priority to **Low**.
6. **Key Experiment (Digital vs Scanned OCR):** Click sidebar button **'📷 Load Scanned Image (OCR)'** or inspect the **'🔬 Evaluation Metrics'** tab to see our empirical proof that optical scanner degradation causes a **34.95% drop in extraction accuracy**.
7. **Export:** Download normalized JSON or CSV in the **'💾 Raw Export'** tab.

---

## 📊 Key Evaluation Benchmark Results (Real Measured Numbers)

| Metric | Measured Value | Benchmark Description |
| :--- | :---: | :--- |
| **Total Test Dataset** | **96 documents** | Stratified across Bank Statements, Invoices, PAN, and Aadhaar |
| **Processing Success Rate** | **100.00%** | Zero unhandled failures across entire test split |
| **Average Processing Speed** | **42.3 ms / doc** | Real-time offline throughput |
| **ML Classification Accuracy** | **100.00%** | TF-IDF + Logistic Regression |
| **Rule Classification Accuracy**| **100.00%** | Keyword density baseline |
| **Field Accuracy: Bank Statements** | **100.00%** | 205/205 reference fields correctly extracted |
| **Field Accuracy: Invoices** | **83.33%** | 175/210 reference fields correctly extracted |
| **Injected Fault Recall** | **100.0%** | 100% detection rate on balance mismatches and arithmetic errors |
| **Digital PDF Field Accuracy** | **87.38%** | Baseline on clean vector digital PDFs |
| **Degraded Scanned Accuracy** | **52.43%** | Extraction accuracy on blurred, rotated, noisy scan PNGs |
| **The Key Experiment Finding** | **-34.95%** | Measured drop in accuracy caused by optical scan degradation |

---

## 🛠️ Repository Directory Structure

```
FinDoc AI/
├── app/
│   └── main.py                     # Interactive Streamlit review dashboard
├── data/
│   ├── raw/                        # 320 synthetic PDFs (train/test splits)
│   ├── ground_truth/               # Paired ground truth JSON files
│   ├── degraded_scans/             # 40 degraded scan PNGs for OCR experiment
│   ├── dataset_manifest.json       # Deterministic 70/30 split manifest
│   └── findoc.db                   # SQLite relational database
├── docs/
│   ├── milestone1/                 # Original Milestone-1 PDF and DOCX reports
│   ├── COMPLETED_VS_REMAINING.md   # Detailed audit of promises vs delivered MVP
│   ├── ARCHITECTURE_AND_DESIGN.md  # Mermaid diagrams (DFD 0/1, Sequence, ER)
│   ├── REQUIREMENTS_AND_TESTING.md # 29-test matrix & updated risk analysis
│   ├── LOG_DIARY.md                # Project work log and supervisor sign-offs
│   └── VIVA_GUIDE.md               # 1-min pitch, 5-min demo, module split & 25 Q&A
├── results/
│   ├── evaluation_summary.csv      # Real benchmark metrics summary
│   ├── accuracy_comparison.png     # Key experiment chart (Digital vs Scanned OCR)
│   ├── classification_confusion_matrices.png # ML confusion matrix plot
│   ├── limitations_analysis.md     # Honest academic limitations report
│   └── pytest_test_report.txt      # 29-test pytest execution log
├── src/findoc/
│   ├── ingest/                     # PDF parsing (PyMuPDF, pdfplumber) & OCR engine
│   ├── classify/                   # Dual classifier (Keyword rules & TF-IDF ML)
│   ├── extract/                    # Schemas, normalizers, regex/positional extractors
│   ├── validate/                   # 10 explicit arithmetic and regulatory rules
│   ├── flags/                      # Explainable unusual transaction indicators
│   ├── storage/                    # SQLite CRUD, audit trails, and privacy masking
│   ├── api/                        # FastAPI REST application endpoints
│   ├── generator.py                # Synthetic dataset & degradation generator
│   └── evaluate.py                 # Evaluation benchmark script
├── tests/                          # 29 automated pytest test cases
├── pyproject.toml                  # Package installation specification
├── pytest.ini                      # Pytest configuration
├── requirements.txt                # Pinned dependencies with one-line explanations
└── run_pipeline.py                 # Single-command orchestrator script
```

---

## 👥 Student Contributions & Module Ownership

- **Harsh Shukla (`E23CSEU0003`):** Ingestion (PyMuPDF/pdfplumber), regex and positional extraction schemas, rule-based validation engine (`VAL_REQ`, `VAL_NUM`, `VAL_BNK_REC`, `VAL_INV_TOT`, `VAL_FMT`), FastAPI REST endpoints, and SQLite audit database.
- **Akshita Singh (`E23CSEU0030`):** Synthetic dataset generation (ReportLab & Faker), optical scan degradation simulation (Pillow & NumPy), dual classification (Keyword rules + TF-IDF ML), Review Priority engine, Streamlit UI, and evaluation benchmarking suite.
