"""FinDocAI: Single-Command Pipeline Orchestrator.

One command to:
1. Verify environment and database initialization.
2. Generate synthetic dataset (320 documents + 40 degraded scans) if not present.
3. Train TF-IDF + Logistic Regression ML classifier.
4. Execute comprehensive benchmark evaluation and generate charts.
5. Run automated pytest test suite (29 tests).
6. Launch interactive Streamlit application.

Usage:
    python run_pipeline.py
"""

import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MANIFEST_PATH = BASE_DIR / "data" / "dataset_manifest.json"
MODEL_PATH = BASE_DIR / "results" / "classifier_model.pkl"
RESULTS_SUMMARY = BASE_DIR / "results" / "evaluation_summary.csv"


def print_step(num: int, title: str):
    print("\n" + "=" * 65)
    print(f"STEP {num}: {title}")
    print("=" * 65)


def main():
    print("=" * 65)
    print("   FinDocAI: Financial Document Processing MVP Pipeline")
    print("   Group G382: Harsh Shukla & Akshita Singh")
    print("   Course: CSET400C Capstone Project, Milestone-2")
    print("=" * 65)

    # 1. Initialize SQLite Database
    print_step(1, "Initializing Relational Database")
    from findoc.storage.db import init_db
    init_db()
    print("  [OK] SQLite database initialized at: data/findoc.db")

    # 2. Check / Generate Synthetic Dataset
    print_step(2, "Checking Synthetic Dataset")
    if not MANIFEST_PATH.exists():
        print("  Generating 320 synthetic documents and 40 degraded scans...")
        from findoc.generator import generate_all_datasets
        generate_all_datasets()
    else:
        print("  [OK] Synthetic dataset already generated (data/dataset_manifest.json found).")

    # 3. Train ML Classifier
    print_step(3, "Training ML Document Classifier")
    from findoc.classify.ml_classifier import ml_classifier
    if not MODEL_PATH.exists():
        print("  Training TF-IDF + Logistic Regression model on training corpus...")
        ml_classifier._auto_train_from_dataset()
    else:
        ml_classifier.load()
        print(f"  [OK] Trained model loaded from: {MODEL_PATH}")

    # 4. Run Benchmark Evaluation
    print_step(4, "Executing Benchmark Evaluation")
    if not RESULTS_SUMMARY.exists():
        print("  Running full evaluation across test set...")
        from findoc.evaluate import run_full_evaluation
        run_full_evaluation()
    else:
        print(f"  [OK] Real evaluation results present in results/ directory.")

    # 5. Run Automated Test Suite
    print_step(5, "Running Pytest Automated Test Suite (29 Tests)")
    test_res = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"])
    if test_res.returncode != 0:
        print("  [ERROR] Pytest reported failures. Aborting launch.")
        sys.exit(1)
    print("  [OK] All 29 unit and edge-case tests passed with 100% success!")

    # 6. Launch Streamlit Application
    print_step(6, "Launching Streamlit Interactive Dashboard")
    print("  Starting Streamlit application at: http://localhost:8501")
    print("  Press Ctrl+C to stop the server.\n")

    subprocess.run([sys.executable, "-m", "streamlit", "run", "app/main.py"])


if __name__ == "__main__":
    main()
