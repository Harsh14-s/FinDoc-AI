# FinDocAI: Experimental Results & Limitations Analysis
**Course:** CSET400C Capstone Project | **Milestone:** 2
**Group G382:** Harsh Shukla (E23CSEU0003), Akshita Singh (E23CSEU0030)
**Primary SDG:** SDG 9 (Industry, Innovation & Infrastructure) | **Secondary SDG:** SDG 8 (Decent Work)

---

## 1. Executive Experimental Results

| Metric | Measured Value | Benchmark Description |
| :--- | :--- | :--- |
| **Total Test Dataset** | **96 documents** | Stratified across Bank Statements, Invoices, PAN, and Aadhaar |
| **Processing Success Rate** | **100.00%** | Proportion of supported documents processed end-to-end |
| **Average Processing Time** | **42.3 ms/doc** | High-throughput local offline processing |
| **ML Classification Accuracy** | **100.00%** | TF-IDF + Logistic Regression on 4 document categories |
| **Baseline Rule Classification**| **100.00%** | Keyword density baseline comparison |
| **Clean False Positive Rate** | **60.24%** | Percentage of clean documents incorrectly flagged |
| **Flag Precision** | **17.81%** | Precision against ground-truth labelled cases |
| **Flag Recall** | **100.00%** | Recall of labelled inconsistencies |
| **Digital PDF Field Accuracy** | **87.38%** | Extraction accuracy on high-quality digital vector PDFs |
| **Degraded Scanned Accuracy** | **52.43%** | Extraction accuracy on degraded scanned PNGs (noise/blur) |
| **OCR Performance Drop** | **-34.95%** | Accuracy drop caused by scanner optical imperfections |

---

## 2. Injected Fault Detection Rates

| Fault Label | Target Document | Injected | Detected | Detection Rate (%) |
| :--- | :--- | :---: | :---: | :---: |
| `balance_mismatch` | Auto-Routed | 4 | 4 | **100.0%** |
| `total_mismatch` | Auto-Routed | 1 | 1 | **100.0%** |
| `future_dates` | Auto-Routed | 3 | 3 | **100.0%** |
| `duplicate_transactions` | Auto-Routed | 2 | 2 | **100.0%** |
| `invalid_pan_format` | Auto-Routed | 0 | 0 | **0.0%** |
| `invalid_aadhaar_format` | Auto-Routed | 2 | 2 | **100.0%** |
| `invalid_gstin` | Auto-Routed | 1 | 1 | **100.0%** |

---

## 3. Honest Academic Limitations (Evaluator Discussion)

1. **Synthetic Data vs Real-World Variances:**
   - *Observation:* While the synthetic dataset incorporates realistic variations in bank names, IFSC codes, GSTINs, transaction narratives, and multi-template layouts, real enterprise documents exhibit greater graphical diversity, watermarks, proprietary stamps, and handwritten signatures.
   - *Impact:* Evaluator scores should acknowledge that real-world deployment requires fine-tuning extractors across hundreds of enterprise vendor templates.

2. **Template and Regex Positional Dependencies:**
   - *Observation:* The extraction layer uses robust regex and layout anchors. While explainable and fast, drastic shifts in tabular column ordering require updated heuristics.
   - *Impact:* Layout-aware vision models (e.g. LayoutLMv3) are identified in Milestone-1 as future work for cross-enterprise generalizations.

3. **Local OCR Sensitivity to Scan Degradation:**
   - *Observation:* As demonstrated by our key experiment, extraction accuracy drops from **87.38%** on digital PDFs to **52.43%** on degraded scans.
   - *Cause:* Gaussian optical blur and slight rotation introduce character substitution errors (e.g., confusing '0' and 'O', or missing decimal points).
   - *Mitigation:* FinDocAI applies an automatic confidence penalty on OCR inputs, alerting human reviewers to verify scanned fields.

4. **Human Review Governance & Ethical Disclaimer:**
   - *Observation:* FinDocAI strictly produces *preliminary review indicators* and *never* makes automated fraud or credit scoring decisions.
   - *Wording Policy:* All UI components and reports maintain the disclaimer: `"Indicators only. Human review required."`
