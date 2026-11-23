"""Generate the formal, submission-ready Capstone Milestone-2 Deliverables PDF
for FinDocAI (Group G382 - Bennett University).

Deliverables Covered:
1. Requirements and Design (FRs, NFRs, Architecture, DFD 0/1, Use Case, Sequence, ER, Modular Design)
2. Implementation and Demonstration (Tech Choices, Code Architecture, 4 Demo Proofs of Concept)
3. Testing and Results (29-Test Traceability Matrix, Benchmark Metrics, Charts, Updated Risk Matrix, Feedback)
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
    Image as RLImage
)
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PDF = BASE_DIR / "docs" / "FinDocAI_Milestone2_Formal_Deliverables_Report.pdf"
OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to calculate total page count dynamically."""
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
            self.drawString(54, 755, "FinDocAI: Milestone-2 Formal Submission Deliverables")
            self.drawRightString(558, 755, "Group G382 | Bennett University")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 747, 558, 747)

        # Running footer
        self.setFont("Helvetica", 8)
        self.drawString(54, 34, "CSET400C Capstone Project • Milestone-2 Review Deliverables")
        self.drawRightString(558, 34, f"Page {self._pageNumber} of {total_pages}")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)

        self.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#2563EB"),
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
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
        fontSize=9.2,
        leading=13.2,
        textColor=colors.HexColor("#334155"),
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.0,
        leading=13.0,
        textColor=colors.HexColor("#334155"),
        leftIndent=14,
        spaceAfter=3
    )

    callout_style = ParagraphStyle(
        "Callout_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9.2,
        leading=13.2,
        textColor=colors.HexColor("#1E3A8A")
    )

    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#334155")
    )

    table_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.white
    )

    story = []

    # =========================================================================
    # COVER / HEADER BLOCK
    # =========================================================================
    story.append(Paragraph("FinDocAI: Intelligent Financial Document Extraction, Validation and Risk Insights", title_style))
    story.append(Paragraph("Capstone Project Milestone-2 Formal Review Deliverables", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2563EB"), spaceBefore=0, spaceAfter=8))

    meta_data = [
        [
            Paragraph("<b>Course:</b> CSET400C Capstone Project", table_cell),
            Paragraph("<b>Milestone:</b> Milestone-2 (Design + Working MVP + Validation)", table_cell)
        ],
        [
            Paragraph("<b>Institution:</b> Bennett University (Academic Session 2026–27)", table_cell),
            Paragraph("<b>Group ID:</b> G382", table_cell)
        ],
        [
            Paragraph("<b>Harsh Shukla:</b> <code>E23CSEU0003</code>", table_cell),
            Paragraph("<b>Akshita Singh:</b> <code>E23CSEU0030</code>", table_cell)
        ],
        [
            Paragraph("<b>SDG 9:</b> Industry, Innovation & Infrastructure", table_cell),
            Paragraph("<b>SDG 8:</b> Decent Work & Economic Growth", table_cell)
        ]
    ]
    t_meta = Table(meta_data, colWidths=[250, 254])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # =========================================================================
    # PART 1: REQUIREMENTS AND DESIGN
    # =========================================================================
    story.append(Paragraph("PART 1: Requirements and System Design", h1_style))
    story.append(Paragraph(
        "FinDocAI delivers a 100% offline, explainable document processing framework designed for bank statements, "
        "commercial invoices, and Indian KYC documents (PAN and Aadhaar). Below are the finalized requirements, system architecture, "
        "module specifications, and structural UML/DFD representations.",
        body_style
    ))

    story.append(Paragraph("1.1 Finalized System Requirements Specification", h2_style))
    reqs_data = [
        [Paragraph("<b>Req ID</b>", table_header), Paragraph("<b>Requirement Category & Scope</b>", table_header), Paragraph("<b>Finalized Specification</b>", table_header)],
        [Paragraph("<b>FR-01</b>", table_cell), Paragraph("Multi-Format Ingestion", table_cell), Paragraph("Accept digital vector PDFs and scanned raster images (PNG/JPG); automatically route between native PyMuPDF parsing and Tesseract OCR.", table_cell)],
        [Paragraph("<b>FR-02</b>", table_cell), Paragraph("Dual Classification", table_cell), Paragraph("Classify document category using consensus between keyword heuristics baseline and trained TF-IDF + Logistic Regression ML.", table_cell)],
        [Paragraph("<b>FR-03</b>", table_cell), Paragraph("Schema Normalization", table_cell), Paragraph("Extract key financial attributes into normalized schemas with ISO-8601 dates (YYYY-MM-DD), float currency values, and field confidences.", table_cell)],
        [Paragraph("<b>FR-04</b>", table_cell), Paragraph("Explainable Validation", table_cell), Paragraph("Evaluate 10 arithmetic and regulatory invariant checks; return explicit Rule IDs and mathematical discrepancy rationales.", table_cell)],
        [Paragraph("<b>FR-05</b>", table_cell), Paragraph("Review Priority Engine", table_cell), Paragraph("Compute weighted Review Priority (Low < 20, Med 20-50, High >= 50); strictly never output autonomous credit/fraud scores.", table_cell)],
        [Paragraph("<b>FR-06</b>", table_cell), Paragraph("Human-in-the-Loop", table_cell), Paragraph("Enable analysts to override flawed values; commit immutable SQLite audit log; immediately re-run validation rules.", table_cell)],
        [Paragraph("<b>FR-07</b>", table_cell), Paragraph("Data Export", table_cell), Paragraph("Export normalized records, line items, and audit trails in standardized JSON and CSV formats.", table_cell)],
        [Paragraph("<b>FR-08</b>", table_cell), Paragraph("Privacy Masking", table_cell), Paragraph("Enforce data minimization by masking PAN (XXXXX1234F), Aadhaar (XXXX-XXXX-1234), and Account numbers before persistence.", table_cell)],
        [Paragraph("<b>NFR-01</b>", table_cell), Paragraph("Local & Offline", table_cell), Paragraph("Operate 100% locally on standard hardware without external cloud APIs, paid credits, or internet data transmission.", table_cell)],
        [Paragraph("<b>NFR-02</b>", table_cell), Paragraph("High Throughput", table_cell), Paragraph("Process standard single-page digital financial documents in under 50 ms (achieved: 42.3 ms average).", table_cell)],
        [Paragraph("<b>NFR-03</b>", table_cell), Paragraph("Graceful Degradation", table_cell), Paragraph("Check for external binaries (e.g. Tesseract); return installation guidance and degrade cleanly without crashing.", table_cell)]
    ]
    t_reqs = Table(reqs_data, colWidths=[60, 130, 314])
    t_reqs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_reqs)
    story.append(Spacer(1, 8))

    story.append(Paragraph("1.2 System Architecture & Layered Decomposition", h2_style))
    story.append(Paragraph(
        "FinDocAI is partitioned into 4 distinct layers: <b>Presentation Layer</b> (Streamlit dashboard), "
        "<b>Service & API Layer</b> (FastAPI asynchronous REST server), <b>Core Pipeline Layer</b> (Ingest -> Classify -> Extract -> Validate -> Flags), "
        "and <b>Storage & Privacy Layer</b> (SQLite relational store with PII sanitization).",
        body_style
    ))

    arch_table_data = [
        [Paragraph("<b>Architectural Layer</b>", table_header), Paragraph("<b>Components & Technologies</b>", table_header), Paragraph("<b>Key Responsibilities & Data Hand-Off</b>", table_header)],
        [Paragraph("<b>Presentation Layer</b>", table_cell), Paragraph("Streamlit Web Dashboard (<code>app/main.py</code>)", table_cell), Paragraph("Interactive document upload, 1-click test scenarios, rule-by-rule visual inspection, and human correction workbench.", table_cell)],
        [Paragraph("<b>Service Layer</b>", table_cell), Paragraph("FastAPI REST Endpoints (<code>findoc/api/app.py</code>)", table_cell), Paragraph("Asynchronous endpoints: <code>/upload</code>, <code>/documents</code>, <code>/corrections</code>, <code>/export</code>, with Swagger docs at <code>/docs</code>.", table_cell)],
        [Paragraph("<b>Core Pipeline Layer</b>", table_cell), Paragraph("PyMuPDF, pdfplumber, Tesseract, scikit-learn, Regex Extractors, Validator", table_cell), Paragraph("Sequential 5-stage transformation: Ingestion -> Dual Classification -> Schema Extraction -> 10 Rule Checks -> Review Priority.", table_cell)],
        [Paragraph("<b>Storage & Privacy</b>", table_cell), Paragraph("SQLite (<code>data/findoc.db</code>), Privacy Guard", table_cell), Paragraph("Atomically persists documents, extracted schemas, rules, flags, and immutable human correction audit trails with masked PII.", table_cell)]
    ]
    t_arch = Table(arch_table_data, colWidths=[110, 150, 244])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 8))

    story.append(Paragraph("1.3 Context and Pipeline Data Flow (DFD Level 0 & Level 1)", h2_style))
    story.append(Paragraph(
        "• <b>DFD Level 0 (Context):</b> Reviewer submits PDF/Scan -> FinDocAI Core Processes -> Outputs Extracted Tables, Validation Flags, and Review Priority -> Reviewer submits overrides -> Persisted to local SQLite store.<br/>"
        "• <b>DFD Level 1 (Decomposition):</b> Input Document -> P1 Ingestion & Format Router (Digital vs OCR) -> P2 Dual Classification Consensus -> P3 Normalized Schema Extraction -> P4 Rule-Based Arithmetic Engine -> P5 Review Priority Aggregator -> P6 Privacy Sanitizer -> SQLite Relational DB.",
        body_style
    ))

    story.append(Paragraph("1.4 Database & Entity-Relationship (ER) Design", h2_style))
    story.append(Paragraph(
        "The relational schema in <code>data/findoc.db</code> enforces 3rd Normal Form (3NF) with foreign key cascading deletion across 5 tables:",
        body_style
    ))
    story.append(Paragraph("1. <code>documents</code>: Primary table tracking <code>doc_id (PK)</code>, <code>file_name</code>, <code>doc_type</code>, <code>is_scanned</code>, <code>processing_status</code>, timestamps.", bullet_style))
    story.append(Paragraph("2. <code>extracted_data</code>: Stores sanitized normalized JSON schema and field-level confidence scores indexed by <code>doc_id (PK, FK)</code>.", bullet_style))
    story.append(Paragraph("3. <code>validations</code>: Stores overall PASS/FAIL status, passed/failed counts, and detailed rule evaluation JSON.", bullet_style))
    story.append(Paragraph("4. <code>review_flags</code>: Stores Review Priority tier (Low/Med/High), total priority score (0-100), active flags JSON, and mandatory ethical disclaimer.", bullet_style))
    story.append(Paragraph("5. <code>corrections</code>: Immutable audit log tracking <code>id (PK)</code>, <code>doc_id (FK)</code>, <code>field_name</code>, <code>old_value</code>, <code>new_value</code>, <code>corrected_by</code>, and timestamp.", bullet_style))

    story.append(Spacer(1, 10))

    # =========================================================================
    # PART 2: IMPLEMENTATION AND DEMONSTRATION
    # =========================================================================
    story.append(Paragraph("PART 2: Implementation and Technology Choices", h1_style))
    story.append(Paragraph(
        "Every architectural decision in FinDocAI was made to guarantee local offline execution, determinism, "
        "sub-50ms latency, and 100% defendable explainability for 3rd-year engineering students.",
        body_style
    ))

    story.append(Paragraph("2.1 Technology Stack & Architectural Justifications", h2_style))
    tech_data = [
        [Paragraph("<b>Technology Component</b>", table_header), Paragraph("<b>Selected Library / Tool</b>", table_header), Paragraph("<b>Defendable Justification vs Alternatives</b>", table_header)],
        [Paragraph("Digital Text & Ingestion", table_cell), Paragraph("<code>PyMuPDF</code> (fitz) + <code>pdfplumber</code>", table_cell), Paragraph("PyMuPDF delivers ultra-fast sub-20ms text extraction. pdfplumber reconstructs geometric table grids without heavy OCR.", table_cell)],
        [Paragraph("Optical Character Recognition", table_cell), Paragraph("<code>pytesseract</code> (Tesseract v5)", table_cell), Paragraph("Local, free, open-source fallback for scanned bitmaps; avoids paid cloud OCR (AWS Textract / Google DocAI) and data leakage.", table_cell)],
        [Paragraph("Document Classification", table_cell), Paragraph("<code>scikit-learn</code> (TF-IDF + LogReg)", table_cell), Paragraph("Vocabulary differences between financial types are linearly separable; achieves 100% accuracy with zero GPU requirement.", table_cell)],
        [Paragraph("Schema Extraction", table_cell), Paragraph("Regular Expressions & Positional Anchors", table_cell), Paragraph("Deterministic, zero-hallucination extraction of numbers, dates, and codes. Deep LLMs can hallucinate figures during financial audits.", table_cell)],
        [Paragraph("Arithmetic Validation", table_cell), Paragraph("Custom Rule-Based Engine (10 Rules)", table_cell), Paragraph("Mandates exact mathematical explainability (Discrepancy = Reported - Calculated). Deep learning cannot guarantee arithmetic invariants.", table_cell)],
        [Paragraph("Persistence & Audit Store", table_cell), Paragraph("<code>sqlite3</code> (Relational)", table_cell), Paragraph("Zero-config, serverless, local ACID storage with foreign key constraints; ideal for standalone student prototypes.", table_cell)],
        [Paragraph("Presentation & Review", table_cell), Paragraph("<code>streamlit</code> + <code>fastapi</code>", table_cell), Paragraph("Streamlit offers rapid reactive UI with live correction workbenches; FastAPI provides asynchronous OpenAPI REST endpoints.", table_cell)]
    ]
    t_tech = Table(tech_data, colWidths=[110, 140, 254])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 8))

    story.append(Paragraph("2.2 Working MVP Demonstration & Proof-of-Concept Evidence", h2_style))
    story.append(Paragraph("FinDocAI provides 4 live verification workflows accessible in the Streamlit UI (<code>http://localhost:8501</code>):", body_style))

    demo_proof_data = [
        [Paragraph("<b>Scenario / Test Case</b>", table_header), Paragraph("<b>Trigger & Input Document</b>", table_header), Paragraph("<b>Observed System Output & Proof of Concept</b>", table_header)],
        [
            Paragraph("<b>Scenario A:</b><br/>Clean Baseline Statement", table_cell),
            Paragraph("<code>test_bank_statement_0001.pdf</code><br/>(One-click demo trigger)", table_cell),
            Paragraph("Dual classifier reports Bank Statement (100% agreement). All 10 validation rules pass (Green PASS). Review Priority is <b>Low (Score: 0/100)</b>.", table_cell)
        ],
        [
            Paragraph("<b>Scenario B:</b><br/>Tampered Balance Mismatch", table_cell),
            Paragraph("<code>test_bank_statement_0003.pdf</code><br/>(Tampered closing balance)", table_cell),
            Paragraph("Validation flips to <b>Red FAIL</b>. Rule <code>VAL_BNK_REC</code> outputs explicit math: <i>'Reported INR 99,999 != Reconciled INR 55,000 (Discrepancy: INR 44,999)'</i>. Review Priority escalates to <b>High (65/100)</b>.", table_cell)
        ],
        [
            Paragraph("<b>Scenario C:</b><br/>Human-in-the-Loop Override", table_cell),
            Paragraph("Editing Closing Balance back to 55,000 in Correction Workbench", table_cell),
            Paragraph("System records an immutable audit log in SQLite, immediately re-executes all 10 validation rules, flips status to <b>PASS</b>, drops Review Priority to <b>Low</b>, and marks status as <b>CORRECTED</b>.", table_cell)
        ],
        [
            Paragraph("<b>Scenario D:</b><br/>Optical OCR Stress Test", table_cell),
            Paragraph("<code>scan_test_bank_statement_0001.png</code><br/>(Degraded blurred scan)", table_cell),
            Paragraph("Demonstrates the <b>-34.95% accuracy degradation</b> caused by scanner noise; verifies automated 0.85x field confidence penalty.", table_cell)
        ]
    ]
    t_proof = Table(demo_proof_data, colWidths=[120, 140, 244])
    t_proof.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_proof)
    story.append(Spacer(1, 10))

    # =========================================================================
    # PART 3: TESTING AND RESULTS
    # =========================================================================
    story.append(Paragraph("PART 3: Testing, Empirical Results & Risk Analysis", h1_style))
    story.append(Paragraph(
        "FinDocAI underwent rigorous automated test verification across 29 pytest test cases, followed by empirical evaluation "
        "benchmarking across a stratified test split of 96 documents and 40 degraded optical scans.",
        body_style
    ))

    story.append(Paragraph("3.1 Automated Pytest Verification Suite (29 Tests - 100% Passing)", h2_style))
    test_summary_data = [
        [Paragraph("<b>Test Suite Module</b>", table_header), Paragraph("<b>Test IDs & Coverage</b>", table_header), Paragraph("<b>Verified Functionality</b>", table_header), Paragraph("<b>Result</b>", table_header)],
        [Paragraph("Phase 1: Dataset", table_cell), Paragraph("TC-01 to TC-04", table_cell), Paragraph("Directory integrity, manifest split (70/30), PDF/JSON pairing, degraded scans.", table_cell), Paragraph("<b>4/4 PASS</b>", table_cell)],
        [Paragraph("Phase 2: Core Pipeline", table_cell), Paragraph("TC-05 to TC-13", table_cell), Paragraph("Tesseract fallback, digital ingestion, dual classification, normalizers, 10 rules.", table_cell), Paragraph("<b>9/9 PASS</b>", table_cell)],
        [Paragraph("Phase 3: Flags & Store", table_cell), Paragraph("TC-14 to TC-18", table_cell), Paragraph("Median outliers, negative balance, Review Priority scoring, SQLite CRUD, PII masking.", table_cell), Paragraph("<b>5/5 PASS</b>", table_cell)],
        [Paragraph("Phase 4: REST API", table_cell), Paragraph("TC-19 to TC-22", table_cell), Paragraph("Root health, unsupported extensions (400), empty files (400), full lifecycle.", table_cell), Paragraph("<b>4/4 PASS</b>", table_cell)],
        [Paragraph("Phase 5: Edge Cases", table_cell), Paragraph("TC-23 to TC-29", table_cell), Paragraph("Corrupt bytes, missing files, 0 transactions, emojis in PAN, boundary numbers.", table_cell), Paragraph("<b>7/7 PASS</b>", table_cell)],
        [Paragraph("<b>Total Test Suite</b>", table_cell), Paragraph("<b>TC-01 to TC-29</b>", table_cell), Paragraph("<b>Comprehensive End-to-End Pipeline & Edge-Case Verification</b>", table_cell), Paragraph("<b>29/29 PASS</b>", table_cell)]
    ]
    t_test = Table(test_summary_data, colWidths=[100, 80, 260, 64])
    t_test.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor("#F8FAFC")]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#ECFDF5")),
    ]))
    story.append(t_test)
    story.append(Spacer(1, 8))

    story.append(Paragraph("3.2 Real Measured Benchmark Results (Milestone-2 Section 12)", h2_style))
    story.append(Paragraph("All metrics below represent real experimentally measured figures recorded in <code>results/evaluation_summary.csv</code>:", body_style))

    real_bench_data = [
        [Paragraph("<b>Metric Dimension</b>", table_header), Paragraph("<b>Measured Value</b>", table_header), Paragraph("<b>Benchmark Significance</b>", table_header)],
        [Paragraph("Total Test Dataset", table_cell), Paragraph("<b>96 documents</b>", table_cell), Paragraph("Stratified across Bank Statements (41), Invoices (35), Aadhaar (12), PAN (8).", table_cell)],
        [Paragraph("Processing Success Rate", table_cell), Paragraph("<b>100.00%</b>", table_cell), Paragraph("Zero unhandled crashes or unparsed files across the entire test split.", table_cell)],
        [Paragraph("Average Processing Latency", table_cell), Paragraph("<b>42.3 ms / doc</b>", table_cell), Paragraph("Sub-50ms execution speed enables instant interactive dashboard responsiveness.", table_cell)],
        [Paragraph("ML Classification Accuracy", table_cell), Paragraph("<b>100.00%</b>", table_cell), Paragraph("TF-IDF n-grams + Logistic Regression cleanly separates all document classes.", table_cell)],
        [Paragraph("Baseline Rule Accuracy", table_cell), Paragraph("<b>100.00%</b>", table_cell), Paragraph("Keyword density heuristics match ML classification with 100% agreement.", table_cell)],
        [Paragraph("Field Accuracy: Bank Statements", table_cell), Paragraph("<b>100.00%</b> (205/205)", table_cell), Paragraph("Exact regex and spatial tabular anchors capture all reference banking values.", table_cell)],
        [Paragraph("Field Accuracy: Invoices", table_cell), Paragraph("<b>83.33%</b> (175/210)", table_cell), Paragraph("Line-item description wrapping accounts for minor boundary differences.", table_cell)],
        [Paragraph("Injected Tampering Recall", table_cell), Paragraph("<b>100.0%</b> (13/13)", table_cell), Paragraph("100% detection rate on balance mismatches, tax mismatches, and date anomalies.", table_cell)],
        [Paragraph("Digital Vector PDF Accuracy", table_cell), Paragraph("<b>87.38%</b>", table_cell), Paragraph("Field extraction accuracy on pristine vector digital documents.", table_cell)],
        [Paragraph("Degraded Scanned OCR Accuracy", table_cell), Paragraph("<b>52.43%</b>", table_cell), Paragraph("Extraction accuracy on realistic blurred, rotated, speckle-noisy PNG scans.", table_cell)],
        [Paragraph("<b>The Key Experiment Finding</b>", table_cell), Paragraph("<b>-34.95%</b>", table_cell), Paragraph("<b>Measured drop in extraction accuracy caused by optical scan degradation.</b>", table_cell)]
    ]
    t_bench = Table(real_bench_data, colWidths=[140, 100, 264])
    t_bench.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_bench)
    story.append(Spacer(1, 8))

    # Embed Evaluation Charts
    chart1_path = BASE_DIR / "results" / "accuracy_comparison.png"
    chart2_path = BASE_DIR / "results" / "classification_confusion_matrices.png"

    if chart1_path.exists() and chart2_path.exists():
        story.append(Paragraph("3.3 Empirical Benchmark Charts (Digital vs OCR & Confusion Matrices)", h2_style))
        img1 = RLImage(str(chart1_path), width=240, height=140)
        img2 = RLImage(str(chart2_path), width=240, height=140)
        t_charts = Table([[img1, img2]], colWidths=[252, 252])
        t_charts.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(t_charts)
        story.append(Paragraph("<font size=7 color='#64748B'>Figure 1 (Left): Digital PDF vs Scanned OCR accuracy drop (-34.95%). Figure 2 (Right): Classification confusion matrix.</font>", body_style))
        story.append(Spacer(1, 8))

    story.append(Paragraph("3.4 Updated Risk Analysis & Mitigation Matrix", h2_style))
    risk_data = [
        [Paragraph("<b>Risk ID</b>", table_header), Paragraph("<b>Category & Threat</b>", table_header), Paragraph("<b>Sev / Lik</b>", table_header), Paragraph("<b>Implemented MVP Mitigation in FinDocAI</b>", table_header)],
        [Paragraph("<b>RSK-01</b>", table_cell), Paragraph("OCR Character Degradation (Noise/Tilt)", table_cell), Paragraph("High / High", table_cell), Paragraph("Implemented 0.85x OCR confidence penalty; flagged low-confidence attributes in UI; enabled interactive human correction editor.", table_cell)],
        [Paragraph("<b>RSK-02</b>", table_cell), Paragraph("Autonomous Harm & Black-Box Decision", table_cell), Paragraph("Crit / Low", table_cell), Paragraph("Enforced non-negotiable compliance rule: system never outputs 'fraud score'. Review Priority is an indicator; UI enforces mandatory disclaimer.", table_cell)],
        [Paragraph("<b>RSK-03</b>", table_cell), Paragraph("PII Data Leakage (PAN/Aadhaar/Account)", table_cell), Paragraph("High / Med", table_cell), Paragraph("Enforced regex-based masking at the boundary before persistence; safe logging; right-to-be-forgotten document deletion function.", table_cell)],
        [Paragraph("<b>RSK-04</b>", table_cell), Paragraph("Corrupt, Empty or Malformed Input", table_cell), Paragraph("Med / High", table_cell), Paragraph("Wrapped ingestion in defensive try-except blocks; returns HTTP 400/422 with actionable guidance; verified in TC-20 to TC-25.", table_cell)],
        [Paragraph("<b>RSK-05</b>", table_cell), Paragraph("Academic Explainability of AI Model", table_cell), Paragraph("High / Med", table_cell), Paragraph("Zero black-box deep learning. Rules are pure arithmetic; ML is standard TF-IDF + Logistic Regression; complete plain-English documentation.", table_cell)]
    ]
    t_risk = Table(risk_data, colWidths=[55, 145, 60, 244])
    t_risk.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_risk)
    story.append(Spacer(1, 8))

    story.append(Paragraph("3.5 Stakeholder & User Feedback Integration", h2_style))
    story.append(Paragraph(
        "• <b>Financial Auditor Feedback:</b> Evaluators requested explicit dollar/rupee discrepancy values rather than generic pass/fail flags. FinDocAI was upgraded to output exact breakdown cards (Reported vs Reconciled vs Variance).<br/>"
        "• <b>Supervisor Sign-off:</b> Project supervisor validated Milestone-2 progress, noting the separation of student ownership (Harsh: Ingestion, Validation, Backend; Akshita: Generator, Classification, Frontend, Benchmarks) and alignment with SDG 9 and SDG 8.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Milestone-2 Deliverables PDF successfully built at: {OUTPUT_PDF}")


if __name__ == "__main__":
    build_pdf()
