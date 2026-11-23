"""Script to generate a comprehensive, publication-quality Viva & Oral Defense Guide PDF
for FinDocAI Capstone Project Milestone-2 (Group G382).
"""

import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable
)
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PDF = BASE_DIR / "docs" / "FinDocAI_Viva_Preparation_Guide_G382.pdf"
OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and draw total page numbers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "FinDocAI: Intelligent Financial Document Extraction & Risk Insights")
            self.drawRightString(558, 755, "Group G382 | Milestone-2 Viva Guide")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 747, 558, 747)

        # Running footer
        self.setFont("Helvetica", 8)
        self.drawString(54, 34, "CSET400C Capstone Project • Bennett University • Academic Session 2026-27")
        self.drawRightString(558, 34, f"Page {self._pageNumber} of {total_pages}")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)

        self.restoreState()


def create_viva_guide_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#2563EB"),
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.2,
        leading=13,
        textColor=colors.HexColor("#334155"),
        leftIndent=14,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        "Callout_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1E3A8A")
    )

    q_style = ParagraphStyle(
        "QuestionStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.2,
        leading=14,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    a_style = ParagraphStyle(
        "AnswerStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.3,
        leading=13.2,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8
    )

    story = []

    # =========================================================================
    # HEADER / COVER SECTION
    # =========================================================================
    story.append(Paragraph("FinDocAI: Intelligent Financial Document Extraction, Validation and Risk Insights", title_style))
    story.append(Paragraph("Comprehensive Viva Voce & Oral Defense Master Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2563EB"), spaceBefore=0, spaceAfter=10))

    meta_table_data = [
        [
            Paragraph("<b>Course:</b> CSET400C Capstone Project", body_style),
            Paragraph("<b>Milestone:</b> Milestone-2 (Working MVP & Validation)", body_style)
        ],
        [
            Paragraph("<b>Institution:</b> Bennett University, Academic Session 2026–27", body_style),
            Paragraph("<b>Group ID:</b> G382", body_style)
        ],
        [
            Paragraph("<b>Student A:</b> Harsh Shukla (<code>E23CSEU0003</code>)", body_style),
            Paragraph("<b>Student B:</b> Akshita Singh (<code>E23CSEU0030</code>)", body_style)
        ],
        [
            Paragraph("<b>SDG 9:</b> Industry, Innovation & Infrastructure", body_style),
            Paragraph("<b>SDG 8:</b> Decent Work & Economic Growth", body_style)
        ]
    ]
    t_meta = Table(meta_table_data, colWidths=[250, 254])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 1: THE 1-MINUTE ELEVATOR PITCH
    # =========================================================================
    story.append(Paragraph("1. The 1-Minute Executive Elevator Pitch", h1_style))
    story.append(Paragraph("<i>Memorize this verbatim for your opening statement to the evaluators:</i>", body_style))

    pitch_text = (
        "\"Respected evaluators, financial institutions and small businesses manually process millions of bank statements, "
        "commercial invoices, and KYC credentials daily. This manual entry is slow, expensive, and frequently overlooks subtle calculation tampering.<br/><br/>"
        "<b>FinDocAI</b> is an intelligent, 100% local, offline document intelligence framework. It ingests digital PDFs and optical scans, "
        "classifies document types using both dictionary heuristics and a TF-IDF + Logistic Regression ML classifier, extracts structured schemas into normalized JSON, "
        "and executes <b>10 deterministic arithmetic and regulatory validation rules</b>—such as transaction-by-transaction running balance reconciliation and GST tax arithmetic.<br/><br/>"
        "Unlike opaque black-box AI tools, <b>every single warning in FinDocAI explicitly explains WHY it failed</b>. Furthermore, our system surfaces explainable review indicators "
        "for human experts—strictly never outputting autonomous fraud or credit verdicts. In our benchmark across 96 stratified test documents, FinDocAI achieved a <b>100% processing success rate "
        "at 42.3 ms per document</b>, and our key empirical experiment demonstrated that optical scan degradation causes a <b>34.95% drop in extraction accuracy</b>, proving why automated confidence "
        "penalties and human-in-the-loop workflows are mathematically essential.\""
    )
    p_pitch = Paragraph(pitch_text, callout_style)
    t_pitch = Table([[p_pitch]], colWidths=[504])
    t_pitch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#3B82F6")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t_pitch)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 2: 5-MINUTE LIVE EVALUATOR DEMO SCRIPT
    # =========================================================================
    story.append(Paragraph("2. The 5-Minute Evaluator Live Demo Script", h1_style))
    demo_table_data = [
        [
            Paragraph("<b>Timeline & Lead</b>", body_style),
            Paragraph("<b>Action on Screen (Streamlit UI)</b>", body_style),
            Paragraph("<b>What to Say to the Evaluators</b>", body_style)
        ],
        [
            Paragraph("<b>0:00 - 0:45</b><br/>Harsh", body_style),
            Paragraph("Open <code>http://localhost:8501</code>.<br/>Point to top disclaimer and engine telemetry.", body_style),
            Paragraph("\"Notice our mandatory disclaimer: 'Indicators only. Human review required.' FinDocAI supports human experts; it never makes autonomous decisions. All processing runs 100% locally on standard hardware without external cloud APIs.\"", body_style)
        ],
        [
            Paragraph("<b>0:45 - 1:45</b><br/>Akshita", body_style),
            Paragraph("Click <b>'🟢 Clean Bank Statement'</b>.<br/>Show 100% classification & 10 green PASS rules.", body_style),
            Paragraph("\"Within 42 ms, our dual classifier confirms a Bank Statement with 100% agreement between keyword density and TF-IDF ML. All 10 validation rules—including transaction running-balance continuity—pass with green status. Review Priority is Low (0/100).\"", body_style)
        ],
        [
            Paragraph("<b>1:45 - 3:00</b><br/>Harsh", body_style),
            Paragraph("Click <b>'🔴 Tampered Statement'</b>.<br/>Show red FAIL banner and discrepancy callout.", body_style),
            Paragraph("\"Now observe balance tampering. Validation flips to red FAIL. Rule VAL_BNK_REC explicitly explains: 'Closing balance of INR 99,999 does not match calculated balance of INR 55,000 (Discrepancy: INR 44,999)'. Review Priority jumps to High (65/100).\"", body_style)
        ],
        [
            Paragraph("<b>3:00 - 4:00</b><br/>Akshita", body_style),
            Paragraph("Go to <b>'Human-in-the-Loop'</b> tab.<br/>Edit Closing Balance to 55000 and click Save.", body_style),
            Paragraph("\"This proves our human-in-the-loop workflow. A reviewer rectifies the closing balance, FinDocAI commits an immutable SQLite audit trail, immediately re-runs validation rules, flips status to PASS, and drops Review Priority back to Low.\"", body_style)
        ],
        [
            Paragraph("<b>4:00 - 4:40</b><br/>Harsh", body_style),
            Paragraph("Click <b>'📷 Scanned OCR Test'</b> or go to <b>'Evaluation Benchmarks'</b> tab.", body_style),
            Paragraph("\"Here is our empirical experiment. Clean digital PDFs achieve 87.38% extraction accuracy. But on realistic degraded scans with optical blur and rotation, accuracy drops to 52.43%—a 34.95% drop. FinDocAI applies an automated confidence penalty on OCR inputs.\"", body_style)
        ],
        [
            Paragraph("<b>4:40 - 5:00</b><br/>Both", body_style),
            Paragraph("Show JSON/CSV export, masked PII, and pass all 29 pytest tests.", body_style),
            Paragraph("\"Finally, the analyst exports normalized JSON or CSV. All 29 unit tests pass, and privacy is strictly enforced by masking PAN, Aadhaar, and account numbers. We are ready for questions.\"", body_style)
        ]
    ]
    t_demo = Table(demo_table_data, colWidths=[80, 160, 264])
    t_demo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    for r in range(1):
        for c in range(3):
            t_demo.setStyle(TableStyle([('TEXTCOLOR', (c,r), (c,r), colors.white)]))
    story.append(t_demo)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 3: SYSTEM ARCHITECTURE & 10 VALIDATION RULES
    # =========================================================================
    story.append(Paragraph("3. End-to-End Architecture & Core Pipeline", h1_style))
    story.append(Paragraph(
        "FinDocAI follows a 7-stage sequential pipeline designed for deterministic execution, explainability, and full data residency:",
        body_style
    ))
    story.append(Paragraph("• <b>Stage 1 (Ingestion):</b> Native vector parsing via PyMuPDF (sub-20ms) and geometric grid reconstruction with pdfplumber. Optical scans fallback to Tesseract OCR with graceful fallback diagnostics.", bullet_style))
    story.append(Paragraph("• <b>Stage 2 (Dual Classification):</b> Two parallel engines: Baseline Keyword Density heuristics and Machine Learning (TF-IDF Vectorizer + Logistic Regression, 100% test split accuracy).", bullet_style))
    story.append(Paragraph("• <b>Stage 3 (Extraction & Normalization):</b> Regular expressions with spatial boundary anchors extract dates into ISO <code>YYYY-MM-DD</code>, currency values into floats, and line items into structured lists. Each field receives a confidence score (0.0 to 1.0) with an automatic 0.85x penalty for OCR sources.", bullet_style))
    story.append(Paragraph("• <b>Stage 4 (Rule Validation):</b> 10 explicit mathematical and regulatory checks evaluated with plain-English rationales.", bullet_style))
    story.append(Paragraph("• <b>Stage 5 (Review Priority Engine):</b> Transparent weighted aggregator (0 to 100 score: Low &lt; 20, Medium 20–50, High &gt;= 50) computing explainable risk indicators.", bullet_style))
    story.append(Paragraph("• <b>Stage 6 (Storage & Privacy):</b> Relational SQLite store (<code>data/findoc.db</code>) with automatic privacy masking (PAN: <code>XXXXX1234X</code>, Aadhaar: <code>XXXX-XXXX-1234</code>, Account: <code>XXXXXX1234</code>) and immutable human correction audit trails.", bullet_style))
    story.append(Paragraph("• <b>Stage 7 (Presentation & APIs):</b> Modern Streamlit review dashboard and FastAPI asynchronous REST endpoints (Swagger at <code>/docs</code>).", bullet_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("The 10 Formal Rule-Based Validation Checks:", h2_style))

    rules_table_data = [
        [Paragraph("<b>Rule ID</b>", body_style), Paragraph("<b>Rule Name</b>", body_style), Paragraph("<b>Mathematical / Logical Definition</b>", body_style)],
        [Paragraph("<code>VAL_REQ_001</code>", body_style), Paragraph("Mandatory Fields", body_style), Paragraph("Checks presence of all schema-required attributes (e.g. Account Number, Subtotal).", body_style)],
        [Paragraph("<code>VAL_NUM_001</code>", body_style), Paragraph("Non-Negative Balances", body_style), Paragraph("Asserts Opening Balance, Subtotal, Grand Total, and Tax &gt;= 0.", body_style)],
        [Paragraph("<code>VAL_BNK_REC</code>", body_style), Paragraph("Statement Reconciliation", body_style), Paragraph("<code>|Opening + Deposits - Withdrawals - Closing| &lt;= 0.05 INR</code>.", body_style)],
        [Paragraph("<code>VAL_BNK_RUN_BAL</code>", body_style), Paragraph("Running Balance Continuity", body_style), Paragraph("Validates row-by-row: <code>Prev_Bal + Credit - Debit == Stated_Bal</code> across all txns.", body_style)],
        [Paragraph("<code>VAL_INV_TOT</code>", body_style), Paragraph("Invoice Total Arithmetic", body_style), Paragraph("Checks: <code>|Subtotal + Tax_Amount - Grand_Total| &lt;= 0.05 INR</code> and line-item sums.", body_style)],
        [Paragraph("<code>VAL_FMT_PAN</code>", body_style), Paragraph("PAN Regulatory Format", body_style), Paragraph("Validates statutory Income Tax regex pattern: <code>^[A-Z]{5}[0-9]{4}[A-Z]$</code>.", body_style)],
        [Paragraph("<code>VAL_FMT_AAD</code>", body_style), Paragraph("Aadhaar Format Check", body_style), Paragraph("Validates UIDAI 12-digit numeric constraint: <code>^[2-9]{1}[0-9]{3}\\s?[0-9]{4}\\s?[0-9]{4}$</code>.", body_style)],
        [Paragraph("<code>VAL_FMT_IFSC</code>", body_style), Paragraph("IFSC Code Standard", body_style), Paragraph("Validates RBI 11-character alphanumeric structure: <code>^[A-Z]{4}0[A-Z0-9]{6}$</code>.", body_style)],
        [Paragraph("<code>VAL_DAT_SAN</code>", body_style), Paragraph("Date Chronological Sanity", body_style), Paragraph("Ensures invoice/statement dates are not future-dated and chronologically ordered.", body_style)],
        [Paragraph("<code>VAL_DUP_TXN</code>", body_style), Paragraph("Duplicate Transaction Check", body_style), Paragraph("Hashes <code>ref_no</code> + amount + date to detect redundant debit entries.", body_style)]
    ]
    t_rules = Table(rules_table_data, colWidths=[90, 140, 274])
    t_rules.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    for r in range(1):
        for c in range(3):
            t_rules.setStyle(TableStyle([('TEXTCOLOR', (c,r), (c,r), colors.white)]))
    story.append(t_rules)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 4: STUDENT MODULE DIVISION (VIVA DEFENSE)
    # =========================================================================
    story.append(Paragraph("4. Individual Student Module Ownership (Viva Defense Split)", h1_style))
    story.append(Paragraph("Be prepared to defend your respective modules individually during oral questions:", body_style))

    split_data = [
        [
            Paragraph("<b>Student A: Harsh Shukla (<code>E23CSEU0003</code>)</b>", body_style),
            Paragraph("<b>Student B: Akshita Singh (<code>E23CSEU0030</code>)</b>", body_style)
        ],
        [
            Paragraph(
                "• <b>Ingestion Engine (<code>ingest/</code>):</b> Fast PyMuPDF vector extraction, geometric pdfplumber table parser, and Tesseract OCR fallback handling.<br/>"
                "• <b>Extraction Schemas (<code>extract/</code>):</b> Regex token boundary matching, ISO date and float currency normalizers, and privacy masking functions.<br/>"
                "• <b>Rule-Based Validation (<code>validate/</code>):</b> Authored all 10 deterministic checks (<code>VAL_REQ</code>, <code>VAL_NUM</code>, <code>VAL_BNK_REC</code>, <code>VAL_INV_TOT</code>, <code>VAL_FMT</code>) with discrepancy calculations.<br/>"
                "• <b>Backend REST API & SQLite (<code>api/</code>, <code>storage/</code>):</b> Implemented FastAPI endpoints (<code>/upload</code>, <code>/documents</code>, <code>/corrections</code>), relational schemas, cascading keys, and audit logging.",
                body_style
            ),
            Paragraph(
                "• <b>Synthetic Dataset Generator (<code>generator.py</code>):</b> Programmatic generation of 320 PDFs using ReportLab and Faker with fixed seed 70/30 train/test split.<br/>"
                "• <b>Optical Scanner Degradation:</b> Implemented Pillow/NumPy simulation (rotation, Gaussian blur, speckle noise) producing 40 test PNG scans.<br/>"
                "• <b>Dual Classification (<code>classify/</code>):</b> Developed dictionary keyword heuristics and TF-IDF + Logistic Regression ML classifier.<br/>"
                "• <b>Risk Flags & Priority Engine (<code>flags/</code>):</b> Designed explainable anomaly indicators (median outliers, cash withdrawals, bounced entries) and weighted Review Priority.<br/>"
                "• <b>Streamlit UI & Evaluation Benchmarks (<code>app/</code>, <code>evaluate.py</code>):</b> Built interactive dashboard and executed Section 12 benchmark generating all evaluation metrics.",
                body_style
            )
        ]
    ]
    t_split = Table(split_data, colWidths=[250, 254])
    t_split.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('BACKGROUND', (0,1), (0,1), colors.HexColor("#F8FAFC")),
        ('BACKGROUND', (1,1), (1,1), colors.white),
    ]))
    for r in range(1):
        for c in range(2):
            t_split.setStyle(TableStyle([('TEXTCOLOR', (c,r), (c,r), colors.white)]))
    story.append(t_split)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 5: REAL BENCHMARK RESULTS (NUMBERS TO QUOTE)
    # =========================================================================
    story.append(Paragraph("5. Empirical Benchmark Results (Exact Numbers to Quote)", h1_style))
    story.append(Paragraph("Always quote these exact measured numbers from your <code>results/evaluation_summary.csv</code>:", body_style))

    metrics_data = [
        [Paragraph("<b>Evaluation Metric</b>", body_style), Paragraph("<b>Measured Value</b>", body_style), Paragraph("<b>Technical Significance for Examiners</b>", body_style)],
        [Paragraph("Total Test Split Size", body_style), Paragraph("<b>96 documents</b>", body_style), Paragraph("Stratified across Bank Statements (41), Invoices (35), Aadhaar (12), PAN (8).", body_style)],
        [Paragraph("Processing Success Rate", body_style), Paragraph("<b>100.00%</b>", body_style), Paragraph("Zero unhandled exceptions or crashes across all 96 test documents.", body_style)],
        [Paragraph("Average Processing Latency", body_style), Paragraph("<b>42.3 ms / doc</b>", body_style), Paragraph("Ultra-low offline throughput on standard CPU; sub-50ms target met.", body_style)],
        [Paragraph("ML Classification Accuracy", body_style), Paragraph("<b>100.00%</b>", body_style), Paragraph("TF-IDF n-grams + Logistic Regression cleanly separates distinct vocabularies.", body_style)],
        [Paragraph("Baseline Rule Accuracy", body_style), Paragraph("<b>100.00%</b>", body_style), Paragraph("Dictionary keyword density matches ML with 100% consensus.", body_style)],
        [Paragraph("Injected Tampering Recall", body_style), Paragraph("<b>100.0%</b>", body_style), Paragraph("100% recall on balance mismatches and arithmetic invoice errors.", body_style)],
        [Paragraph("Digital PDF Field Accuracy", body_style), Paragraph("<b>87.38%</b>", body_style), Paragraph("Extraction baseline on clean vector digital PDFs.", body_style)],
        [Paragraph("Scanned OCR Field Accuracy", body_style), Paragraph("<b>52.43%</b>", body_style), Paragraph("Extraction accuracy on realistic blurred, rotated, speckle-noisy PNG scans.", body_style)],
        [Paragraph("<b>Key Experiment Accuracy Drop</b>", body_style), Paragraph("<b>-34.95%</b>", body_style), Paragraph("<b>The central empirical finding: optical noise severely impacts OCR token fidelity.</b>", body_style)]
    ]
    t_metrics = Table(metrics_data, colWidths=[140, 100, 264])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    for r in range(1):
        for c in range(3):
            t_metrics.setStyle(TableStyle([('TEXTCOLOR', (c,r), (c,r), colors.white)]))
    story.append(t_metrics)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 6: COMPLETE 25 VIVA QUESTIONS & CRISP ANSWERS
    # =========================================================================
    story.append(Paragraph("6. 25 Likely Evaluator Questions & Defendable Answers", h1_style))
    story.append(Paragraph("Review these 25 questions thoroughly. They represent the most probable questions examiners will pose:", body_style))

    qa_list = [
        ("Q1: Why did you use synthetic data instead of real financial documents?",
         "Real financial documents contain sensitive PII and proprietary banking records protected by RBI regulations and the Digital Personal Data Protection (DPDP) Act. Programmatic synthesis with ReportLab and Faker allows us to establish exact ground-truth values for every single field and inject controlled, labelled tamper faults (~15%) without ethical violations or privacy leaks."),

        ("Q2: Why use a rule-based validation engine instead of an end-to-end deep learning model?",
         "Financial audits demand 100% deterministic mathematical explainability. If an invoice total is wrong, an auditor needs to see the exact arithmetic failure: Subtotal + Tax != Total. Deep learning models are probabilistic black boxes prone to hallucinations and cannot mathematically guarantee arithmetic reconciliation."),

        ("Q3: Why didn't you use LayoutLM or modern multimodal vision-language models?",
         "LayoutLM requires heavy GPU compute, multi-gigabyte weights, and high inference latency. Our engineering goal was a lightweight, offline MVP that runs in under 50 ms on standard commodity student laptops while remaining 100% explainable to evaluators."),

        ("Q4: Why did you avoid cloud OCR services like AWS Textract or Google Cloud Document AI?",
         "Cloud OCR violates our local offline constraint, incurs per-page billing costs, and requires transmitting confidential financial documents over the public internet. We prioritized open-source Tesseract OCR and PyMuPDF to guarantee zero operating cost and complete on-premises data residency."),

        ("Q5: Why is Machine Learning used ONLY for document classification and not extraction?",
         "Classification is an open-vocabulary semantic task where TF-IDF n-grams excels at distinguishing broad vocabulary differences between statements and invoices. Extraction, however, requires exact character boundaries and numbers where regex and positional anchors provide deterministic precision."),

        ("Q6: Why do you strictly avoid the terms 'fraud score' or 'credit score'?",
         "Milestone-1 and AI ethics standards (NIST AI RMF, ISO/IEC 42001) mandate that AI must never make autonomous credit or fraud decisions. We output 'Review Priority' and 'Explainable Indicators' to assist human experts, accompanied by our mandatory disclaimer: 'Indicators only. Human review required.'"),

        ("Q7: How does your bank statement running balance reconciliation work?",
         "Rule VAL_BNK_REC verifies overall reconciliation: |Opening Balance + Deposits - Withdrawals - Closing Balance| <= 0.05. Rule VAL_BNK_RUN_BAL iterates transaction-by-transaction: Previous Balance + Credit - Debit == Stated Balance. Any break immediately flags the exact transaction and discrepancy amount."),

        ("Q8: What was your key empirical finding in the Digital PDF vs Scanned OCR experiment?",
         "On clean digital PDFs, field extraction achieved 87.38% accuracy, but dropped to 52.43% on realistic degraded scans (a -34.95% accuracy degradation). Optical blur, rotation, and speckle noise cause OCR character confusion (e.g. mistaking commas for periods or dropping digits), empirically proving why OCR inputs require confidence penalties and human review."),

        ("Q9: How does the system handle corrupt, empty, or malicious files?",
         "All ingestion functions are wrapped in defensive handlers detecting 0-byte files, invalid extensions, or malformed bytes, returning HTTP 400/422 status codes and graceful user alerts rather than crashing the server (verified across unit tests TC-20 to TC-25)."),

        ("Q10: How does your human-in-the-loop correction workflow work?",
         "In Streamlit or via PUT /documents/{id}/corrections, a human reviewer overrides flawed values. FinDocAI records an immutable audit log in SQLite with old value, new value, reviewer signature, and timestamp, immediately re-runs all 10 validation rules, updates Review Priority, and flips document status to 'CORRECTED'."),

        ("Q11: How do you enforce privacy and data minimization?",
         "The mask_sensitive_value function automatically masks PAN numbers (XXXXX1234F), Aadhaar numbers (XXXX-XXXX-1234), and bank accounts (XXXXXX1234) before committing records to SQLite or logs. In addition, delete_document provides a GDPR / DPDP Act right-to-be-forgotten deletion tool."),

        ("Q12: How did you ensure 70/30 train/test split reproducibility?",
         "In generator.py, we fixed a global random seed (RANDOM_SEED = 42) across Python random, numpy, and Faker. The dataset splits deterministically into 224 training documents and 96 test documents, cataloged in data/dataset_manifest.json."),

        ("Q13: Why does your clean document false-positive rate reach ~60% in evaluation?",
         "Because our statistical outlier rule (FLAG_MEDIAN_OUTLIER) flags legitimate high-value transactions (such as quarterly tax transfers or large bonuses) as review indicators. In financial audit, high recall is prioritized over precision so no suspicious transaction escapes human inspection."),

        ("Q14: How does FinDocAI align with Sustainable Development Goal 9 (SDG 9)?",
         "SDG 9 focuses on Industry, Innovation, and Infrastructure. FinDocAI provides accessible, open-source digital infrastructure automating repetitive financial paperwork, upgrading technological capabilities for small businesses without costly software licenses."),

        ("Q15: How does FinDocAI align with SDG 8 (Decent Work)?",
         "SDG 8 promotes productive employment and decent work. By eliminating tedious manual verification and data entry, FinDocAI reduces cognitive fatigue and human error, enabling accountants and analysts to focus on higher-value financial advisory work."),

        ("Q16: How would this architecture scale to real-world messy documents?",
         "By implementing a template registry: each enterprise vendor's layout is registered with its specific anchor offsets. For un-templated documents, a lightweight layout model (such as quantized LayoutLM ONNX) can serve as a fallback extractor."),

        ("Q17: What is the purpose of field-level confidence scores?",
         "Every extracted field receives a confidence score: 0.95 for primary regex matches, 0.75 for fallback patterns, and a 0.85x penalty multiplier if derived from OCR. This visually alerts the reviewer in Streamlit to direct their manual scrutiny toward low-confidence attributes."),

        ("Q18: What is your database structure and why SQLite?",
         "SQLite is serverless, zero-configuration, and ACID-compliant, ideal for local standalone prototypes. We designed relational tables for documents, extracted_data, validations, review_flags, and corrections with cascading foreign keys."),

        ("Q19: What happens if Tesseract OCR is not installed on the evaluator's machine?",
         "The system checks PATH and common Windows install directories via check_tesseract_installed(). If missing, it prints exact UB-Mannheim download instructions, skips OCR execution, and continues processing digital PDFs without crashing."),

        ("Q20: What are the primary failure modes of the regex extractor?",
         "Multi-line invoice descriptions that wrap across lines, non-standard date formats (e.g., Hijri or Julian calendars), and skewed scanned tables where OCR merges columns together."),

        ("Q21: How do you detect duplicate transactions?",
         "Rule VAL_DUP_TXN hashes transaction reference numbers (ref_no). If duplicate reference numbers appear with identical amounts and dates in the same statement, the rule triggers a failure."),

        ("Q22: How do you calculate Review Priority?",
         "It is a transparent weighted sum of contributing flags: Validation failures (+35), Negative balances (+25), Bounced entries (+20), Median outliers (+15), and Repeated amounts (+15). Capped at 100: Score < 20 is Low, 20–50 is Medium, >= 50 is High."),

        ("Q23: Why did both baseline rules and ML achieve 100% classification accuracy?",
         "Financial documents have highly distinct lexical vocabularies. Bank statements heavily feature words like 'deposit', 'IFSC', 'balance'; invoices feature 'GSTIN', 'subtotal', 'due date'; and KYC documents feature 'Income Tax' or 'UIDAI'. Both keyword sets and TF-IDF vectors separate them cleanly."),

        ("Q24: What are the key limitations of your Milestone-2 MVP?",
         "Lack of support for multi-page balance sheets, inability to perform cross-document reconciliation (e.g. matching an invoice to a bank debit), and reliance on standard templates rather than general-purpose vision models."),

        ("Q25: What is the single most important lesson learned during this project?",
         "That in financial AI systems, transparency and explainability are more important than algorithmic complexity. An auditor will never trust an opaque 99% accuracy claim, but they will readily adopt an assistant that highlights the exact line where numbers fail to add up.")
    ]

    for q, a in qa_list:
        story.append(Paragraph(f"<b>{q}</b>", q_style))
        story.append(Paragraph(f"<b>Answer:</b> {a}", a_style))

    # =========================================================================
    # SECTION 7: DEPENDENCY QUICK REFERENCE
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("7. Project Dependencies & Technical Justifications", h1_style))
    story.append(Paragraph("Be prepared to explain the exact purpose of every library in <code>requirements.txt</code>:", body_style))

    dep_data = [
        [Paragraph("<b>Library</b>", body_style), Paragraph("<b>Exact Technical Purpose in FinDocAI</b>", body_style)],
        [Paragraph("<code>fastapi</code>", body_style), Paragraph("Asynchronous REST API framework powering document upload and review endpoints.", body_style)],
        [Paragraph("<code>uvicorn</code>", body_style), Paragraph("Lightweight, high-performance ASGI production server running FastAPI.", body_style)],
        [Paragraph("<code>streamlit</code>", body_style), Paragraph("Interactive web dashboard for document ingestion, review, and corrections.", body_style)],
        [Paragraph("<code>pymupdf</code> (fitz)", body_style), Paragraph("Ultra-fast sub-20ms vector PDF text, span, and metadata extraction.", body_style)],
        [Paragraph("<code>pdfplumber</code>", body_style), Paragraph("Geometric grid reconstruction of transaction tables from digital bank statements.", body_style)],
        [Paragraph("<code>pytesseract</code>", body_style), Paragraph("Python interface to Tesseract OCR engine for scanned raster image parsing.", body_style)],
        [Paragraph("<code>pillow</code> (PIL)", body_style), Paragraph("Image manipulation and optical scanner degradation simulation (blur/rotation).", body_style)],
        [Paragraph("<code>scikit-learn</code>", body_style), Paragraph("TF-IDF n-gram vectorization and Logistic Regression classification model.", body_style)],
        [Paragraph("<code>reportlab</code>", body_style), Paragraph("Programmatic synthesis of financial PDFs with custom fonts and tables.", body_style)],
        [Paragraph("<code>faker</code>", body_style), Paragraph("Generates realistic synthetic names, addresses, narratives, and bank accounts.", body_style)],
        [Paragraph("<code>pandas</code>", body_style), Paragraph("Tabular processing of transaction ledgers, CSV exports, and metrics dataframes.", body_style)],
        [Paragraph("<code>pydantic</code>", body_style), Paragraph("Data schema validation, type enforcement, and serialization for API requests.", body_style)],
        [Paragraph("<code>pytest</code>", body_style), Paragraph("Automated unit and integration test framework executing all 29 test cases.", body_style)],
        [Paragraph("<code>matplotlib</code>", body_style), Paragraph("Generates publication-ready confusion matrix and accuracy comparison charts.", body_style)]
    ]
    t_dep = Table(dep_data, colWidths=[120, 384])
    t_dep.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    for r in range(1):
        for c in range(2):
            t_dep.setStyle(TableStyle([('TEXTCOLOR', (c,r), (c,r), colors.white)]))
    story.append(t_dep)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Viva Guide PDF successfully created at: {OUTPUT_PDF}")


if __name__ == "__main__":
    create_viva_guide_pdf()
