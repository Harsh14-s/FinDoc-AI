"""Synthetic Financial Document Generator for FinDocAI.

Generates realistic, multi-template Bank Statements, Invoices, and KYC documents (PAN / Aadhaar)
as PDF files with paired ground-truth JSON files.
Includes labelled tamper injections (~15%) and degraded scanned PNGs for OCR evaluation.
Group G382: Harsh Shukla, Akshita Singh.
"""

import os
import json
import random
import math
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
from pathlib import Path

from faker import Faker
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
import pymupdf

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Frame, PageTemplate
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


# Fixed random seed for complete experimental reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
fake = Faker(locale="en_IN")
Faker.seed(RANDOM_SEED)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
GT_DIR = DATA_DIR / "ground_truth"
SCANS_DIR = DATA_DIR / "degraded_scans"

BANKS = [
    {"name": "Apex National Bank", "ifsc_prefix": "APEX", "branch": "Connaught Place, New Delhi"},
    {"name": "State Mercantile Commercial Bank", "ifsc_prefix": "SMCB", "branch": "Bandra Kurla Complex, Mumbai"},
    {"name": "Beacon Cooperative Urban Bank", "ifsc_prefix": "BCOB", "branch": "MG Road, Bengaluru"},
    {"name": "Metro Alliance Bank", "ifsc_prefix": "METR", "branch": "Sector 62, Noida"},
]

VENDORS = [
    {"name": "Vortex Tech Solutions Pvt Ltd", "gstin": "07AAAAA1234A1Z5", "category": "IT & Cloud Services"},
    {"name": "Apex Logistics & Supply Chain Ltd", "gstin": "27BBBBB5678B1Z2", "category": "Freight & Warehousing"},
    {"name": "Pinnacle Advisory & Consulting LLP", "gstin": "29CCCCC9012C1Z8", "category": "Professional Services"},
    {"name": "BlueSky Office Supplies Pvt Ltd", "gstin": "09DDDDD3456D1Z1", "category": "Office Equipment"},
]

INVOICE_ITEMS = [
    ("Cloud Server Hosting - Monthly", 4500.0),
    ("Software License Subscription", 12000.0),
    ("IT Consulting & Architecture Hours", 25000.0),
    ("Logistics Freight Handling Services", 8500.0),
    ("Warehouse Pallet Storage Fee", 6200.0),
    ("Ergonomic Mesh Office Chairs", 7500.0),
    ("Network Security Audit & Patching", 18000.0),
    ("Data Backup Storage (5TB Tier)", 3500.0),
]


def format_currency(val: float, fmt_type: int = 0) -> str:
    """Format numeric values with varying currency symbols and decimal styles."""
    val = round(val, 2)
    if fmt_type == 0:
        return f"INR {val:,.2f}"
    elif fmt_type == 1:
        return f"Rs. {val:,.2f}"
    else:
        return f"{val:,.2f}"


def format_date_str(dt: datetime, fmt_type: int = 0) -> str:
    """Format date objects into different common enterprise date formats."""
    if fmt_type == 0:
        return dt.strftime("%Y-%m-%d")
    elif fmt_type == 1:
        return dt.strftime("%d/%m/%Y")
    else:
        return dt.strftime("%d-%b-%Y")


def generate_bank_statement_data(doc_id: str, is_tampered: bool, tamper_type: str = "none") -> Dict[str, Any]:
    """Generate structured synthetic bank statement data and ground truth."""
    bank = random.choice(BANKS)
    account_num = str(random.randint(10000000000, 99999999999))
    ifsc = f"{bank['ifsc_prefix']}0{random.randint(100000, 999999)}"
    holder_name = fake.name()

    base_date = datetime(2025, random.randint(1, 10), 1)
    period_start = base_date
    period_end = base_date + timedelta(days=random.randint(28, 31))

    opening_balance = round(random.uniform(25000.0, 150000.0), 2)
    current_balance = opening_balance

    num_txns = random.randint(8, 14)
    transactions = []
    total_deposits = 0.0
    total_withdrawals = 0.0

    current_tx_date = period_start
    descriptions = [
        "UPI-TRANSFER-SALARY", "ATM-CASH-WITHDRAWAL", "NEFT-INWARD-REMITTANCE",
        "POS-RETAIL-GROCERY", "ELECTRICITY-BILL-PAYMENT", "INTEREST-CREDIT",
        "UPI-SWIGGY-FOOD", "ONLINE-SHOPPING-AMZN", "FIXED-DEPOSIT-INTEREST",
        "IMPS-PEER-TRANSFER"
    ]

    for i in range(num_txns):
        day_inc = random.randint(1, 2)
        current_tx_date = min(current_tx_date + timedelta(days=day_inc), period_end)
        desc = random.choice(descriptions)
        is_credit = ("CREDIT" in desc or "SALARY" in desc or "REMITTANCE" in desc or random.random() < 0.35)
        amount = round(random.uniform(500.0, 35000.0), 2)

        if is_credit:
            debit = 0.0
            credit = amount
            current_balance += credit
            total_deposits += credit
        else:
            debit = amount
            credit = 0.0
            current_balance -= debit
            total_withdrawals += debit

        ref_no = f"TXN{random.randint(10000000, 99999999)}"
        transactions.append({
            "date": format_date_str(current_tx_date, random.randint(0, 2)),
            "raw_date": current_tx_date.strftime("%Y-%m-%d"),
            "description": desc,
            "ref_no": ref_no,
            "debit": debit,
            "credit": credit,
            "balance": round(current_balance, 2)
        })

    closing_balance = round(current_balance, 2)
    total_deposits = round(total_deposits, 2)
    total_withdrawals = round(total_withdrawals, 2)

    tamper_details = []
    if is_tampered:
        if tamper_type == "balance_mismatch":
            # Tamper the closing balance so opening + deposits - withdrawals != closing
            closing_balance = round(closing_balance + random.choice([5000.0, -12500.0, 7800.0]), 2)
            tamper_details.append("balance_mismatch: closing balance altered")
        elif tamper_type == "future_dates":
            # Inject a future transaction date (e.g., year 2029)
            future_dt = datetime(2029, 6, 15)
            transactions[-1]["date"] = format_date_str(future_dt, 0)
            transactions[-1]["raw_date"] = "2029-06-15"
            tamper_details.append("future_dates: transaction date 2029-06-15 after period end")
        elif tamper_type == "duplicate_transactions":
            # Duplicate the second transaction exactly
            dup_tx = dict(transactions[1])
            transactions.insert(2, dup_tx)
            tamper_details.append(f"duplicate_transactions: ref_no {dup_tx['ref_no']} duplicated")

    return {
        "document_id": doc_id,
        "document_type": "bank_statement",
        "bank_name": bank["name"],
        "branch": bank["branch"],
        "ifsc": ifsc,
        "account_holder": holder_name,
        "account_number": account_num,
        "period_start": period_start.strftime("%Y-%m-%d"),
        "period_end": period_end.strftime("%Y-%m-%d"),
        "opening_balance": opening_balance,
        "closing_balance": closing_balance,
        "total_deposits": total_deposits,
        "total_withdrawals": total_withdrawals,
        "transactions": transactions,
        "is_tampered": is_tampered,
        "tamper_types": tamper_details
    }


def generate_invoice_data(doc_id: str, is_tampered: bool, tamper_type: str = "none") -> Dict[str, Any]:
    """Generate structured synthetic tax invoice data and ground truth."""
    vendor = random.choice(VENDORS)
    client_name = fake.company()
    client_gstin = f"07{fake.bothify(text='?????####?#?#').upper()}"
    inv_num = f"INV-2025-{random.randint(1001, 9999)}"

    inv_date = datetime(2025, random.randint(1, 10), random.randint(1, 28))
    due_date = inv_date + timedelta(days=30)

    num_items = random.randint(2, 5)
    selected_items = random.sample(INVOICE_ITEMS, num_items)
    items = []
    subtotal = 0.0

    for desc, unit_p in selected_items:
        qty = random.randint(1, 5)
        line_total = round(qty * unit_p, 2)
        subtotal += line_total
        items.append({
            "description": desc,
            "quantity": qty,
            "unit_price": unit_p,
            "total": line_total
        })

    subtotal = round(subtotal, 2)
    tax_rate = 0.18  # 18% GST (9% CGST + 9% SGST)
    tax_amount = round(subtotal * tax_rate, 2)
    grand_total = round(subtotal + tax_amount, 2)

    tamper_details = []
    if is_tampered:
        if tamper_type == "total_mismatch":
            # Grand total does not match subtotal + tax
            grand_total = round(grand_total + random.choice([2500.0, -1800.0, 4200.0]), 2)
            tamper_details.append("total_mismatch: grand total does not match subtotal + tax")
        elif tamper_type == "future_dates":
            future_dt = datetime(2030, 4, 1)
            inv_date = future_dt
            due_date = future_dt + timedelta(days=30)
            tamper_details.append("future_dates: invoice date 2030-04-01 is far in the future")
        elif tamper_type == "invalid_gstin":
            # Malformed GSTIN: wrong length and invalid characters
            vendor = dict(vendor)
            vendor["gstin"] = "INVALID#GST#999"
            tamper_details.append("invalid_gstin: vendor GSTIN violates 15-character standard pattern")

    return {
        "document_id": doc_id,
        "document_type": "invoice",
        "vendor_name": vendor["name"],
        "vendor_gstin": vendor["gstin"],
        "vendor_category": vendor["category"],
        "client_name": client_name,
        "client_gstin": client_gstin,
        "invoice_number": inv_num,
        "invoice_date": inv_date.strftime("%Y-%m-%d"),
        "due_date": due_date.strftime("%Y-%m-%d"),
        "line_items": items,
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "tax_rate": "18%",
        "grand_total": grand_total,
        "is_tampered": is_tampered,
        "tamper_types": tamper_details
    }


def generate_kyc_data(doc_id: str, kyc_type: str, is_tampered: bool, tamper_type: str = "none") -> Dict[str, Any]:
    """Generate structured synthetic KYC data (PAN or Aadhaar) and ground truth."""
    full_name = fake.name()
    father_name = fake.name_male()
    dob = datetime(random.randint(1975, 2003), random.randint(1, 12), random.randint(1, 28))

    tamper_details = []
    if kyc_type == "pan_card":
        # Standard PAN format: 5 uppercase letters, 4 digits, 1 uppercase letter (e.g., ABCDE1234F)
        prefix = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=5))
        digits = f"{random.randint(1000, 9999)}"
        suffix = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        pan_num = f"{prefix}{digits}{suffix}"

        if is_tampered and tamper_type == "invalid_pan_format":
            # Alter to invalid format (e.g., missing letter or digits)
            pan_num = f"INVALID{random.randint(10, 99)}"
            tamper_details.append("invalid_pan_format: PAN violates 10-char alphanumeric regex")

        return {
            "document_id": doc_id,
            "document_type": "pan_card",
            "full_name": full_name,
            "father_name": father_name,
            "dob": dob.strftime("%Y-%m-%d"),
            "pan_number": pan_num,
            "is_tampered": is_tampered,
            "tamper_types": tamper_details
        }
    else:  # Aadhaar card
        # Standard Aadhaar format: 12 digits (formatted as XXXX XXXX XXXX)
        part1 = f"{random.randint(2000, 9999)}"
        part2 = f"{random.randint(1000, 9999)}"
        part3 = f"{random.randint(1000, 9999)}"
        aadhaar_num = f"{part1} {part2} {part3}"
        gender = random.choice(["Male", "Female", "Other"])
        address = fake.address().replace("\n", ", ")

        if is_tampered and tamper_type == "invalid_aadhaar_format":
            # Invalid Aadhaar: only 8 digits or letters included
            aadhaar_num = f"9999 ABCD {random.randint(100, 999)}"
            tamper_details.append("invalid_aadhaar_format: Aadhaar contains alphabets and incorrect length")

        return {
            "document_id": doc_id,
            "document_type": "aadhaar_card",
            "full_name": full_name,
            "gender": gender,
            "dob": dob.strftime("%Y-%m-%d"),
            "aadhaar_number": aadhaar_num,
            "address": address,
            "is_tampered": is_tampered,
            "tamper_types": tamper_details
        }


# ==========================================
# REPORTLAB PDF RENDERING FUNCTIONS
# ==========================================

def render_bank_statement_pdf(data: Dict[str, Any], filepath: Path):
    """Render a realistic, multi-template Bank Statement PDF."""
    doc = SimpleDocTemplate(str(filepath), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    elements = []

    # Title & Header
    bank_title = Paragraph(f"<b><font size='16' color='#1E3A8A'>{data['bank_name']}</font></b>", styles["Normal"])
    branch_sub = Paragraph(f"<font size='9' color='#4B5563'>Branch: {data['branch']} | IFSC: {data['ifsc']}</font>", styles["Normal"])
    elements.extend([bank_title, branch_sub, Spacer(1, 10)])

    # Account Summary Box
    summary_data = [
        [Paragraph(f"<b>Account Holder:</b> {data['account_holder']}", styles["Normal"]),
         Paragraph(f"<b>Account Number:</b> {data['account_number']}", styles["Normal"])],
        [Paragraph(f"<b>Statement Period:</b> {data['period_start']} to {data['period_end']}", styles["Normal"]),
         Paragraph(f"<b>Opening Balance:</b> {format_currency(data['opening_balance'])}", styles["Normal"])],
        [Paragraph(f"<b>Total Deposits:</b> {format_currency(data['total_deposits'])}", styles["Normal"]),
         Paragraph(f"<b>Closing Balance:</b> <b>{format_currency(data['closing_balance'])}</b>", styles["Normal"])],
    ]
    summary_table = Table(summary_data, colWidths=[270, 270])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F4F6")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#D1D5DB")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.extend([summary_table, Spacer(1, 15)])

    # Transactions Header
    elements.append(Paragraph("<b><font size='11' color='#1F2937'>Transaction Activity</font></b>", styles["Normal"]))
    elements.append(Spacer(1, 6))

    # Transactions Table
    tx_rows = [["Date", "Description", "Ref / Chq No", "Withdrawal (Dr)", "Deposit (Cr)", "Balance"]]
    for tx in data["transactions"]:
        dr_str = format_currency(tx["debit"]) if tx["debit"] > 0 else "-"
        cr_str = format_currency(tx["credit"]) if tx["credit"] > 0 else "-"
        bal_str = format_currency(tx["balance"])
        tx_rows.append([
            tx["date"],
            tx["description"][:28],
            tx["ref_no"],
            dr_str,
            cr_str,
            bal_str
        ])

    tx_table = Table(tx_rows, colWidths=[65, 145, 95, 80, 80, 75])
    tx_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(tx_table)

    # Disclaimer Footer
    elements.append(Spacer(1, 15))
    footer = Paragraph("<font size='7' color='#9CA3AF'>* This is a computer-generated bank statement. For verification, contact branch customer support.</font>", styles["Normal"])
    elements.append(footer)

    doc.build(elements)


def render_invoice_pdf(data: Dict[str, Any], filepath: Path):
    """Render a realistic, multi-template Tax Invoice PDF."""
    doc = SimpleDocTemplate(str(filepath), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    elements = []

    # Title & Vendor Info
    header_data = [
        [Paragraph(f"<b><font size='16' color='#0F766E'>{data['vendor_name']}</font></b><br/><font size='8' color='#4B5563'>GSTIN: {data['vendor_gstin']}<br/>Sector: {data['vendor_category']}</font>", styles["Normal"]),
         Paragraph(f"<b><font size='14' color='#111827'>TAX INVOICE</font></b><br/><font size='9'><b>Invoice No:</b> {data['invoice_number']}<br/><b>Date:</b> {data['invoice_date']}<br/><b>Due Date:</b> {data['due_date']}</font>", styles["Normal"])]
    ]
    header_table = Table(header_data, colWidths=[300, 240])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.extend([header_table, Spacer(1, 10)])

    # Billed To Section
    bill_data = [
        [Paragraph(f"<b>BILLED TO:</b><br/>{data['client_name']}<br/>GSTIN: {data['client_gstin']}", styles["Normal"])]
    ]
    bill_table = Table(bill_data, colWidths=[540])
    bill_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0FDFA")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CCFBF1")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.extend([bill_table, Spacer(1, 15)])

    # Line Items Table
    item_rows = [["#", "Item Description", "Qty", "Unit Price (INR)", "Amount (INR)"]]
    for idx, item in enumerate(data["line_items"], start=1):
        item_rows.append([
            str(idx),
            item["description"],
            str(item["quantity"]),
            f"{item['unit_price']:,.2f}",
            f"{item['total']:,.2f}"
        ])

    items_table = Table(item_rows, colWidths=[30, 270, 50, 100, 90])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F766E")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.extend([items_table, Spacer(1, 10)])

    # Summary Table (Subtotal, Tax, Grand Total)
    summary_data = [
        ["", "Subtotal:", f"INR {data['subtotal']:,.2f}"],
        ["", f"GST ({data['tax_rate']}):", f"INR {data['tax_amount']:,.2f}"],
        ["", "Grand Total:", f"INR {data['grand_total']:,.2f}"],
    ]
    summary_table = Table(summary_data, colWidths=[290, 130, 120])
    summary_table.setStyle(TableStyle([
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("FONTSIZE", (1, 0), (-1, -1), 9),
        ("FONTNAME", (1, 2), (-1, 2), "Helvetica-Bold"),
        ("LINEABOVE", (1, 2), (-1, 2), 1, colors.HexColor("#111827")),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.extend([summary_table, Spacer(1, 20)])

    doc.build(elements)


def render_kyc_pdf(data: Dict[str, Any], filepath: Path):
    """Render a synthetic KYC card PDF (PAN or Aadhaar style)."""
    doc = SimpleDocTemplate(str(filepath), pagesize=letter, leftMargin=72, rightMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()

    elements = []

    if data["document_type"] == "pan_card":
        header_p = Paragraph("<b><font size='13' color='#831843'>INCOME TAX DEPARTMENT - GOVT. OF INDIA</font></b>", styles["Normal"])
        sub_p = Paragraph("<font size='9' color='#374151'>Permanent Account Number (PAN) Card</font>", styles["Normal"])
        elements.extend([header_p, sub_p, Spacer(1, 15)])

        card_data = [
            [Paragraph("<b>Permanent Account Number (PAN):</b>", styles["Normal"]),
             Paragraph(f"<b><font size='12' color='#1E3A8A'>{data['pan_number']}</font></b>", styles["Normal"])],
            [Paragraph("<b>Name:</b>", styles["Normal"]),
             Paragraph(data["full_name"], styles["Normal"])],
            [Paragraph("<b>Father's Name:</b>", styles["Normal"]),
             Paragraph(data["father_name"], styles["Normal"])],
            [Paragraph("<b>Date of Birth:</b>", styles["Normal"]),
             Paragraph(data["dob"], styles["Normal"])],
        ]
        card_table = Table(card_data, colWidths=[200, 260])
        card_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FDF2F8")),
            ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#BE185D")),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(card_table)

    else:  # Aadhaar card
        header_p = Paragraph("<b><font size='13' color='#1E3A8A'>UNIQUE IDENTIFICATION AUTHORITY OF INDIA</font></b>", styles["Normal"])
        sub_p = Paragraph("<font size='9' color='#374151'>Aadhaar - Government of India</font>", styles["Normal"])
        elements.extend([header_p, sub_p, Spacer(1, 15)])

        card_data = [
            [Paragraph("<b>Aadhaar Number:</b>", styles["Normal"]),
             Paragraph(f"<b><font size='13' color='#B91C1C'>{data['aadhaar_number']}</font></b>", styles["Normal"])],
            [Paragraph("<b>Resident Name:</b>", styles["Normal"]),
             Paragraph(data["full_name"], styles["Normal"])],
            [Paragraph("<b>Gender:</b>", styles["Normal"]),
             Paragraph(data["gender"], styles["Normal"])],
            [Paragraph("<b>Date of Birth:</b>", styles["Normal"]),
             Paragraph(data["dob"], styles["Normal"])],
            [Paragraph("<b>Address:</b>", styles["Normal"]),
             Paragraph(data["address"], styles["Normal"])],
        ]
        card_table = Table(card_data, colWidths=[150, 310])
        card_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
            ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#2563EB")),
            ("PADDING", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(card_table)

    elements.append(Spacer(1, 15))
    elements.append(Paragraph("<font size='7' color='#9CA3AF'>* Synthetic sample generated for FinDocAI academic evaluation purposes only.</font>", styles["Normal"]))

    doc.build(elements)


def create_degraded_scan(pdf_path: Path, output_png_path: Path):
    """Render PDF to PNG and inject realistic scanner degradations: blur, noise, slight tilt."""
    doc = pymupdf.open(str(pdf_path))
    page = doc.load_page(0)
    pix = page.get_pixmap(dpi=150)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # 1. Slight realistic rotation (-2.0 to +2.0 degrees) with white background
    angle = random.uniform(-2.2, 2.2)
    img = img.rotate(angle, resample=Image.BICUBIC, expand=False, fillcolor=(255, 255, 255))

    # 2. Mild Gaussian Blur (simulates optical lens imperfection)
    img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 0.9)))

    # 3. Add light salt-and-pepper / scanner speckle noise
    arr = np.array(img).astype(np.float32)
    noise = np.random.normal(0, 7.0, arr.shape)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)

    # 4. Slight contrast variation
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(random.uniform(0.85, 1.15))

    img.save(str(output_png_path), format="PNG")


def generate_all_datasets(total_docs: int = 320, train_ratio: float = 0.70):
    """Generate 320 synthetic documents (Bank Statements, Invoices, KYC) with 70/30 split and degraded scans."""
    os.makedirs(RAW_DIR / "train", exist_ok=True)
    os.makedirs(RAW_DIR / "test", exist_ok=True)
    os.makedirs(GT_DIR / "train", exist_ok=True)
    os.makedirs(GT_DIR / "test", exist_ok=True)
    os.makedirs(SCANS_DIR, exist_ok=True)

    # Document quotas:
    # 120 Bank Statements (core, deepest support)
    # 120 Invoices (core)
    # 40 PAN Cards (light KYC)
    # 40 Aadhaar Cards (light KYC)
    # Total = 320 documents
    # Tampered: ~15% overall (approx 50 documents)

    specs = []
    # 1. Bank statements: 120 total, 20 tampered
    for i in range(120):
        is_tampered = (i < 20)
        t_type = "none"
        if is_tampered:
            t_type = ["balance_mismatch", "future_dates", "duplicate_transactions"][i % 3]
        specs.append(("bank_statement", is_tampered, t_type))

    # 2. Invoices: 120 total, 18 tampered
    for i in range(120):
        is_tampered = (i < 18)
        t_type = "none"
        if is_tampered:
            t_type = ["total_mismatch", "future_dates", "invalid_gstin"][i % 3]
        specs.append(("invoice", is_tampered, t_type))

    # 3. PAN: 40 total, 6 tampered
    for i in range(40):
        is_tampered = (i < 6)
        t_type = "invalid_pan_format" if is_tampered else "none"
        specs.append(("pan_card", is_tampered, t_type))

    # 4. Aadhaar: 40 total, 6 tampered
    for i in range(40):
        is_tampered = (i < 6)
        t_type = "invalid_aadhaar_format" if is_tampered else "none"
        specs.append(("aadhaar_card", is_tampered, t_type))

    # Shuffle deterministically
    random.seed(RANDOM_SEED)
    random.shuffle(specs)

    split_idx = int(len(specs) * train_ratio)
    train_specs = specs[:split_idx]
    test_specs = specs[split_idx:]

    print(f"Generating dataset: Total={len(specs)}, Train={len(train_specs)}, Test={len(test_specs)}")

    manifest = {"train": [], "test": [], "degraded_scans": []}

    for split_name, current_specs in [("train", train_specs), ("test", test_specs)]:
        for idx, (doc_type, is_tampered, t_type) in enumerate(current_specs):
            doc_id = f"{split_name}_{doc_type}_{idx+1:04d}"
            pdf_path = RAW_DIR / split_name / f"{doc_id}.pdf"
            gt_path = GT_DIR / split_name / f"{doc_id}.json"

            if doc_type == "bank_statement":
                data = generate_bank_statement_data(doc_id, is_tampered, t_type)
                render_bank_statement_pdf(data, pdf_path)
            elif doc_type == "invoice":
                data = generate_invoice_data(doc_id, is_tampered, t_type)
                render_invoice_pdf(data, pdf_path)
            elif doc_type in ("pan_card", "aadhaar_card"):
                data = generate_kyc_data(doc_id, doc_type, is_tampered, t_type)
                render_kyc_pdf(data, pdf_path)

            with open(gt_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            manifest[split_name].append({
                "doc_id": doc_id,
                "doc_type": doc_type,
                "is_tampered": is_tampered,
                "tamper_types": data["tamper_types"],
                "pdf_path": str(pdf_path.relative_to(BASE_DIR)),
                "gt_path": str(gt_path.relative_to(BASE_DIR))
            })

    # Render 40 test documents as degraded scans for the OCR experiment
    test_manifest = manifest["test"]
    scan_count = min(40, len(test_manifest))
    for i in range(scan_count):
        item = test_manifest[i]
        src_pdf = BASE_DIR / item["pdf_path"]
        png_filename = f"scan_{item['doc_id']}.png"
        png_path = SCANS_DIR / png_filename
        create_degraded_scan(src_pdf, png_path)

        # Copy reference ground truth
        scan_gt_path = SCANS_DIR / f"scan_{item['doc_id']}.json"
        src_gt = BASE_DIR / item["gt_path"]
        with open(src_gt, "r", encoding="utf-8") as f:
            gt_data = json.load(f)
        with open(scan_gt_path, "w", encoding="utf-8") as f:
            json.dump(gt_data, f, indent=2)

        manifest["degraded_scans"].append({
            "scan_id": f"scan_{item['doc_id']}",
            "original_doc_id": item["doc_id"],
            "doc_type": item["doc_type"],
            "image_path": str(png_path.relative_to(BASE_DIR)),
            "gt_path": str(scan_gt_path.relative_to(BASE_DIR))
        })

    # Save manifest
    with open(DATA_DIR / "dataset_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    total_tampered = sum(1 for s in specs if s[1])
    print(f"Dataset generation complete!")
    print(f"Total documents: {len(specs)} (Train: {len(train_specs)}, Test: {len(test_specs)})")
    print(f"Tampered documents: {total_tampered} ({total_tampered/len(specs)*100:.1f}%)")
    print(f"Degraded test scans: {scan_count} rendered into data/degraded_scans/")
    return manifest


if __name__ == "__main__":
    generate_all_datasets()
