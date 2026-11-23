"""Review Priority and Flags Engine for FinDocAI.

Computes a transparent weighted review priority based on triggered explainable flags
and validation failures. Always surfaces contributing flags and rationales.
DISCLAIMER: Indicators only. Human review required. System never makes autonomous fraud or credit decisions.
Group G382: Harsh Shukla, Akshita Singh.
"""

from typing import Dict, Any, List
from findoc.flags.rules import (
    flag_median_outliers,
    flag_repeated_identical_transactions,
    flag_negative_balances,
    flag_large_cash_withdrawals,
    flag_bounced_entries,
    flag_invoice_anomalies
)

DISCLAIMER_TEXT = "Indicators only. Human review required. System does not make autonomous fraud or credit decisions."


def evaluate_review_priority(extracted_data: Dict[str, Any], validation_result: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate review priority (Low / Medium / High) and compile contributing flags.

    Args:
        extracted_data: Structured document payload from extractor_service
        validation_result: Output from validator.validate_document

    Returns:
        Structured review priority dictionary detailing priority tier, total score,
        and all contributing explainable flags with reasons.
    """
    doc_type = extracted_data.get("document_type", "unknown")
    flags: List[Dict[str, Any]] = []

    # 1. Flag validation failures directly
    val_failures = [r for r in validation_result.get("rules", []) if r["status"] == "FAIL"]
    for vf in val_failures:
        flags.append({
            "flag_id": f"FLAG_VAL_FAIL_{vf['rule_id']}",
            "name": f"Validation Failure: {vf['rule_name']}",
            "weight": 35,
            "reason": f"Core validation failed: {vf['reason']}",
            "details": vf.get("details", {})
        })

    # 2. Bank statement transaction-level flags
    if doc_type == "bank_statement":
        txns = extracted_data.get("transactions", [])
        flags.extend(flag_median_outliers(txns))
        flags.extend(flag_repeated_identical_transactions(txns))
        flags.extend(flag_negative_balances(txns))
        flags.extend(flag_large_cash_withdrawals(txns))
        flags.extend(flag_bounced_entries(txns))

    # 3. Invoice specific flags
    elif doc_type == "invoice":
        flags.extend(flag_invoice_anomalies(extracted_data))

    # Calculate transparent weighted sum (capped at 100)
    raw_score = sum(f["weight"] for f in flags)
    total_priority_score = min(raw_score, 100)

    # Determine Review Priority tier
    if total_priority_score >= 50:
        priority_tier = "High"
        summary_rationale = f"High review priority triggered by {len(flags)} indicator(s) including critical inconsistencies."
    elif total_priority_score >= 20:
        priority_tier = "Medium"
        summary_rationale = f"Medium review priority triggered by {len(flags)} indicator(s) requiring standard supervisory review."
    else:
        priority_tier = "Low"
        summary_rationale = "Low review priority. Document conforms to normal verification expectations."

    return {
        "review_priority": priority_tier,
        "priority_score": total_priority_score,
        "disclaimer": DISCLAIMER_TEXT,
        "summary": summary_rationale,
        "flags_count": len(flags),
        "flags": flags,
        "contributing_flags_summary": [
            f"[{f['flag_id']}] (Weight +{f['weight']}): {f['reason']}" for f in flags
        ]
    }
