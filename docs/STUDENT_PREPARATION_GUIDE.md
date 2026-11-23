# FinDocAI: Complete Student Master Preparation Guide
**Comprehensive Conceptual Breakdown, Code Walkthrough, Demo Script & Evaluator Defense**

**Course:** CSET400C Capstone Project, Milestone-2 (Working MVP & Validation)  
**Institution:** Bennett University (Times of India Group)  
**Academic Session:** 2026–2027  
**Group ID:** G382  
**Students:**  
- **Harsh Shukla** (`E23CSEU0003`)
- **Akshita Singh** (`E23CSEU0030`)  
**SDG Alignment:** Primary: **SDG 9** (Industry, Innovation & Infrastructure), Secondary: **SDG 8** (Decent Work & Economic Growth)

---

## TABLE OF CONTENTS
1. [The Big Picture: What is FinDocAI and Why Does it Exist?](#1-the-big-picture)
2. [Non-Negotiable Project Rules & Ethics](#2-non-negotiable-project-rules--ethics)
3. [Student Division of Ownership](#3-student-division-of-ownership)
4. [Step-by-Step Codebase Architecture](#4-step-by-step-codebase-architecture)
5. [The Key Experiment & Real Benchmark Numbers](#5-the-key-experiment--real-benchmark-numbers)
6. [Step-by-Step 5-Minute Live Demo Guide](#6-step-by-step-5-minute-live-demo-guide)
7. [Evaluator Questions & Bulletproof Answers](#7-evaluator-questions--bulletproof-answers)
8. [Quick Reference Cheat-Sheet](#8-quick-reference-cheat-sheet)

---

## 1. THE BIG PICTURE

### The Industry Problem
Every day, banks, audit firms, NBFCs, and businesses process thousands of financial documents—bank account statements, supplier invoices, and KYC identity cards.
- **Problem 1 (Different Layouts):** HDFC statements look nothing like ICICI or SBI statements. Invoices from AWS look nothing like logistics freight slips.
- **Problem 2 (Extraction Errors):** Scanned photos or mobile phone pictures suffer from blur, tilted angles, and sensor noise. Standard OCR makes mistakes (e.g., misreading `0` as `O`, or dropping decimal points).
- **Problem 3 (Manual Verification Burden):** Human accountants must manually calculate whether line items add up to the subtotal, whether tax is 18%, and whether running balances match. This is exhausting, expensive, and error-prone.

### The FinDocAI Solution
FinDocAI is an **end-to-end, 100% offline, explainable document intelligence system**. It takes a digital PDF or scanned image and automatically:
1. **Ingests** the text and tables cleanly.
2. **Classifies** the document type (Bank Statement vs. Invoice vs. PAN vs. Aadhaar) using both keyword rules and a machine learning model.
3. **Extracts** critical attributes into a standardized schema (normalized ISO dates, clean float numbers) with a confidence score per field.
4. **Validates** predefined mathematical and regulatory rules (e.g., Opening + Deposits - Withdrawals == Closing). If a check fails, it explains **EXACTLY WHY**.
5. **Flags** unusual transactions (unusually large amounts vs account median, negative balances, cash withdrawals, bounced payments) and combines them into an explainable **Review Priority (Low/Medium/High)**.
6. **Enables Human Correction**: If OCR misread a field, the human reviewer edits it on screen, saves it to an audited SQLite database, and the system **instantly re-evaluates validation and flags in real time**.

---

## 2. NON-NEGOTIABLE PROJECT RULES & ETHICS

When speaking to any evaluator, you must stick strictly to these three principles:

1. **NEVER SAY "FRAUD SCORE" OR "CREDIT SCORE"**:
   - *Why?* Milestone-1 explicitly promises that this system supports human professionals and does not make autonomous legal, financial, or credit decisions.
   - *What to say instead:* Say **"Review Priority (Low, Medium, High)"** and **"Risk Indicators"** or **"Flags"**.
   - *Notice our UI:* The top banner says: `⚠️ Indicators only. Human review required. System does not make autonomous fraud or credit decisions.`

2. **100% LOCAL & OFFLINE (NO PAID APIS OR LLMS)**:
   - There is NO OpenAI API, NO cloud OCR (no AWS Textract, no Google Cloud Document AI), and NO paid key.
   - Everything runs on your machine using Python, PyMuPDF, Scikit-learn, SQLite, and Tesseract. This guarantees complete data privacy for financial documents.

3. **REAL NUMBERS ONLY (NO HARD-CODED RESULTS)**:
   - Every number in `results/` was measured by running `src/findoc/evaluate.py` across 96 test documents and 40 degraded scans.

---

## 3. STUDENT DIVISION OF OWNERSHIP

Both students have an equal, distinct share of the project. Practice your respective section so you can speak confidently.

### Harsh Shukla (`E23CSEU0003`) — Core Engineering, Extraction, Validation & Backend
- **Module 1: Ingestion Engine (`src/findoc/ingest/`):**
  - PyMuPDF (`fitz`) for lightning-fast digital PDF text extraction.
  - `pdfplumber` for tabular cell coordinate extraction.
  - Tesseract OCR integration with graceful fallback if the binary is missing.
- **Module 2: Extraction Schemas & Normalization (`src/findoc/extract/`):**
  - Pydantic models for Bank Statements, Invoices, and KYC documents.
  - Regular expressions and layout anchor patterns.
  - Standardization functions: `normalize_date()` to `YYYY-MM-DD`, `normalize_amount()` to clean float numbers.
  - Per-field confidence scoring (0.95 direct match, 0.75 fallback, 0.85x OCR penalty).
- **Module 3: Rule-Based Validation Engine (`src/findoc/validate/`):**
  - 10 deterministic rules returning explicit Rule IDs (`VAL_REQ_001`, `VAL_BNK_REC`, `VAL_INV_TOT`, `VAL_FMT_PAN`, etc.).
  - Mathematical balance reconciliation logic and running balance continuity check.
- **Module 4: Storage, API & Privacy (`src/findoc/storage/`, `src/findoc/api/`):**
  - SQLite database schema (`findoc.db`) with cascading foreign keys and human correction audit history.
  - Privacy masking functions for PAN, Aadhaar, and Account numbers.
  - FastAPI REST backend (`/upload`, `/documents`, `/corrections`, `/export`).

### Akshita Singh (`E23CSEU0030`) — Data Generation, Classification, Risk Flags & UI
- **Module 1: Synthetic Data Generation (`src/findoc/generator.py`):**
  - Created 320 synthetic PDFs across Bank Statements, Invoices, PAN, and Aadhaar using ReportLab and Faker.
  - Deterministic 70/30 train/test split with fixed random seed (`RANDOM_SEED = 42`).
  - Labelled tamper injections (~15%): balance mismatches, total mismatches, future dates, duplicate transactions.
- **Module 2: Scanner Optical Degradation Simulation:**
  - Rendered 40 test documents as realistic scanned PNGs.
  - Simulated scanner imperfections using Pillow and NumPy: slight rotation (-2.2° to +2.2°), Gaussian lens blur, and speckle noise.
- **Module 3: Dual Classification Engine (`src/findoc/classify/`):**
  - Baseline Keyword Density Rules (`rule_classifier.py`).
  - TF-IDF Vectorizer + Logistic Regression ML Classifier (`ml_classifier.py`).
  - Unified consensus dispatcher reporting both predictions and agreement status.
- **Module 4: Flags & Review Priority Engine (`src/findoc/flags/`):**
  - Explainable unusual-transaction rules: median outliers (>3.5x median), repeated identical amounts, negative balances, cash withdrawals, and bounced entries.
  - Weighted aggregator mapping to Low (<20), Medium (20-50), and High (>=50) priority.
- **Module 5: Streamlit Interface & Evaluation Suite (`app/main.py`, `src/findoc/evaluate.py`):**
  - Streamlit dashboard with one-click demo buttons and human-in-the-loop correction editor.
  - Milestone-1 Section 12 benchmark suite generating CSV reports and matplotlib charts in `results/`.

---

## 4. STEP-BY-STEP CODEBASE ARCHITECTURE

Let's walk through how a document moves through FinDocAI:

```
[ Uploaded Document (PDF or PNG) ]
              │
              ▼
    1. INGESTION ENGINE (PyMuPDF / Tesseract)
       - Checks if digital text exists (>40 chars)
       - If scanned image, routes to Tesseract OCR
       - Returns: text, page count, tables, is_scanned flag
              │
              ▼
    2. CLASSIFICATION ENGINE (Dual Strategy)
       - Runs Rule Keyword Matcher
       - Runs TF-IDF + Logistic Regression ML
       - Returns: predicted_class, rule_conf, ml_conf, agreement
              │
              ▼
    3. INFORMATION EXTRACTION (Regex & Positional Anchors)
       - Extracts dates, amounts, account/invoice numbers, line items
       - Normalizes to ISO dates (YYYY-MM-DD) and float currency
       - Computes per-field confidence score
              │
              ▼
    4. VALIDATION ENGINE (10 Explicit Rules)
       - Checks required fields & numeric types
       - Bank: Opening + Deposits - Withdrawals == Closing
       - Bank: Running balance continuity across transactions
       - Invoice: Subtotal + Tax == Grand Total & Line items sum == Subtotal
       - Formats: PAN regex, Aadhaar 12-digit, IFSC 11-char, GSTIN 15-char
       - Date sanity (no dates beyond current year) & Duplicate transactions
       - Returns: Pass/Fail status and exact plain-English reason for every rule
              │
              ▼
    5. FLAGS & REVIEW PRIORITY ENGINE
       - Flags median outliers, repeated amounts, negative balances, bounced entries
       - Computes transparent weighted sum (0 to 100)
       - Assigns Review Priority: Low (<20), Medium (20-50), High (>=50)
              │
              ▼
    6. STORAGE, PRIVACY & AUDIT LOG (SQLite)
       - Masks PAN, Aadhaar, and Account numbers (e.g. ABXXXXXX4F)
       - Stores records in data/findoc.db
              │
              ▼
    7. STREAMLIT UI / FASTAPI REST API
       - Displays badges, rule cards, and editable table (st.data_editor)
       - Human Reviewer edits value -> Triggers instant Re-Validation cycle
       - Exports normalized JSON and audit CSV
```

---

## 5. THE KEY EXPERIMENT & REAL BENCHMARK NUMBERS

Evaluators want to see **real scientific experiments**. You must memorize these exact numbers:

### The Key Experiment: Digital Vector PDF vs Scanned OCR
- **Why did we do this?** To prove the real-world impact of optical scanner imperfections on financial document processing.
- **How did we test it?** We took 40 test documents and rendered them as degraded scanned PNGs with slight tilt (-2.2° to +2.2°), Gaussian blur, and speckle noise. Then we evaluated field extraction on both the clean digital PDF and the degraded scan.
- **The Result:**
  - **Clean Digital PDF Field Accuracy:** **87.38%**
  - **Degraded Scanned OCR Field Accuracy:** **52.43%**
  - **Empirical Accuracy Drop:** **-34.95%**
- **The Academic Conclusion:** Scanner degradation causes character confusion (e.g., misreading `.` as `,` or dropping digits), which severely impairs regex parsing. This empirically justifies why FinDocAI applies an automatic confidence penalty on OCR inputs and why human-in-the-loop review is mandatory!

### Other Real Benchmark Numbers to Cite:
- **Total Test Dataset:** 96 documents (from 320 total, 70/30 split)
- **Processing Success Rate:** **100.00%** (0 unhandled crashes across all 96 docs)
- **Average Processing Speed:** **42.3 milliseconds per document** (super-fast offline performance)
- **Document Classification Accuracy:** **100.00%** on both Keyword Rules and TF-IDF ML
- **Field Extraction Accuracy:**
  - Bank Statements: **100.00%** (205/205 fields)
  - Invoices: **83.33%** (175/210 fields)
  - Aadhaar: **75.00%** | PAN: **66.67%**
- **Fault Detection Recall (Injected Tampering):**
  - `balance_mismatch`: **100.0%** (4/4 detected)
  - `total_mismatch`: **100.0%** (1/1 detected)
  - `future_dates`: **100.0%** (3/3 detected)
  - `duplicate_transactions`: **100.0%** (2/2 detected)
  - `invalid_aadhaar_format`: **100.0%** (2/2 detected)
  - `invalid_gstin`: **100.0%** (1/1 detected)
- **Labelled Tampered Case Recall:** **100.00%** (13/13 detected, 0 false negatives)
- **Automated Tests:** **29 passed tests out of 29** in pytest.

---

## 6. STEP-BY-STEP 5-MINUTE LIVE DEMO GUIDE

Follow this exact sequence when presenting to the evaluator:

### Step 1: Open Terminal & Run One Command
```powershell
python run_pipeline.py
```
*What happens:* It automatically checks the database, validates synthetic data, confirms ML model training, verifies benchmark results, runs all 29 pytest tests (printing 29 green PASSED), and opens the Streamlit browser window at `http://localhost:8501`.

### Step 2: Point Out the Ethical Disclaimer Banner
- Point to the amber box at the top of the screen:
  `⚠️ Review Disclaimer: Indicators only. Human review required. System does not make autonomous fraud or credit decisions.`
- *Say:* *"Evaluators, notice our strict ethical boundary. FinDocAI provides decision support and risk indicators for human auditors; it never outputs an autonomous credit or fraud score."*

### Step 3: Test a Clean Document (Click "🟢 Load Clean Bank Statement")
- In the sidebar under Quick Demo Documents, click **"🟢 Load Clean Bank Statement"**.
- Point out:
  1. **Classification:** Shows `Bank Statement` with 100% agreement between Keyword Rules and TF-IDF ML.
  2. **Review Priority:** Shows green badge: `Low Priority (Score: 0/100)`.
  3. **Validation Status:** Shows green box: `PASS (10/10 checks)`.
  4. **Rule Details:** Expand the validation tab to show that all checks passed, including `VAL_BNK_REC` (Opening + Deposits - Withdrawals == Closing) and `VAL_BNK_RUN_BAL` (continuity across all transactions).
  5. **Transactions Ledger:** Show the extracted table with date, narration, debit, credit, and balance.

### Step 4: Test a Tampered Document (Click "🔴 Load Tampered Bank Statement")
- Click **"🔴 Load Tampered Bank Statement"**.
- Point out what changes:
  1. **Validation Status:** Flips to prominent red `FAIL (1 failure(s))`.
  2. **Explainable Reason:** Under rule `VAL_BNK_REC`, show the plain-English explanation:
     *"Closing balance mismatch. Extracted closing balance is INR 99,999.00, but calculated Opening (INR 50,000.00) + Deposits (INR 20,000.00) - Withdrawals (INR 15,000.00) = INR 55,000.00 (Discrepancy: INR 44,999.00)."*
  3. **Review Priority:** Escalates to red badge: `High Priority (Score: 65/100)`. Show the contributing flags list explaining the exact reason.

### Step 5: Demonstrate Human-in-the-Loop Correction
- Click the third tab: **"✏️ Human Correction & Re-Validation"**.
- In the Closing Balance input, change `99999.0` back to `55000.0`.
- Click **"💾 Save Corrections & Re-Validate"**.
- The page reloads:
  - SQLite logs the audit record (old value: 99999.0, new value: 55000.0, reviewer: analyst_ui).
  - Validation immediately re-evaluates: status flips from red **FAIL** back to green **PASS**!
  - Review Priority drops from **High** to **Low**!
- *Say:* *"This proves our human-in-the-loop workflow. When a human reviewer verifies the document and enters the corrected balance, FinDocAI audits the change and immediately re-evaluates the rules."*

### Step 6: Show Export & Metrics
- Click the fourth tab: **"💾 Raw Export (JSON / CSV)"**.
- Show the **"Download Normalized JSON"** and **"Download Summary CSV"** buttons.
- In the sidebar, click **"🔬 Evaluation Metrics"** to show the real benchmark table and the **Digital vs OCR Accuracy chart**.

---

## 7. EVALUATOR QUESTIONS & BULLETPROOF ANSWERS

Here are the top questions evaluators ask, along with exact, honest answers:

### Q1: Why synthetic data? Why not use real bank statements from Kaggle or the internet?
**Answer:** "Real financial documents contain confidential Personally Identifiable Information (PII) and proprietary banking data protected by RBI data privacy guidelines and the Indian Digital Personal Data Protection (DPDP) Act. Scraping real bank statements risks privacy violations. Furthermore, real documents on Kaggle lack exact mathematical ground truth for transaction running balances. By generating 320 synthetic documents using ReportLab and Faker with fixed random seed 42, we know the exact ground truth for every line item and could inject controlled, labelled tamper faults to benchmark our validation accuracy."

### Q2: Why didn't you use deep learning or LayoutLM for extraction?
**Answer:** "We made a deliberate engineering trade-off:
1. *Compute & Offline Constraint:* LayoutLMv3 requires multi-gigabyte PyTorch dependencies, CUDA GPU infrastructure, and heavy cloud memory. Our system is designed to run 100% offline in 42 milliseconds on a standard laptop.
2. *Explainability:* In financial audits, auditors need deterministic mathematical certainty. If an invoice total doesn't match line items, deep learning attention weights cannot explain the exact arithmetic. Our rule-based validation engine provides an exact Rule ID and human-readable explanation for every discrepancy. We identified LayoutLM in our Milestone-1 report as future work for cross-enterprise generalization."

### Q3: Why is Machine Learning used ONLY for classification?
**Answer:** "Document classification is a semantic text-categorization task where vocabulary distributions naturally separate classes—for instance, bank statements contain words like 'deposit', 'IFSC', and 'balance', while invoices contain 'GSTIN', 'subtotal', and 'due date'. TF-IDF n-grams + Logistic Regression is ideal for this. In contrast, extraction requires precise alphanumeric boundary capture (like matching a 10-digit PAN or an 11-digit IFSC), where regular expressions and layout anchors provide deterministic, hallucination-free precision."

### Q4: Why is your classification accuracy 100%? Isn't that overfitting?
**Answer:** "The 100% accuracy on our 96 test documents is genuine because the vocabulary across these four document types is fundamentally distinct. An Indian PAN card has official phrases like 'Income Tax Department', an Aadhaar card has 'UIDAI' and 'Resident Name', an invoice has 'Tax Invoice' and 'GSTIN', and a bank statement has 'Transaction Activity' and 'Opening Balance'. Both our keyword baseline rules and our TF-IDF model found clear linear separation. If we introduced ambiguous documents like insurance receipts, we would expect lower accuracy."

### Q5: Why is your clean document false-positive rate ~60%?
**Answer:** "In our evaluation, 'False Positive' refers to a clean document triggering a Review Priority flag. This occurs because of our explainable statistical rule `FLAG_MEDIAN_OUTLIER`. When an account has routine small transactions (e.g., INR 1,000 groceries) and a single legitimate high-value salary credit or quarterly rent payment (e.g., INR 45,000), the rule flags it as an outlier for human verification. In financial auditing, high recall is prioritized over precision: auditors prefer inspecting 10 legitimate large transactions rather than letting 1 suspicious transaction slip by unflagged."

### Q6: What happens if Tesseract OCR is not installed on the system?
**Answer:** "We implemented defensive graceful degradation in `src/findoc/ingest/ocr_engine.py`. The system checks the system PATH and standard Windows install paths. If missing, it does not crash or throw unhandled exceptions. Instead, it provides clear instructions for downloading the UB-Mannheim installer, while digital PDF processing remains 100% functional."

### Q7: How does FinDocAI protect sensitive personal data (Privacy)?
**Answer:** "Under `src/findoc/storage/privacy.py`, all sensitive identifiers are sanitized:
- PAN numbers are masked (e.g. `ABCDE1234F` becomes `ABXXXXXX4F`).
- Aadhaar numbers are masked (e.g. `XXXX XXXX 1234`).
- Bank account numbers retain only the last 4 digits (`XXXXXXXX9012`).
- Plaintext PII is never committed to application logs.
- We provide a `delete_document` function to support the right-to-be-forgotten."

### Q8: How does this project align with Sustainable Development Goals?
**Answer:**
- **SDG 9 (Industry, Innovation & Infrastructure):** Upgrades technological capabilities for small accounting firms and credit co-operatives by providing an open-source, offline document verification pipeline without expensive enterprise software licenses.
- **SDG 8 (Decent Work & Economic Growth):** Reduces repetitive, exhausting manual data entry and mental arithmetic, preventing cognitive fatigue and human error for data-entry operators.

### Q9: What are the primary limitations of your current MVP?
**Answer:** "We documented our limitations honestly in `results/limitations_analysis.md`:
1. Multi-page balance sheets and income statements are not yet supported due to complex Ind-AS accounting schedules.
2. Cross-document reconciliation (e.g. 3-way matching an invoice to a purchase order and a bank debit) is out of scope for Milestone-2.
3. Heavily degraded mobile camera photos (with extreme perspective skew or shadows) degrade Tesseract OCR accuracy, demonstrating the necessity of human review."

---

## 8. QUICK REFERENCE CHEAT-SHEET

| Concept | Key Detail |
| :--- | :--- |
| **Command to Run Everything** | `python run_pipeline.py` |
| **Streamlit Port** | `http://localhost:8501` |
| **FastAPI Swagger Docs** | `http://localhost:8000/docs` |
| **Pytest Command** | `python -m pytest tests/ -v` (29 tests pass) |
| **Database File** | `data/findoc.db` (SQLite) |
| **Dataset Split** | 320 docs (224 train / 96 test = 70/30 split, seed 42) |
| **Tampered Documents** | 50 docs (15.6%) |
| **Degraded Scans** | 40 PNGs in `data/degraded_scans/` |
| **Digital PDF Accuracy** | **87.38%** |
| **Scanned OCR Accuracy** | **52.43%** (Drop: **-34.95%**) |
| **Processing Speed** | **42.3 ms / doc** |
| **Review Priority Tiers** | Low (<20), Medium (20-50), High (>=50) |
| **Mandatory Disclaimer** | *"Indicators only. Human review required."* |
| **PAN Regex** | `^[A-Z]{5}[0-9]{4}[A-Z]{1}$` (10 chars) |
| **IFSC Regex** | `^[A-Z]{4}0[A-Z0-9]{6}$` (11 chars) |
| **Aadhaar Regex** | `^[2-9][0-9]{11}$` (12 digits, cannot start with 0 or 1) |
| **GSTIN Regex** | `^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$` (15 chars) |
