"""Validator Engine Coordinator for FinDocAI.

Executes all applicable validation rules against extracted document data,
summarizing pass/fail counts and providing clear reasons for every failure.
Group G382: Harsh Shukla, Akshita Singh.
"""

from typing import Dict, Any, List
from findoc.validate.rules import (
    check_required_fields,
    check_numeric_types,
    check_bank_balance_reconciliation,
    check_invoice_totals_reconciliation,
    check_identifier_formats,
    check_date_sanity,
    check_duplicate_transactions
)


def validate_document(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute complete rule-based validation suite on extracted document data.

    Args:
        extracted_data: Normalized dictionary produced by extract.extractor_service

    Returns:
        Structured validation summary containing rule evaluations, overall status, and failure counts.
    """
    doc_type = extracted_data.get("document_type", "unknown")
    rule_results: List[Dict[str, Any]] = []

    # 1. Required fields
    rule_results.append(check_required_fields(extracted_data, doc_type))

    # 2. Numeric types
    rule_results.append(check_numeric_types(extracted_data, doc_type))

    # 3. Document-specific arithmetic reconciliations
    if doc_type == "bank_statement":
        rule_results.extend(check_bank_balance_reconciliation(extracted_data))
        dup_res = check_duplicate_transactions(extracted_data)
        if dup_res:
            rule_results.append(dup_res)

    elif doc_type == "invoice":
        rule_results.extend(check_invoice_totals_reconciliation(extracted_data))

    # 4. Regulatory format checks (PAN, Aadhaar, IFSC, GSTIN)
    rule_results.extend(check_identifier_formats(extracted_data, doc_type))

    # 5. Date sanity
    rule_results.extend(check_date_sanity(extracted_data, doc_type))

    # Compute overall statistics
    total_checks = len(rule_results)
    failures = [r for r in rule_results if r["status"] == "FAIL"]
    passes = [r for r in rule_results if r["status"] == "PASS"]
    overall_status = "PASS" if len(failures) == 0 else "FAIL"

    return {
        "overall_status": overall_status,
        "total_rules_checked": total_checks,
        "passed_count": len(passes),
        "failed_count": len(failures),
        "rules": rule_results,
        "failure_summary": [f"{r['rule_id']}: {r['reason']}" for r in failures]
    }
