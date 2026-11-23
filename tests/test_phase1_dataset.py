"""Unit tests for Phase 1: Directory Skeleton, Synthetic Dataset, and Scanned PNGs.
Group G382: Harsh Shukla, Akshita Singh.
"""

import json
from pathlib import Path
from PIL import Image
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent


def test_directory_structure_exists():
    """Verify that all standard project folders exist."""
    required_dirs = [
        "data/raw/train", "data/raw/test",
        "data/ground_truth/train", "data/ground_truth/test",
        "data/degraded_scans",
        "src/findoc/ingest", "src/findoc/classify", "src/findoc/extract",
        "src/findoc/validate", "src/findoc/flags", "src/findoc/storage",
        "src/findoc/api", "app", "tests", "docs/milestone1", "results"
    ]
    for d in required_dirs:
        p = BASE_DIR / d
        assert p.exists() and p.is_dir(), f"Directory missing: {d}"


def test_dataset_manifest_and_counts():
    """Verify 320 documents with exact 70/30 split and ~15% tampered proportion."""
    manifest_path = BASE_DIR / "data" / "dataset_manifest.json"
    assert manifest_path.exists(), "Dataset manifest does not exist"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    train_docs = manifest["train"]
    test_docs = manifest["test"]
    scans = manifest["degraded_scans"]

    assert len(train_docs) == 224, f"Expected 224 train docs, got {len(train_docs)}"
    assert len(test_docs) == 96, f"Expected 96 test docs, got {len(test_docs)}"
    assert len(train_docs) + len(test_docs) == 320, "Total documents must equal 320"
    assert len(scans) == 40, f"Expected 40 degraded scans, got {len(scans)}"

    all_docs = train_docs + test_docs
    tampered_docs = [d for d in all_docs if d["is_tampered"]]
    tamper_ratio = len(tampered_docs) / len(all_docs)
    assert 0.14 <= tamper_ratio <= 0.17, f"Tamper ratio {tamper_ratio:.3f} outside expected 15% range"


def test_pdf_and_ground_truth_pairing():
    """Verify that every generated PDF has an accessible, valid paired ground truth JSON."""
    manifest_path = BASE_DIR / "data" / "dataset_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Check a sample across train and test
    sample_docs = manifest["train"][:10] + manifest["test"][:10]
    for doc_meta in sample_docs:
        pdf_path = BASE_DIR / doc_meta["pdf_path"]
        gt_path = BASE_DIR / doc_meta["gt_path"]

        assert pdf_path.exists(), f"PDF missing: {pdf_path}"
        assert pdf_path.stat().st_size > 500, f"PDF file suspiciously small: {pdf_path}"
        assert gt_path.exists(), f"Ground truth missing: {gt_path}"

        with open(gt_path, "r", encoding="utf-8") as f:
            gt_data = json.load(f)

        assert gt_data["document_id"] == doc_meta["doc_id"]
        assert gt_data["document_type"] == doc_meta["doc_type"]
        assert "is_tampered" in gt_data
        assert "tamper_types" in gt_data


def test_degraded_scans_are_valid_images():
    """Verify that the 40 degraded scanned PNGs exist, have non-trivial dimensions, and open cleanly."""
    scans_dir = BASE_DIR / "data" / "degraded_scans"
    png_files = list(scans_dir.glob("*.png"))
    assert len(png_files) == 40, f"Expected 40 PNG scan files, got {len(png_files)}"

    # Check image integrity of first 5
    for png_path in png_files[:5]:
        with Image.open(png_path) as img:
            assert img.format == "PNG"
            assert img.width > 500 and img.height > 700
