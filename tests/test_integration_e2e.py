"""End-to-End integration tests covering all formats, rubrics, and reporting pipelines."""

from pathlib import Path
import pytest
from src.database import get_recent_audits, log_audit_run
from src.extractor.docx_extractor import extract_docx_document
from src.extractor.pdf_extractor import extract_pdf_document
from src.reporting.json_exporter import export_report_to_json
from src.reporting.pdf_report import generate_pdf_report
from src.rules.default_rubrics import get_builtin_rubrics, get_rubric_by_name
from src.rules.rubric_parser import parse_rubric_from_text
from src.validator.base import IssueSeverity
from src.validator.engine import ComplianceValidator

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"
RUBRICS_DIR = Path(__file__).resolve().parent.parent / "rubrics"

def test_e2e_good_pdf_full_pipeline():
    """Verify conforming PDF passes APA rubric and generates valid reports."""
    pdf_path = SAMPLES_DIR / "sample_assignment_good.pdf"
    doc = extract_pdf_document(pdf_path, filename="sample_assignment_good.pdf")
    rubric = get_rubric_by_name("College Standard APA 7th Edition")

    validator = ComplianceValidator(rubric)
    report = validator.audit_document(doc)

    assert report.overall_score >= 80.0
    assert report.critical_count == 0
    assert report.letter_grade in ["A", "A-", "B+", "B"]

    # Test PDF report generation
    pdf_bytes = generate_pdf_report(report)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")

    # Test JSON export
    json_str = export_report_to_json(report)
    assert '"overall_score":' in json_str
    assert '"letter_grade":' in json_str

def test_e2e_bad_pdf_full_pipeline():
    """Verify non-conforming PDF flags multiple critical violations."""
    pdf_path = SAMPLES_DIR / "sample_assignment_bad.pdf"
    doc = extract_pdf_document(pdf_path, filename="sample_assignment_bad.pdf")
    rubric = get_rubric_by_name("College Standard APA 7th Edition")

    validator = ComplianceValidator(rubric)
    report = validator.audit_document(doc)

    assert report.overall_score < 75.0
    assert report.critical_count > 0

    # Ensure critical flags include missing sections and citation mismatches
    failed_rule_ids = [iss.rule_id for iss in report.issues if not iss.passed]
    assert "struct_sec_abstract" in failed_rule_ids
    assert "fmt_margins" in failed_rule_ids
    assert "cite_in_text_cross_reference" in failed_rule_ids

    # ReportLab should still successfully generate report even with failures
    pdf_bytes = generate_pdf_report(report)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")

def test_e2e_good_docx_full_pipeline():
    """Verify conforming DOCX passes APA rubric."""
    docx_path = SAMPLES_DIR / "sample_assignment_good.docx"
    doc = extract_docx_document(docx_path, filename="sample_assignment_good.docx")
    rubric = get_rubric_by_name("College Standard APA 7th Edition")

    validator = ComplianceValidator(rubric)
    report = validator.audit_document(doc)

    assert report.overall_score >= 80.0
    assert report.critical_count == 0
    assert report.letter_grade in ["A", "A-", "B+", "B"]

def test_e2e_bad_docx_full_pipeline():
    """Verify non-conforming DOCX flags formatting and structural errors."""
    docx_path = SAMPLES_DIR / "sample_assignment_bad.docx"
    doc = extract_docx_document(docx_path, filename="sample_assignment_bad.docx")
    rubric = get_rubric_by_name("College Standard APA 7th Edition")

    validator = ComplianceValidator(rubric)
    report = validator.audit_document(doc)

    assert report.overall_score < 75.0
    assert report.critical_count > 0
    assert any(iss.rule_id == "fmt_margins" and not iss.passed for iss in report.issues)

def test_guideline_text_rubric_parser():
    """Verify plain text guideline parser constructs a valid rubric."""
    guidelines_file = RUBRICS_DIR / "sample_rubric_guidelines.txt"
    assert guidelines_file.exists()
    guide_text = guidelines_file.read_text(encoding="utf-8")

    parsed_rubric = parse_rubric_from_text(guide_text)
    assert parsed_rubric.formatting.expected_font == "Times New Roman"
    assert parsed_rubric.formatting.expected_font_size_pt == 12.0
    assert parsed_rubric.formatting.expected_margin_inches == 1.0
    assert parsed_rubric.citations.citation_style == "APA"
    assert "Abstract" in parsed_rubric.structure.required_sections
    assert "References" in parsed_rubric.structure.required_sections

def test_ieee_rubric_validation():
    """Verify IEEE rubric evaluation detects IEEE specific rules."""
    ieee_rubric = get_rubric_by_name("IEEE Conference Proceedings Format")
    assert ieee_rubric.citations.citation_style == "IEEE"
    assert ieee_rubric.formatting.expected_margin_inches == 0.75
    assert ieee_rubric.formatting.expected_font_size_pt == 10.0
