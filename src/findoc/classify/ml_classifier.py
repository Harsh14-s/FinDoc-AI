"""Machine Learning Document Classifier for FinDocAI.

Implements a TF-IDF Vectorizer + Logistic Regression classifier.
Trained on the 70% synthetic training split to classify:
bank_statement, invoice, pan_card, aadhaar_card.
Group G382: Harsh Shukla, Akshita Singh.
"""

import os
import json
import pickle
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from findoc.ingest.pdf_parser import extract_text_and_tables

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
MODEL_PATH = BASE_DIR / "results" / "classifier_model.pkl"


class MLDocumentClassifier:
    """TF-IDF and Logistic Regression classifier for financial documents."""

    def __init__(self, model_file: Optional[Path] = None):
        self.model_file = model_file or MODEL_PATH
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.model: Optional[LogisticRegression] = None
        self.classes_: List[str] = []

    def train(self, texts: List[str], labels: List[str]) -> Dict[str, Any]:
        """Fit TF-IDF vectorizer and Logistic Regression model on training corpus."""
        if not texts or not labels:
            raise ValueError("Training texts and labels cannot be empty")

        # Use unigram and bigram features with sublinear term frequency
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=1000,
            sublinear_tf=True,
            stop_words="english"
        )
        X = self.vectorizer.fit_transform(texts)

        self.model = LogisticRegression(
            C=1.0,
            max_iter=300,
            random_state=42
        )
        self.model.fit(X, labels)
        self.classes_ = list(self.model.classes_)

        # Persist model artifacts
        os.makedirs(self.model_file.parent, exist_ok=True)
        with open(self.model_file, "wb") as f:
            pickle.dump({
                "vectorizer": self.vectorizer,
                "model": self.model,
                "classes": self.classes_
            }, f)

        return {
            "status": "trained",
            "samples_count": len(texts),
            "classes": self.classes_,
            "feature_count": len(self.vectorizer.get_feature_names_out())
        }

    def load(self) -> bool:
        """Load trained model weights from disk if available."""
        if not self.model_file.exists():
            return False
        try:
            with open(self.model_file, "rb") as f:
                data = pickle.load(f)
                self.vectorizer = data["vectorizer"]
                self.model = data["model"]
                self.classes_ = data["classes"]
            return True
        except Exception:
            return False

    def predict(self, text: str) -> Dict[str, Any]:
        """Predict document class with class probabilities."""
        if self.model is None or self.vectorizer is None:
            loaded = self.load()
            if not loaded:
                # If model is not trained yet, train on the train set
                self._auto_train_from_dataset()

        if self.model is None or self.vectorizer is None:
            return {
                "predicted_class": "unknown",
                "confidence": 0.0,
                "method": "ml_tfidf_logreg",
                "probabilities": {}
            }

        X = self.vectorizer.transform([text])
        probs = self.model.predict_proba(X)[0]
        best_idx = int(np.argmax(probs))
        predicted_class = self.classes_[best_idx]
        confidence = float(round(probs[best_idx], 3))

        prob_dict = {
            cls: float(round(p, 4)) for cls, p in zip(self.classes_, probs)
        }

        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "method": "ml_tfidf_logreg",
            "probabilities": prob_dict
        }

    def _auto_train_from_dataset(self):
        """Helper to automatically train from data/raw/train and data/ground_truth/train."""
        train_raw = BASE_DIR / "data" / "raw" / "train"
        train_gt = BASE_DIR / "data" / "ground_truth" / "train"
        if not train_raw.exists() or not train_gt.exists():
            return

        texts = []
        labels = []
        for gt_file in train_gt.glob("*.json"):
            doc_id = gt_file.stem
            pdf_file = train_raw / f"{doc_id}.pdf"
            if pdf_file.exists():
                with open(gt_file, "r", encoding="utf-8") as f:
                    gt_data = json.load(f)
                res = extract_text_and_tables(pdf_file)
                if res["text"]:
                    texts.append(res["text"])
                    labels.append(gt_data["document_type"])

        if texts and labels:
            self.train(texts, labels)


# Global singleton classifier instance
ml_classifier = MLDocumentClassifier()
