"""Baseline Keyword-Rule Document Classifier for FinDocAI.

Implements an explainable, dictionary-based keyword matching heuristic to classify
documents into: bank_statement, invoice, pan_card, aadhaar_card.
Group G382: Harsh Shukla, Akshita Singh.
"""

from typing import Dict, Any, Tuple
import re


KEYWORDS = {
    "bank_statement": [
        "bank", "account number", "statement", "ifsc", "opening balance",
        "closing balance", "withdrawal", "deposit", "transaction", "debit",
        "credit", "account holder", "branch"
    ],
    "invoice": [
        "invoice", "tax invoice", "gstin", "subtotal", "grand total",
        "billed to", "bill to", "due date", "vendor", "cgst", "sgst", "unit price"
    ],
    "pan_card": [
        "income tax department", "permanent account number", "father's name",
        "govt of india", "pan"
    ],
    "aadhaar_card": [
        "unique identification authority of india", "aadhaar", "uidai",
        "resident", "mera aadhaar", "enrollment"
    ]
}


def classify_by_rules(text: str) -> Dict[str, Any]:
    """Classify document type using keyword density rules.

    Args:
        text: Extracted document text.

    Returns:
        Dictionary with predicted class, confidence, and keyword hit details.
    """
    clean_text = text.lower()
    scores = {}
    matched_keywords = {}

    for doc_type, kw_list in KEYWORDS.items():
        hits = []
        for kw in kw_list:
            # Word boundary search for precision
            pattern = r"\b" + re.escape(kw) + r"\b"
            matches = re.findall(pattern, clean_text)
            if matches:
                hits.append(kw)
        scores[doc_type] = len(hits)
        matched_keywords[doc_type] = hits

    total_hits = sum(scores.values())
    if total_hits == 0:
        return {
            "predicted_class": "unknown",
            "confidence": 0.0,
            "method": "rule_based",
            "scores": scores,
            "matched_keywords": matched_keywords
        }

    # Best category
    best_class = max(scores, key=scores.get)
    best_score = scores[best_class]
    confidence = round(best_score / total_hits, 3)

    return {
        "predicted_class": best_class,
        "confidence": confidence,
        "method": "rule_based",
        "scores": scores,
        "matched_keywords": matched_keywords[best_class]
    }
