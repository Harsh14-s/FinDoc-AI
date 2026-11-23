"""Classifier Service for FinDocAI.

Orchestrates both Baseline Keyword Rules and TF-IDF Logistic Regression ML classifiers.
Reports predictions and confidences from both methods for transparent evaluator comparison.
Group G382: Harsh Shukla, Akshita Singh.
"""

from typing import Dict, Any
from findoc.classify.rule_classifier import classify_by_rules
from findoc.classify.ml_classifier import ml_classifier


def classify_document(text: str) -> Dict[str, Any]:
    """Execute both Baseline Keyword Rules and ML Classifier, returning both results.

    Args:
        text: Extracted text from the input document.

    Returns:
        Dictionary containing rule_based, ml_based, and final consensus classification.
    """
    rule_result = classify_by_rules(text)
    ml_result = ml_classifier.predict(text)

    # Primary decision: If both agree, high confidence.
    # If ML has high confidence (> 0.65), adopt ML; otherwise fallback to rule_based.
    if rule_result["predicted_class"] == ml_result["predicted_class"]:
        final_class = rule_result["predicted_class"]
        confidence = max(rule_result["confidence"], ml_result["confidence"])
        agreement = True
    elif ml_result["confidence"] >= 0.70:
        final_class = ml_result["predicted_class"]
        confidence = ml_result["confidence"]
        agreement = False
    else:
        final_class = rule_result["predicted_class"]
        confidence = rule_result["confidence"]
        agreement = False

    return {
        "final_prediction": final_class,
        "confidence": confidence,
        "models_agree": agreement,
        "rule_based": rule_result,
        "ml_based": ml_result
    }
