"""Unusual Transaction and Document Review Flag Rules for FinDocAI.

Implements explainable heuristic rules to highlight potential inconsistencies or
unusual transaction patterns for human reviewer attention.
DISCLAIMER: Indicators only. Human review required. Never makes credit or fraud decisions.
Group G382: Harsh Shukla, Akshita Singh.
"""

import re
from typing import Dict, Any, List
import numpy as np


def flag_median_outliers(transactions: List[Dict[str, Any]], multiplier: float = 3.5, min_amount: float = 20000.0) -> List[Dict[str, Any]]:
    """FLAG_MEDIAN_OUTLIER: Identify transactions whose debit or credit significantly exceeds the median."""
    amounts = [max(t.get("debit", 0.0) or 0.0, t.get("credit", 0.0) or 0.0) for t in transactions]
    amounts = [a for a in amounts if a > 0]

    if len(amounts) < 4:
        return []

    median_val = float(np.median(amounts))
    threshold = max(median_val * multiplier, min_amount)
    flags = []

    for idx, tx in enumerate(transactions):
        tx_amt = max(tx.get("debit", 0.0) or 0.0, tx.get("credit", 0.0) or 0.0)
        if tx_amt >= threshold:
            flags.append({
                "flag_id": "FLAG_MEDIAN_OUTLIER",
                "name": "High-Value Transaction Outlier",
                "weight": 15,
                "reason": (
                    f"Transaction #{idx+1} ({tx.get('ref_no', 'N/A')}) amount of INR {tx_amt:,.2f} "
                    f"is {tx_amt / max(median_val, 1.0):.1f}x higher than the account median transaction "
                    f"size of INR {median_val:,.2f}."
                ),
                "details": {
                    "transaction_ref": tx.get("ref_no"),
                    "amount": tx_amt,
                    "account_median": round(median_val, 2),
                    "threshold": round(threshold, 2)
                }
            })

    return flags


def flag_repeated_identical_transactions(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """FLAG_REPEATED_IDENTICAL: Detect frequent identical transaction amounts within the period."""
    if len(transactions) < 4:
        return []

    amt_counts: Dict[float, List[str]] = {}
    for tx in transactions:
        tx_amt = max(tx.get("debit", 0.0) or 0.0, tx.get("credit", 0.0) or 0.0)
        if tx_amt >= 2000.0:  # Only evaluate non-trivial amounts
            amt_counts.setdefault(tx_amt, []).append(tx.get("ref_no", "N/A"))

    flags = []
    for amt, refs in amt_counts.items():
        if len(refs) >= 3:
            flags.append({
                "flag_id": "FLAG_REPEATED_IDENTICAL",
                "name": "Repeated Identical Amounts",
                "weight": 15,
                "reason": (
                    f"Identical transaction amount of INR {amt:,.2f} appeared {len(refs)} times "
                    f"within the same statement period (Refs: {', '.join(refs[:3])})."
                ),
                "details": {"amount": amt, "occurrences": len(refs), "refs": refs}
            })

    return flags


def flag_negative_balances(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """FLAG_NEGATIVE_BALANCE: Highlight occurrences where running balance dipped below zero."""
    flags = []
    for idx, tx in enumerate(transactions):
        bal = tx.get("balance")
        if bal is not None and bal < 0.0:
            flags.append({
                "flag_id": "FLAG_NEGATIVE_BALANCE",
                "name": "Negative Running Balance",
                "weight": 25,
                "reason": (
                    f"Running balance dipped into negative territory (INR {bal:,.2f}) at "
                    f"transaction #{idx+1} on {tx.get('date', 'unknown')} (Ref: {tx.get('ref_no', 'N/A')})."
                ),
                "details": {"balance": bal, "date": tx.get("date"), "ref_no": tx.get("ref_no")}
            })

    return flags


def flag_large_cash_withdrawals(transactions: List[Dict[str, Any]], cash_threshold: float = 20000.0) -> List[Dict[str, Any]]:
    """FLAG_LARGE_CASH_WITHDRAWAL: Flag cash/ATM withdrawals exceeding monitoring thresholds."""
    flags = []
    cash_keywords = ["ATM", "CASH", "SELF", "WITHDRAWAL"]

    for idx, tx in enumerate(transactions):
        desc = str(tx.get("description", "")).upper()
        debit = tx.get("debit", 0.0) or 0.0
        if any(kw in desc for kw in cash_keywords) and debit >= cash_threshold:
            flags.append({
                "flag_id": "FLAG_LARGE_CASH_WITHDRAWAL",
                "name": "High-Value Cash Withdrawal",
                "weight": 15,
                "reason": (
                    f"High-value cash withdrawal of INR {debit:,.2f} at transaction #{idx+1} "
                    f"exceeds the INR {cash_threshold:,.2f} monitoring threshold (Description: '{tx.get('description')}')."
                ),
                "details": {"amount": debit, "description": tx.get("description"), "ref_no": tx.get("ref_no")}
            })

    return flags


def flag_bounced_entries(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """FLAG_FAILED_BOUNCED_ENTRY: Flag bounced, returned, or dishonored payment records."""
    flags = []
    bounce_keywords = ["BOUNCE", "RETURN", "FAILED", "DISHONOUR", "INSUFFICIENT", "REVERSAL", "UNPAID"]

    for idx, tx in enumerate(transactions):
        desc = str(tx.get("description", "")).upper()
        if any(kw in desc for kw in bounce_keywords):
            flags.append({
                "flag_id": "FLAG_FAILED_BOUNCED_ENTRY",
                "name": "Bounced or Returned Transaction",
                "weight": 20,
                "reason": (
                    f"Transaction #{idx+1} description '{tx.get('description')}' indicates a failed, "
                    f"bounced, or returned transaction."
                ),
                "details": {"description": tx.get("description"), "ref_no": tx.get("ref_no"), "date": tx.get("date")}
            })

    return flags


def flag_invoice_anomalies(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """FLAG_INV_TAX_ANOMALY: Flag invoice tax calculation inconsistencies."""
    flags = []
    subtotal = data.get("subtotal")
    tax = data.get("tax_amount")

    if subtotal and tax and subtotal > 0:
        actual_tax_rate = round(tax / subtotal, 4)
        # Expected standard Indian GST rates: 5%, 12%, 18%, or 28%
        standard_rates = [0.05, 0.12, 0.18, 0.28]
        closest_diff = min(abs(actual_tax_rate - r) for r in standard_rates)

        if closest_diff > 0.025:
            flags.append({
                "flag_id": "FLAG_INV_TAX_ANOMALY",
                "name": "Non-Standard Tax Rate Calculation",
                "weight": 15,
                "reason": (
                    f"Invoice tax rate ({actual_tax_rate*100:.1f}%) deviates from standard GST tiers "
                    f"(5%, 12%, 18%, 28%). Subtotal: INR {subtotal:,.2f}, Tax: INR {tax:,.2f}."
                ),
                "details": {"actual_tax_rate": actual_tax_rate, "subtotal": subtotal, "tax": tax}
            })

    return flags
