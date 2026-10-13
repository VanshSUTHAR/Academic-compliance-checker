"""Tests for PDF and DOCX extractors."""

from pathlib import Path
import pytest
from src.extractor.docx_extractor import extract_docx_document
from src.extractor.pdf_extractor import extract_pdf_document

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"

def test_extract_good_pdf():
    pdf_path = SAMPLES_DIR / "sample_assignment_good.pdf"
    assert pdf_path.exists(), "Sample good PDF must exist"

    doc = extract_pdf_document(pdf_path, filename="sample_assignment_good.pdf")
    assert doc.file_type == "pdf"
    assert doc.total_word_count > 250
    assert "Times" in doc.dominant_font
    assert doc.dominant_font_size_pt >= 11.0
    assert doc.avg_margins["top"] >= 0.7
    assert doc.avg_margins["left"] >= 0.7
    assert any("Abstract" in s.heading for s in doc.sections)
    assert any("Introduction" in s.heading for s in doc.sections)
    assert any("References" in s.heading for s in doc.sections)

def test_extract_good_docx():
    docx_path = SAMPLES_DIR / "sample_assignment_good.docx"
    assert docx_path.exists(), "Sample good DOCX must exist"

    doc = extract_docx_document(docx_path, filename="sample_assignment_good.docx")
    assert doc.file_type == "docx"
    assert doc.total_word_count > 250
    assert "Times New Roman" in doc.dominant_font
    assert doc.dominant_font_size_pt == 12.0
    assert abs(doc.avg_margins["top"] - 1.0) < 0.1
    assert any("Abstract" in s.heading for s in doc.sections)
    assert any("References" in s.heading for s in doc.sections)

def test_extract_bad_pdf():
    pdf_path = SAMPLES_DIR / "sample_assignment_bad.pdf"
    assert pdf_path.exists(), "Sample bad PDF must exist"

    doc = extract_pdf_document(pdf_path, filename="sample_assignment_bad.pdf")
    assert doc.file_type == "pdf"
    # Should not have Abstract section
    assert not any("Abstract" in s.heading for s in doc.sections)
