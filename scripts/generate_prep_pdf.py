"""PDF Generator for FinDocAI Master Preparatory & Evaluator Defense Guide.

Generates a beautifully styled, comprehensive multi-page PDF document
for Harsh Shukla and Akshita Singh to study and present to their Capstone Evaluator.
Group G382: Harsh Shukla, Akshita Singh.
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PDF = BASE_DIR / "docs" / "FinDocAI_Master_Preparatory_Guide.pdf"


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and render total page count."""
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

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#6B7280"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "FinDocAI — Capstone Milestone-2 Evaluator Defense Guide (Group G382)")
            self.setStrokeColor(colors.HexColor("#E5E7EB"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)
        
        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, footer_text)
        self.drawString(54, 36, "Bennett University | B.Tech CSE | Harsh Shukla & Akshita Singh")
        self.setStrokeColor(colors.HexColor("#E5E7EB"))
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)
        
        self.restoreState()


def build_preparatory_pdf():
    """Build the complete master defense guide PDF."""
    os.makedirs(OUTPUT_PDF.parent, exist_ok=True)
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
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#4B5563"),
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0F766E"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1F2937"),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        "CustomBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1F2937"),
        leftIndent=14,
        spaceAfter=3
    )

    disclaimer_style = ParagraphStyle(
        "DisclaimerText",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#92400E")
    )

    story = []

    # ==========================================
    # COVER / HEADER BLOCK
    # ==========================================
    story.append(Paragraph("FinDocAI: Master Evaluator Defense Guide", title_style))
    story.append(Paragraph("Intelligent Financial Document Extraction, Validation and Risk Insights", subtitle_style))
    
    # Metadata Badge Box
    meta_data = [
        [Paragraph("<b>Course:</b> CSET400C Capstone (Milestone-2)", body_style),
         Paragraph("<b>Institution:</b> Bennett University", body_style)],
        [Paragraph("<b>Group ID:</b> G382", body_style),
         Paragraph("<b>Session:</b> Academic Year 2026–2027", body_style)],
        [Paragraph("<b>Student A:</b> Harsh Shukla (E23CSEU0003)", body_style),
         Paragraph("<b>Student B:</b> Akshita Singh (E23CSEU0030)", body_style)],
        [Paragraph("<b>Primary SDG:</b> SDG 9 (Industry & Innovation)", body_style),
         Paragraph("<b>Secondary SDG:</b> SDG 8 (Decent Work)", body_style)],
    ]
    meta_table = Table(meta_data, colWidths=[250, 254])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#93C5FD")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Mandatory Ethical Disclaimer Box
    disc_data = [[
        Paragraph("⚠️ <b>MANDATORY EVALUATOR RULE:</b> FinDocAI produces <b>preliminary review indicators only</b> for human review. It strictly never makes autonomous fraud or credit decisions. Never use 'fraud score' or 'credit score'. Use <b>'Review Priority (Low/Medium/High)'</b> and <b>'Flags'</b>.", disclaimer_style)
    ]]
    disc_table = Table(disc_data, colWidths=[504])
    disc_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF3C7")),
        ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#F59E0B")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(disc_table)
    story.append(Spacer(1, 12))

    # ==========================================
    # SECTION 1: THE BIG PICTURE
    # ==========================================
    story.append(Paragraph("1. The Big Picture: What is FinDocAI and Why Does it Exist?", h1_style))
    story.append(Paragraph(
        "<b>The Problem:</b> Financial institutions process millions of bank statements, tax invoices, and KYC documents daily. "
        "Manual verification is slow, prone to data-entry errors, and struggles with diverse vendor formats and degraded scanned images.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The Solution:</b> FinDocAI is a 100% local, offline, explainable document processing framework. "
        "It ingests digital PDFs and scans, classifies document types, extracts structured schemas, executes 10 mathematical and regulatory validation rules, "
        "surfaces explainable risk indicators, and provides a human-in-the-loop review interface.",
        body_style
    ))

    # ==========================================
    # SECTION 2: STUDENT DIVISION OF OWNERSHIP
    # ==========================================
    story.append(Spacer(1, 8))
    story.append(Paragraph("2. Equal Student Division of Ownership", h1_style))

    split_data = [
        [Paragraph("<b>Student A: Harsh Shukla (E23CSEU0003)</b><br/><i>Core Engineering, Extraction, Validation & Backend</i>", body_style),
         Paragraph("<b>Student B: Akshita Singh (E23CSEU0030)</b><br/><i>Synthetic Data, Classification, Risk Flags & UI</i>", body_style)],
        [
            Paragraph(
                "• <b>Ingestion Engine:</b> PyMuPDF digital text parser, pdfplumber tabular grid parser, and graceful OCR fallback.<br/>"
                "• <b>Extraction Schemas:</b> Regex and layout anchor rules for Bank Statements, Invoices, and KYC documents.<br/>"
                "• <b>Validation Engine:</b> 10 deterministic checks (Opening + Deposits - Withdrawals == Closing, running balances, GST math, regulatory regex).<br/>"
                "• <b>Storage, API & Privacy:</b> SQLite schema with foreign keys, PII masking, correction audit logging, and FastAPI REST endpoints.",
                body_style
            ),
            Paragraph(
                "• <b>Synthetic Dataset Generator:</b> 320 PDFs (ReportLab & Faker) with fixed seed 42 (70/30 split) and 15% labelled tamper faults.<br/>"
                "• <b>Scanner Degradation:</b> 40 degraded scan PNGs simulating tilt (-2.2° to +2.2°), Gaussian blur, and speckle noise.<br/>"
                "• <b>Dual Classification:</b> Keyword rules baseline vs. TF-IDF + Logistic Regression ML model (100% accuracy).<br/>"
                "• <b>Flags & Review Priority:</b> Explainable rules (outliers, repeated amounts, negative balances) + weighted 0-100 score.<br/>"
                "• <b>Streamlit UI & Evaluation:</b> Interactive dashboard with demo buttons, live data editor, and Section 12 benchmark suite.",
                body_style
            )
        ]
    ]
    split_table = Table(split_data, colWidths=[250, 254])
    split_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#EFF6FF")),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#F0FDFA")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#D1D5DB")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
    ]))
    story.append(split_table)

    # ==========================================
    # SECTION 3: KEY EXPERIMENTAL FINDINGS
    # ==========================================
    story.append(Spacer(1, 12))
    story.append(Paragraph("3. The Key Experiment & Measured Benchmark Results", h1_style))
    story.append(Paragraph(
        "<b>The Key Experiment (Digital PDF vs. Scanned OCR):</b> Evaluated on 40 test documents to prove the real-world impact of scanner degradation.",
        body_style
    ))

    exp_data = [
        ["Modality / Document Type", "Correct Fields", "Total Fields", "Measured Accuracy (%)", "Key Finding / Significance"],
        ["Clean Digital PDF", "180", "206", "87.38%", "High baseline on native vector PDFs"],
        ["Degraded Scanned OCR", "108", "206", "52.43%", "Degraded by blur, rotation, and noise"],
        ["OCR Performance Drop", "-", "-", "-34.95%", "Key Finding: Proves necessity of OCR confidence penalty & human review"],
        ["Bank Statements (Digital)", "205", "205", "100.00%", "Perfect extraction on structured tabular ledgers"],
        ["Tax Invoices (Digital)", "175", "210", "83.33%", "High accuracy across varying line-item layouts"],
        ["Injected Fault Detection", "13", "13", "100.00%", "100% recall on balance/total tamper faults"],
        ["Document Processing Speed", "-", "-", "42.3 ms/doc", "Sub-50ms execution enables real-time interactive review"],
        ["Automated Pytest Suite", "29", "29", "100.00%", "29 passed tests covering edge cases & corrupt files"]
    ]
    exp_table = Table(exp_data, colWidths=[130, 60, 55, 95, 164])
    exp_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (1, 0), (3, -1), "CENTER"),
    ]))
    story.append(exp_table)

    # ==========================================
    # SECTION 4: 5-MINUTE LIVE DEMO SCRIPT
    # ==========================================
    story.append(Spacer(1, 12))
    story.append(Paragraph("4. The 5-Minute Evaluator Live Demo Walkthrough", h1_style))

    demo_data = [
        ["Time", "Speaker", "Action / Screen", "Exact Spoken Lines to Say to the Evaluator"],
        ["0:00 - 0:45", "Harsh", "Run 'python run_pipeline.py'. Point to top amber banner.",
         "Notice our ethical disclaimer banner: 'Indicators only. Human review required.' FinDocAI supports human experts; it strictly never outputs credit or fraud scores. The pipeline runs 100% offline."],
        ["0:45 - 1:45", "Akshita", "Click '🟢 Load Clean Bank Statement' in sidebar.",
         "Our dual classifier identifies Bank Statement with 100% consensus between Keyword Rules and TF-IDF ML. All 10 validation rules pass (green banner). Review Priority is Low (Score: 0/100)."],
        ["1:45 - 3:00", "Harsh", "Click '🔴 Load Tampered Bank Statement' in sidebar.",
         "Notice: Status flips to red FAIL. Under rule VAL_BNK_REC, it explains: 'Closing balance of INR 99,999.00 does not match calculated balance of INR 55,000.00 (Discrepancy: INR 44,999.00)'. Review Priority jumps to High (Score: 65/100)."],
        ["3:00 - 4:00", "Akshita", "Tab 3: Edit Closing Balance to 55,000.0. Click Save & Re-Validate.",
         "This demonstrates our human-in-the-loop workflow. The reviewer enters the corrected balance. SQLite logs an audit trail, immediately re-runs validation, status flips to PASS, and Priority drops to Low."],
        ["4:00 - 5:00", "Both", "Tab 4: Export JSON/CSV. Sidebar: Evaluation Metrics.",
         "Reviewer exports normalized JSON or CSV for downstream accounting. Our benchmark shows 100% test success and proves scanner blur causes a 34.95% OCR accuracy drop. All 29 unit tests pass."]
    ]
    demo_table = Table(demo_data, colWidths=[60, 48, 140, 256])
    demo_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F766E")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0FDFA")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(demo_table)

    # ==========================================
    # SECTION 5: TOP EVALUATOR DEFENSE QUESTIONS
    # ==========================================
    story.append(Spacer(1, 12))
    story.append(Paragraph("5. Top 10 Evaluator Questions & Defenses", h1_style))

    qa_list = [
        ("Q1: Why synthetic data instead of real financial documents?",
         "Real financial documents contain confidential PII protected under RBI guidelines and the DPDP Act. Scraping them risks privacy violations. Furthermore, real documents lack ground truth for running balances. By generating 320 synthetic documents using ReportLab and Faker with fixed seed 42, we know the exact ground truth for every line item and could inject controlled, labelled tamper faults to benchmark our validation accuracy."),
        
        ("Q2: Why didn't you use LayoutLM or an LLM like ChatGPT?",
         "LayoutLM and LLMs require multi-gigabyte models, GPUs, paid APIs, or cloud infrastructure. Our requirement was a 100% offline system that runs in 42 ms on any laptop. More importantly, financial audits require mathematical explainability—an LLM cannot guarantee that Opening + Deposits - Withdrawals == Closing. Our rule-based validation engine provides deterministic, hallucination-free mathematical proof with an exact Rule ID."),
        
        ("Q3: Why is Machine Learning used ONLY for classification and not extraction?",
         "Classification is an open-vocabulary text categorization task where TF-IDF n-grams excels at separating vocabulary differences between bank statements and invoices. In contrast, extraction requires capturing exact alphanumeric formats (like a 10-digit PAN or an 11-digit IFSC), where regular expressions and layout anchors provide deterministic precision."),
        
        ("Q4: Why is your clean document false-positive rate ~60%?",
         "In financial audit, high recall is prioritized over precision. Our explainable rule FLAG_MEDIAN_OUTLIER flags legitimate high-value transactions (such as quarterly rent or salary) for reviewer verification. Auditors prefer inspecting 10 legitimate large transactions rather than letting 1 suspicious transaction slip by unflagged."),
        
        ("Q5: What happens if Tesseract OCR is not installed on the system?",
         "We implemented defensive graceful degradation in src/findoc/ingest/ocr_engine.py. The system checks PATH and standard Windows install paths. If missing, it does not crash or throw unhandled exceptions. Instead, it provides clear instructions for downloading the UB-Mannheim installer, while digital PDF processing remains 100% functional."),

        ("Q6: How do you protect sensitive personal data (Privacy)?",
         "Under src/findoc/storage/privacy.py, all sensitive identifiers are sanitized: PAN numbers are masked (ABXXXXXX4F), Aadhaar numbers are masked (XXXX XXXX 1234), and bank account numbers retain only the last 4 digits (XXXXXXXX9012). Plaintext PII is never committed to application logs, and delete_document provides a right-to-be-forgotten deletion feature."),

        ("Q7: How does FinDocAI align with Sustainable Development Goals?",
         "SDG 9 (Industry, Innovation & Infrastructure): Upgrades technological capabilities for small accounting firms and credit co-operatives by providing an open-source, offline document verification pipeline without expensive enterprise software licenses. SDG 8 (Decent Work): Eliminates tedious manual data entry and mental arithmetic, preventing cognitive fatigue and human error for data-entry operators."),

        ("Q8: How does your bank statement running balance reconciliation work?",
         "Rule VAL_BNK_REC verifies two levels: first, Opening Balance + Total Deposits - Total Withdrawals == Closing Balance (within 0.05 tolerance). Second, VAL_BNK_RUN_BAL iterates transaction-by-transaction: Previous Balance + Credit - Debit == Stated Balance. Any break immediately flags the exact transaction and discrepancy."),

        ("Q9: What are the primary limitations of your current MVP?",
         "Multi-page balance sheets and income statements are not yet supported due to complex Ind-AS accounting schedules; cross-document reconciliation (e.g. 3-way matching an invoice to a purchase order and a bank debit) is deferred to future work; and heavily degraded mobile camera photos degrade Tesseract OCR accuracy, demonstrating the necessity of human review."),

        ("Q10: What is the single most important lesson learned during this project?",
         "In financial AI systems, transparency and explainability are more important than algorithmic complexity. An auditor will never trust an opaque 99% accuracy claim, but they will readily adopt an assistant that highlights the exact line where numbers fail to add up.")
    ]

    for q, a in qa_list:
        story.append(Paragraph(f"<b>{q}</b>", h2_style))
        story.append(Paragraph(a, body_style))

    # ==========================================
    # SECTION 6: QUICK REFERENCE CHEAT-SHEET
    # ==========================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("6. Quick Reference Cheat-Sheet", h1_style))

    cheat_data = [
        ["Key Concept / Item", "Exact Value / Details", "Key Concept / Item", "Exact Value / Details"],
        ["Run Everything", "python run_pipeline.py", "Database Path", "data/findoc.db (SQLite)"],
        ["Streamlit App", "http://localhost:8501", "FastAPI Docs", "http://localhost:8000/docs"],
        ["Pytest Suite", "python -m pytest tests/ -v (29 passed)", "Test Documents", "96 docs (from 320, seed 42)"],
        ["Processing Speed", "42.3 ms / doc (Offline)", "Key Drop (OCR)", "-34.95% on degraded scans"],
        ["PAN Regex", "^[A-Z]{5}[0-9]{4}[A-Z]{1}$ (10 chars)", "IFSC Regex", "^[A-Z]{4}0[A-Z0-9]{6}$ (11 chars)"],
        ["Aadhaar Regex", "^[2-9][0-9]{11}$ (12 digits)", "GSTIN Regex", "^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$ (15 chars)"]
    ]
    cheat_table = Table(cheat_data, colWidths=[110, 142, 110, 142])
    cheat_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4B5563")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(cheat_table)

    # Build document with custom dynamic canvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated Master Preparatory PDF at: {OUTPUT_PDF}")


if __name__ == "__main__":
    build_preparatory_pdf()
