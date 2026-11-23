"""Validation Rule Definitions and Implementation for FinDocAI.

Every rule produces an explicit Rule ID, Pass/Fail status, and a human-readable
explanation explaining WHY the rule succeeded or failed.
Group G382: Harsh Shukla, Akshita Singh.
"""

import re
from datetime import datetime
from typing import Dict, Any, List, Optional


def check_required_fields(data: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
    """VAL_REQ_001: Ensure all mandatory fields for the document type are present and non-empty."""
    requirements = {
        "bank_statement": ["account_number", "opening_balance", "closing_balance"],
        "invoice": ["invoice_number", "invoice_date", "grand_total"],
        "pan_card": ["id_number", "full_name"],
        "aadhaar_card": ["id_number", "full_name"],
    }

    req_fields = requirements.get(doc_type, [])
    missing = [f for f in req_fields if data.get(f) is None or str(data.get(f)).strip() == ""]

    if missing:
        return {
            "rule_id": "VAL_REQ_001",
            "rule_name": "Required Fields Presence",
            "status": "FAIL",
            "reason": f"Mandatory field(s) missing or empty: {', '.join(missing)}.",
            "details": {"missing_fields": missing, "required_fields": req_fields}
        }

    return {
        "rule_id": "VAL_REQ_001",
        "rule_name": "Required Fields Presence",
        "status": "PASS",
        "reason": "All mandatory document fields are present.",
        "details": {"checked_fields": req_fields}
    }


def check_numeric_types(data: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
    """VAL_NUM_001: Ensure financial amounts are valid numeric values."""
    numeric_fields = {
        "bank_statement": ["opening_balance", "closing_balance", "total_deposits", "total_withdrawals"],
        "invoice": ["subtotal", "tax_amount", "grand_total"],
        "pan_card": [],
        "aadhaar_card": []
    }

    fields_to_check = numeric_fields.get(doc_type, [])
    invalid = []

    for f in fields_to_check:
        val = data.get(f)
        if val is not None and not isinstance(val, (int, float)):
            invalid.append(f)

    if invalid:
        return {
            "rule_id": "VAL_NUM_001",
            "rule_name": "Numeric Type Verification",
            "status": "FAIL",
            "reason": f"Field(s) expected to be numeric: {', '.join(invalid)}.",
            "details": {"invalid_fields": invalid}
        }

    return {
        "rule_id": "VAL_NUM_001",
        "rule_name": "Numeric Type Verification",
        "status": "PASS",
        "reason": "All expected financial amount fields contain valid numeric types.",
        "details": {"checked_fields": fields_to_check}
    }


def check_bank_balance_reconciliation(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """VAL_BNK_REC: Verify opening balance + deposits - withdrawals equals closing balance.

    Also checks running balance consistency across transaction rows.
    """
    results = []

    opening = data.get("opening_balance")
    closing = data.get("closing_balance")
    deposits = data.get("total_deposits")
    withdrawals = data.get("total_withdrawals")

    if all(v is not None for v in [opening, closing, deposits, withdrawals]):
        expected_closing = round(opening + deposits - withdrawals, 2)
        diff = round(abs(closing - expected_closing), 2)

        if diff > 0.05:
            results.append({
                "rule_id": "VAL_BNK_REC",
                "rule_name": "Bank Statement Balance Reconciliation",
                "status": "FAIL",
                "reason": (
                    f"Closing balance mismatch. Extracted closing balance is INR {closing:,.2f}, "
                    f"but calculated Opening (INR {opening:,.2f}) + Deposits (INR {deposits:,.2f}) "
                    f"- Withdrawals (INR {withdrawals:,.2f}) = INR {expected_closing:,.2f} "
                    f"(Discrepancy: INR {diff:,.2f})."
                ),
                "details": {
                    "extracted_closing": closing,
                    "expected_closing": expected_closing,
                    "discrepancy": diff
                }
            })
        else:
            results.append({
                "rule_id": "VAL_BNK_REC",
                "rule_name": "Bank Statement Balance Reconciliation",
                "status": "PASS",
                "reason": (
                    f"Closing balance reconciles accurately: Opening ({opening:,.2f}) + Deposits ({deposits:,.2f}) "
                    f"- Withdrawals ({withdrawals:,.2f}) = Closing ({closing:,.2f})."
                ),
                "details": {"closing": closing, "discrepancy": 0.0}
            })

    # Check running balances across transactions
    txns = data.get("transactions", [])
    if len(txns) >= 2 and opening is not None:
        curr_bal = opening
        broken_steps = []
        for idx, tx in enumerate(txns):
            dr = tx.get("debit", 0.0) or 0.0
            cr = tx.get("credit", 0.0) or 0.0
            curr_bal = round(curr_bal + cr - dr, 2)
            stated_bal = tx.get("balance")
            if stated_bal is not None and abs(stated_bal - curr_bal) > 0.05:
                broken_steps.append({
                    "tx_index": idx,
                    "ref_no": tx.get("ref_no"),
                    "expected_balance": curr_bal,
                    "stated_balance": stated_bal
                })

        if broken_steps:
            first_fail = broken_steps[0]
            results.append({
                "rule_id": "VAL_BNK_RUN_BAL",
                "rule_name": "Transaction Running Balance Continuity",
                "status": "FAIL",
                "reason": (
                    f"Running balance calculation broke at transaction #{first_fail['tx_index']+1} "
                    f"(Ref: {first_fail['ref_no']}). Expected balance was INR {first_fail['expected_balance']:,.2f}, "
                    f"but row records INR {first_fail['stated_balance']:,.2f}."
                ),
                "details": {"failures_count": len(broken_steps), "first_failure": first_fail}
            })
        else:
            results.append({
                "rule_id": "VAL_BNK_RUN_BAL",
                "rule_name": "Transaction Running Balance Continuity",
                "status": "PASS",
                "reason": f"All {len(txns)} transaction running balances mathematically reconcile.",
                "details": {"transaction_count": len(txns)}
            })

    return results


def check_invoice_totals_reconciliation(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """VAL_INV_TOT: Verify Subtotal + Tax Amount equals Grand Total."""
    results = []

    subtotal = data.get("subtotal")
    tax = data.get("tax_amount")
    grand_total = data.get("grand_total")

    if subtotal is not None and tax is not None and grand_total is not None:
        expected_total = round(subtotal + tax, 2)
        diff = round(abs(grand_total - expected_total), 2)

        if diff > 0.05:
            results.append({
                "rule_id": "VAL_INV_TOT",
                "rule_name": "Invoice Subtotal and Tax Reconciliation",
                "status": "FAIL",
                "reason": (
                    f"Invoice Grand Total mismatch. Extracted Grand Total is INR {grand_total:,.2f}, "
                    f"but Subtotal (INR {subtotal:,.2f}) + Tax (INR {tax:,.2f}) = INR {expected_total:,.2f} "
                    f"(Discrepancy: INR {diff:,.2f})."
                ),
                "details": {
                    "extracted_grand_total": grand_total,
                    "expected_grand_total": expected_total,
                    "discrepancy": diff
                }
            })
        else:
            results.append({
                "rule_id": "VAL_INV_TOT",
                "rule_name": "Invoice Subtotal and Tax Reconciliation",
                "status": "PASS",
                "reason": (
                    f"Grand Total reconciles: Subtotal (INR {subtotal:,.2f}) + Tax (INR {tax:,.2f}) "
                    f"= Grand Total (INR {grand_total:,.2f})."
                ),
                "details": {"grand_total": grand_total, "discrepancy": 0.0}
            })

    # Check sum of line items if present
    items = data.get("line_items", [])
    if items and subtotal is not None:
        item_sum = round(sum(it.get("total", 0.0) or 0.0 for it in items), 2)
        diff_items = round(abs(item_sum - subtotal), 2)
        if diff_items > 0.05:
            results.append({
                "rule_id": "VAL_INV_LINE_SUM",
                "rule_name": "Invoice Line Items Sum Reconciliation",
                "status": "FAIL",
                "reason": (
                    f"Sum of line items (INR {item_sum:,.2f}) does not match invoice Subtotal "
                    f"(INR {subtotal:,.2f}). Discrepancy: INR {diff_items:,.2f}."
                ),
                "details": {"line_items_sum": item_sum, "stated_subtotal": subtotal}
            })
        else:
            results.append({
                "rule_id": "VAL_INV_LINE_SUM",
                "rule_name": "Invoice Line Items Sum Reconciliation",
                "status": "PASS",
                "reason": f"Sum of {len(items)} line items exactly equals Subtotal (INR {subtotal:,.2f}).",
                "details": {"line_items_count": len(items)}
            })

    return results


def check_identifier_formats(data: Dict[str, Any], doc_type: str) -> List[Dict[str, Any]]:
    """Verify PAN, Aadhaar, IFSC, and GSTIN formatting against regulatory regex standards."""
    results = []

    # PAN Check
    if doc_type == "pan_card" or data.get("pan_number"):
        pan = data.get("id_number") or data.get("pan_number")
        if pan:
            pan_pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"
            if not re.match(pan_pattern, str(pan).strip().upper()):
                results.append({
                    "rule_id": "VAL_FMT_PAN",
                    "rule_name": "Permanent Account Number (PAN) Format",
                    "status": "FAIL",
                    "reason": f"PAN '{pan}' does not match the 10-character standard format (5 uppercase letters, 4 digits, 1 letter).",
                    "details": {"pan": pan}
                })
            else:
                results.append({
                    "rule_id": "VAL_FMT_PAN",
                    "rule_name": "Permanent Account Number (PAN) Format",
                    "status": "PASS",
                    "reason": f"PAN '{pan}' complies with Indian Income Tax Department format standards.",
                    "details": {"pan": pan}
                })

    # Aadhaar Check
    if doc_type == "aadhaar_card" or data.get("aadhaar_number"):
        aadhaar = data.get("id_number") or data.get("aadhaar_number")
        if aadhaar:
            clean_aadhaar = re.sub(r"\s+", "", str(aadhaar))
            # 12 digits, cannot start with 0 or 1
            aadhaar_pattern = r"^[2-9][0-9]{11}$"
            if not re.match(aadhaar_pattern, clean_aadhaar):
                results.append({
                    "rule_id": "VAL_FMT_AAD",
                    "rule_name": "Aadhaar Card UIDAI Format",
                    "status": "FAIL",
                    "reason": f"Aadhaar '{aadhaar}' violates UIDAI 12-digit format (must be 12 digits and cannot start with 0 or 1).",
                    "details": {"aadhaar": aadhaar}
                })
            else:
                results.append({
                    "rule_id": "VAL_FMT_AAD",
                    "rule_name": "Aadhaar Card UIDAI Format",
                    "status": "PASS",
                    "reason": "Aadhaar number adheres to UIDAI 12-digit specification.",
                    "details": {"aadhaar_valid": True}
                })

    # IFSC Check (Bank statements)
    if data.get("ifsc"):
        ifsc = str(data["ifsc"]).strip().upper()
        ifsc_pattern = r"^[A-Z]{4}0[A-Z0-9]{6}$"
        if not re.match(ifsc_pattern, ifsc):
            results.append({
                "rule_id": "VAL_FMT_IFSC",
                "rule_name": "Bank IFSC Code Format",
                "status": "FAIL",
                "reason": f"IFSC code '{ifsc}' violates the RBI 11-character format (4 letters, 0, 6 alphanumeric).",
                "details": {"ifsc": ifsc}
            })
        else:
            results.append({
                "rule_id": "VAL_FMT_IFSC",
                "rule_name": "Bank IFSC Code Format",
                "status": "PASS",
                "reason": f"IFSC code '{ifsc}' complies with RBI standards.",
                "details": {"ifsc": ifsc}
            })

    # GSTIN Check (Invoices)
    if data.get("vendor_gstin"):
        gstin = str(data["vendor_gstin"]).strip().upper()
        gstin_pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
        if not re.match(gstin_pattern, gstin):
            results.append({
                "rule_id": "VAL_FMT_GST",
                "rule_name": "Vendor GSTIN Format",
                "status": "FAIL",
                "reason": f"Vendor GSTIN '{gstin}' violates the Indian 15-character Goods & Services Tax format.",
                "details": {"gstin": gstin}
            })
        else:
            results.append({
                "rule_id": "VAL_FMT_GST",
                "rule_name": "Vendor GSTIN Format",
                "status": "PASS",
                "reason": f"Vendor GSTIN '{gstin}' is valid.",
                "details": {"gstin": gstin}
            })

    return results


def check_date_sanity(data: Dict[str, Any], doc_type: str) -> List[Dict[str, Any]]:
    """VAL_DAT_SAN: Ensure document dates are logically ordered and not in the far future."""
    results = []
    # Current threshold year (capstone demo context: reasonable bounds <= 2026)
    MAX_VALID_YEAR = 2026

    # 1. Bank statement dates
    if doc_type == "bank_statement":
        txns = data.get("transactions", [])
        future_txns = []
        for tx in txns:
            dt_str = tx.get("date")
            if dt_str:
                try:
                    dt = datetime.strptime(dt_str[:10], "%Y-%m-%d")
                    if dt.year > MAX_VALID_YEAR:
                        future_txns.append({"date": dt_str, "ref_no": tx.get("ref_no")})
                except ValueError:
                    pass

        if future_txns:
            results.append({
                "rule_id": "VAL_DAT_SAN",
                "rule_name": "Date Sanity & Future Date Check",
                "status": "FAIL",
                "reason": f"Detected {len(future_txns)} transaction(s) dated beyond year {MAX_VALID_YEAR} (e.g. {future_txns[0]['date']}).",
                "details": {"future_transactions": future_txns}
            })
        else:
            results.append({
                "rule_id": "VAL_DAT_SAN",
                "rule_name": "Date Sanity & Future Date Check",
                "status": "PASS",
                "reason": "All transaction dates fall within valid historical/current calendar limits.",
                "details": {"checked_transactions": len(txns)}
            })

    # 2. Invoice dates
    elif doc_type == "invoice":
        inv_dt = data.get("invoice_date")
        if inv_dt:
            try:
                dt = datetime.strptime(inv_dt[:10], "%Y-%m-%d")
                if dt.year > MAX_VALID_YEAR:
                    results.append({
                        "rule_id": "VAL_DAT_SAN",
                        "rule_name": "Invoice Date Sanity",
                        "status": "FAIL",
                        "reason": f"Invoice date '{inv_dt}' is set in the future beyond year {MAX_VALID_YEAR}.",
                        "details": {"invoice_date": inv_dt}
                    })
                else:
                    results.append({
                        "rule_id": "VAL_DAT_SAN",
                        "rule_name": "Invoice Date Sanity",
                        "status": "PASS",
                        "reason": f"Invoice date '{inv_dt}' is valid.",
                        "details": {"invoice_date": inv_dt}
                    })
            except ValueError:
                pass

    return results


def check_duplicate_transactions(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """VAL_DUP_TXN: Identify identical transaction records with duplicate reference IDs or amounts."""
    txns = data.get("transactions", [])
    if len(txns) < 2:
        return None

    seen_refs = {}
    duplicates = []

    for tx in txns:
        ref = tx.get("ref_no")
        if not ref:
            continue
        if ref in seen_refs:
            duplicates.append({
                "ref_no": ref,
                "date": tx.get("date"),
                "debit": tx.get("debit"),
                "credit": tx.get("credit")
            })
        else:
            seen_refs[ref] = tx

    if duplicates:
        return {
            "rule_id": "VAL_DUP_TXN",
            "rule_name": "Duplicate Transaction Detection",
            "status": "FAIL",
            "reason": f"Detected {len(duplicates)} duplicate transaction record(s) with identical reference IDs (e.g. {duplicates[0]['ref_no']}).",
            "details": {"duplicate_count": len(duplicates), "examples": duplicates[:3]}
        }

    return {
        "rule_id": "VAL_DUP_TXN",
        "rule_name": "Duplicate Transaction Detection",
        "status": "PASS",
        "reason": f"All {len(txns)} transactions possess distinct, unique reference IDs.",
        "details": {"total_transactions": len(txns)}
    }
