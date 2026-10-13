"""Tests for compliance validators and engine."""

from pathlib import Path
import pytest
from src.extractor.pdf_extractor import extract_pdf_document
from src.rules.default_rubrics import get_builtin_rubrics
from src.rules.schema import RubricRuleSet
from src.validator.engine import ComplianceValidator

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"

def test_validate_good_document():
    rubrics = get_builtin_rubrics()
    apa_rubric = rubrics.get("College Standard APA 7th Edition")
    assert apa_rubric is not None

    pdf_path = SAMPLES_DIR / "sample_assignment_good.pdf"
    doc = extract_pdf_document(pdf_path, filename="sample_assignment_good.pdf")

    validator = ComplianceValidator(apa_rubric)
    report = validator.audit_document(doc)

    assert report.overall_score >= 80.0
    assert report.critical_count == 0
    assert report.letter_grade in ["A", "A-", "B+", "B"]
    assert report.total_rules > 10

def test_validate_bad_document():
    rubrics = get_builtin_rubrics()
    apa_rubric = rubrics.get("College Standard APA 7th Edition")
    assert apa_rubric is not None

    pdf_path = SAMPLES_DIR / "sample_assignment_bad.pdf"
    doc = extract_pdf_document(pdf_path, filename="sample_assignment_bad.pdf")

    validator = ComplianceValidator(apa_rubric)
    report = validator.audit_document(doc)

    # Bad document must have critical issues and lower score
    assert report.overall_score < 75.0
    assert report.critical_count > 0
    # Must flag missing Abstract or missing course code or citation mismatch
    missing_abstract = any(
        iss.rule_id == "struct_sec_abstract" and not iss.passed
        for iss in report.issues
    )
    assert missing_abstract, "Must flag missing Abstract in bad document"
