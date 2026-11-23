"""Generate a clean, conversational, practical Hinglish Viva Script PDF for FinDocAI.
Designed for students to explain to evaluators 'upar upar se' covering every UI feature without deep tech jargon.
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
    HRFlowable,
    KeepTogether
)
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PDF = BASE_DIR / "docs" / "FinDocAI_Hinglish_Viva_Script.pdf"
OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)


class NumberedCanvas(canvas.Canvas):
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

        if self._pageNumber > 1:
            self.drawString(54, 755, "FinDocAI: Viva Voce Speaking Script (Hinglish Guide)")
            self.drawRightString(558, 755, "Group G382 • Capstone Milestone-2")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 747, 558, 747)

        self.setFont("Helvetica", 8)
        self.drawString(54, 34, "FinDocAI • Evaluator Defense Script • Bennett University")
        self.drawRightString(558, 34, f"Page {self._pageNumber} of {total_pages}")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)

        self.restoreState()


def build_hinglish_pdf():
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
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#2563EB"),
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    dialogue_style = ParagraphStyle(
        "DialogueStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.2,
        leading=13.5,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=5
    )

    action_style = ParagraphStyle(
        "ActionStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#2563EB"),
        spaceAfter=2
    )

    tip_style = ParagraphStyle(
        "TipStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#475569")
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("FinDocAI: Viva Speaking Script in Hinglish", title_style))
    story.append(Paragraph("Evaluator ko 'Upar-Upar Se' Explain Karne Ka Complete Step-by-Step Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceBefore=0, spaceAfter=8))

    meta_table_data = [
        [Paragraph("<b>Course:</b> CSET400C Capstone (Milestone-2)", dialogue_style), Paragraph("<b>Group ID:</b> G382", dialogue_style)],
        [Paragraph("<b>Harsh Shukla:</b> E23CSEU0003", dialogue_style), Paragraph("<b>Akshita Singh:</b> E23CSEU0030", dialogue_style)],
        [Paragraph("<b>Target Audience:</b> External / Internal Evaluators", dialogue_style), Paragraph("<b>Tone:</b> Simple, Confident, UI-Focused (No heavy math/tech)", dialogue_style)]
    ]
    t_meta = Table(meta_table_data, colWidths=[250, 254])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 8))

    # SECTION 1: INTRODUCTION
    story.append(Paragraph("1. Starting / Introduction: Evaluator Ko Pehle 1 Minute Me Kya Bolna Hai", h1_style))
    story.append(Paragraph("<b>Sirf itna confidently bolna hai:</b>", action_style))

    p1 = (
        "\"Good morning Sir / Ma'am. Humara project hai <b>FinDocAI</b> – Intelligent Financial Document Extraction, Validation and Risk Insights.<br/><br/>"
        "<b>Problem kya thi?</b><br/>"
        "Sir, banks, loan departments aur CA firms me roz hazaron Bank Statements, Invoices aur KYC documents aate hain. "
        "Log inko manually baithkar check karte hain. Isme do badi dikkat aati hai:<br/>"
        "1. Bahut zyada time waste hota hai aur human error hone ka darr rehta hai.<br/>"
        "2. Sabse bada risk – agar kisi document me number tampered hai (jaise closing balance fake likha hai ya invoice ka tax total galat hai), "
        "toh manually wo pakad me nahi aata.<br/><br/>"
        "<b>Humne kya banaya? (Solution):</b><br/>"
        "FinDocAI ek simple, fast aur <b>100% offline tool</b> hai. Yeh koi bhi PDF ya photo leta hai, khud identify karta hai ki document Bank Statement hai, "
        "Invoice hai ya PAN/Aadhaar hai, uska saara data clean format me nikalta hai, aur sabse important cheez – <b>10 rule-based arithmetic checks lagata hai</b>. "
        "Agar document me 1 rupaye ka bhi balance mismatch hai, toh yeh red alert dekar clearly batata hai ki kitne ka discrepancy hai. "
        "Aur saath hi humne human reviewer ke liye edit aur correction ka option bhi diya hai taaki human-in-the-loop audit trail maintain ho sake.\""
    )
    story.append(Paragraph(p1, dialogue_style))
    story.append(Spacer(1, 6))

    # SECTION 2: UI WALKTHROUGH FEATURE BY FEATURE
    story.append(Paragraph("2. Live UI Walkthrough: Screen Par Ek-Ek Feature Dikhate Hue Kya Bolna Hai", h1_style))
    story.append(Paragraph("<i>(Ab aap apna browser open karenge <code>http://localhost:8501</code> par aur ek-ek cheez point karenge)</i>", tip_style))
    story.append(Spacer(1, 4))

    # Feature 2.1
    story.append(Paragraph("Feature 1: Top Compliance Banner (Ethical AI Mandate)", h2_style))
    story.append(Paragraph("<b>Screen par dikhayein:</b> Top par yellow/amber disclaimer banner.", action_style))
    story.append(Paragraph(
        "\"Sir sabse pehle dekhiye, screen ke top par humne ek mandatory compliance banner lagaya hai: "
        "<i>'Indicators only. Human review required.'</i><br/>"
        "Yeh isliye important hai kyunki humara system kabhi bhi khud se koi autonomous 'fraud score' ya 'credit decision' nahi deta. "
        "Yeh tool human expert ko assist karne ke liye hai, unka replacement nahi hai. Final decision hamesha human analyst ka hi hota hai.\"",
        dialogue_style
    ))

    # Feature 2.2
    story.append(Paragraph("Feature 2: Document Intake & Quick Demo Buttons", h2_style))
    story.append(Paragraph("<b>Screen par dikhayein:</b> File Uploader aur Sidebar me 5 Quick Demo buttons.", action_style))
    story.append(Paragraph(
        "\"Yahan user apni koi bhi real PDF ya image file drag-and-drop karke upload kar sakta hai.<br/>"
        "Lekin testing aur live evaluation ko aasan banane ke liye, humne sidebar me 5 quick demo buttons diye hain: "
        "Clean Bank Statement, Tampered Statement, Tampered Invoice, KYC Document aur Scanned Image test. "
        "Bas 1 click karte hi document turant process ho jata hai bina kisi delay ke.\"",
        dialogue_style
    ))

    # Feature 2.3
    story.append(Paragraph("Feature 3: Executive Summary Cards (Top 4 KPIs)", h2_style))
    story.append(Paragraph("<b>Screen par dikhayein:</b> Document load hote hi upar aane wale 4 boxes.", action_style))
    story.append(Paragraph(
        "\"Jaise hi document process hota hai, top par 4 summary cards aate hain:<br/>"
        "• <b>1. Document Classification:</b> System batata hai document kya hai (jaise Bank Statement) aur model ka confidence.<br/>"
        "• <b>2. Review Priority:</b> Score 0 se 100 ke beech hota hai. Agar document clean hai toh 'Low Priority' (Green), agar tampering mili toh 'High Priority' (Red).<br/>"
        "• <b>3. Validation Health:</b> 10 me se kitne checks pass hue (e.g. 10/10 checks PASS ya FAIL).<br/>"
        "• <b>4. Processing Speed:</b> Real-time speed dikhata hai – sirf 42 ms ke andar processing complete ho jati hai!\"",
        dialogue_style
    ))

    # Feature 2.4: Tab 1
    story.append(Paragraph("Feature 4: Tab 1 – Rule-by-Rule Validation Engine (Humara Core Feature)", h2_style))
    story.append(Paragraph("<b>Action:</b> Sidebar me <b>'🔴 Tampered Statement (Math Fail)'</b> dabayein aur Tab 1 dikhayein.", action_style))
    story.append(Paragraph(
        "\"Sir dekhiye, maine tampered statement load kiya. Validation status turant red <b>FAIL</b> ho gaya.<br/>"
        "Neeche rule <code>VAL_BNK_REC</code> dekhiye – humara system sirf 'Error' bolkar nahi chodta, balki explicit reason explain karta hai:<br/>"
        "<i>'Reported value hai INR 99,999, jabki saare transactions jodkar calculated balance hona chahiye INR 55,000 – isme exact INR 44,999 ka discrepancy hai!'</i><br/>"
        "Evaluator ko turant pata chal jata hai ki document me kis jagah par fraud ya mismatch hai.\"",
        dialogue_style
    ))

    # Feature 2.5: Tab 2
    story.append(Paragraph("Feature 5: Tab 2 – Structured Ledger & Extracted Data", h2_style))
    story.append(Paragraph("<b>Action:</b> Tab 2 par click karein.", action_style))
    story.append(Paragraph(
        "\"Is tab me pura extracted data clean table aur summary format me aa jata hai:<br/>"
        "• Bank account number, opening balance, deposits aur closing balance.<br/>"
        "• Niche pura Transaction Ledger table hai, jisme Credits green me aur Debits red me highlighted hain.<br/>"
        "• Agar hum Invoice load karte hain, toh Line Items, GST amounts aur vendor names aate hain.<br/>"
        "• Aur agar PAN ya Aadhaar load karte hain, toh humne ek digital physical card container banaya hai jisme Government headers aur masked ID number dikhta hai.\"",
        dialogue_style
    ))

    # Feature 2.6: Tab 3
    story.append(Paragraph("Feature 6: Tab 3 – Human-in-the-Loop Review & Instant Re-validation", h2_style))
    story.append(Paragraph("<b>Action:</b> Tab 3 me jakar Closing Balance ko 55000 karein aur Save button dabayein.", action_style))
    story.append(Paragraph(
        "\"Sir yeh humara sabse impactful feature hai – <b>Human-in-the-Loop</b>.<br/>"
        "Real life me agar OCR se koi digit misread ho gaya, toh human analyst is screen par us field ko manually edit kar sakta hai. "
        "Jaise hi maine closing balance ko wapas 55,000 kiya, reason select kiya aur Save dabaya – system ne turant do cheezein ki:<br/>"
        "1. Database me audit trail save kar liya ki kis user ne purani value badalkar nayi value daali.<br/>"
        "2. Saari validation rules turant re-calculate hui aur status wapas <b>PASS (Green)</b> ho gaya!\"",
        dialogue_style
    ))

    # Feature 2.7: Tab 4
    story.append(Paragraph("Feature 7: Tab 4 – Export & Payloads", h2_style))
    story.append(Paragraph("<b>Action:</b> Tab 4 par download buttons dikhayein.", action_style))
    story.append(Paragraph(
        "\"Verified document ko analyst 1-click me normalized <b>JSON</b> ya <b>CSV</b> me export kar sakta hai, "
        "taaki wo data direct Tally, SAP ya banking software me import ho sake.\"",
        dialogue_style
    ))

    # Feature 2.8: Other Pages
    story.append(Paragraph("Feature 8: Sidebar Ke Baaki 3 Pages", h2_style))
    story.append(Paragraph("<b>Sidebar se teeno pages upar-upar se dikhayein:</b>", action_style))
    story.append(Paragraph(
        "• <b>Audit Trail & History:</b> Database me saved saare past processed documents ki list aur kisne kya edit kiya uska pura history log dikhta hai.<br/>"
        "• <b>Evaluation Benchmarks:</b> Yahan humara key experiment hai – digital PDF me accuracy 87% hoti hai, lekin degraded scanned photo me drop hokar 52% ho jaati hai (34.95% drop). Isliye hum OCR par confidence penalty lagate hain.<br/>"
        "• <b>System & Privacy:</b> Privacy compliance ke liye PAN, Aadhaar aur Account number auto-mask rehte hain, aur Right-to-be-Forgotten ke under agar koi data delete karna chahe toh 1-click me permanent purge kar sakta hai.",
        dialogue_style
    ))

    # SECTION 3: FREQUENT EVALUATOR QUESTIONS
    story.append(Spacer(1, 6))
    story.append(Paragraph("3. Evaluator Agar Yeh Pooche Toh 1 Line Me Kya Bolna Hai", h1_style))

    q_data = [
        [
            Paragraph("<b>Evaluator Ka Question</b>", action_style),
            Paragraph("<b>Aapko Simple 1-Line Me Kya Jawab Dena Hai</b>", action_style)
        ],
        [
            Paragraph("<b>Q: AI model kya use kiya hai?</b>", dialogue_style),
            Paragraph("\"Sir document classification ke liye humne TF-IDF aur Logistic Regression use kiya hai jo 100% accuracy deta hai, aur validation ke liye 10 deterministic arithmetic rules banayi hain taaki mathematical explainability guarantee ho sake.\"", dialogue_style)
        ],
        [
            Paragraph("<b>Q: Real bank statements kyun nahi use kiye?</b>", dialogue_style),
            Paragraph("\"Sir RBI aur DPDP Act privacy laws ke according real customer data bina permission use karna illegal hai, isliye humne realistic synthetic data generate kiya taaki controlled tampering inject karke benchmark measure kiya ja sake.\"", dialogue_style)
        ],
        [
            Paragraph("<b>Q: Cloud AI (jaise AWS ya OpenAI) kyun nahi use kiya?</b>", dialogue_style),
            Paragraph("\"Sir cloud APIs me sensitive financial data internet par jata hai aur per-page cost lagti hai. Humne 100% local open-source pipeline banayi hai jo standard laptop par offline 42 ms me run karti hai zero cost par.\"", dialogue_style)
        ],
        [
            Paragraph("<b>Q: Aap dono me work divide kaise tha?</b>", dialogue_style),
            Paragraph("\"Harsh ne Ingestion, Regex Extraction, Validation Rules, SQLite database aur backend banaya hai; Akshita ne Dataset Generator, Optical Scan degradation, ML Classification, Review Priority aur Streamlit UI banaya hai.\"", dialogue_style)
        ]
    ]
    t_q = Table(q_data, colWidths=[180, 324])
    t_q.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_q)

    # FINAL CLOSING
    story.append(Spacer(1, 8))
    story.append(Paragraph("4. Final Closing Line (Apna Demo End Karte Hue)", h1_style))
    p_end = (
        "\"Sir, upar-upar se humara project ek fast, explainable financial assistant hai jo boring manual verification ko automate karta hai, "
        "arithmetic cheating aur errors ko instant pakadta hai, aur human reviewer ko full control deta hai. Thank you sir, we are open to questions!\""
    )
    t_end = Table([[Paragraph(p_end, dialogue_style)]], colWidths=[504])
    t_end.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1.2, colors.HexColor("#3B82F6")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_end)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Hinglish Viva Script PDF successfully created at: {OUTPUT_PDF}")


if __name__ == "__main__":
    build_hinglish_pdf()
