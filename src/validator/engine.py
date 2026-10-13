"""Core Compliance Validator Engine orchestrating all audits."""

from datetime import datetime, timezone
from typing import Dict, List
from src.extractor.base import ExtractedDocument
from src.rules.schema import RubricRuleSet
from src.validator.base import (
    ComplianceReport,
    IssueSeverity,
    ValidationCategory,
    ValidationIssue,
)
from src.validator.citations import validate_citations
from src.validator.content_quality import validate_content_quality
from src.validator.formatting import validate_formatting
from src.validator.metadata import validate_metadata
from src.validator.structure import validate_structure

CATEGORY_WEIGHTS: Dict[ValidationCategory, float] = {
    ValidationCategory.FORMATTING: 0.25,
    ValidationCategory.STRUCTURE: 0.25,
    ValidationCategory.CITATIONS: 0.25,
    ValidationCategory.METADATA: 0.15,
    ValidationCategory.CONTENT_QUALITY: 0.10,
}

def calculate_letter_grade(score: float) -> str:
    """Map a percentage score to standard academic letter grades."""
    if score >= 94.0:
        return "A"
    if score >= 90.0:
        return "A-"
    if score >= 87.0:
        return "B+"
    if score >= 83.0:
        return "B"
    if score >= 80.0:
        return "B-"
    if score >= 75.0:
        return "C+"
    if score >= 70.0:
        return "C"
    if score >= 60.0:
        return "D"
    return "F"

class ComplianceValidator:
    """Orchestrates comprehensive document compliance evaluation against a rubric."""

    def __init__(self, rubric: RubricRuleSet):
        self.rubric = rubric

    def audit_document(self, doc: ExtractedDocument) -> ComplianceReport:
        """Run all validators and compile the complete compliance audit report."""
        all_issues: List[ValidationIssue] = []

        # Run modular validators
        all_issues.extend(validate_formatting(doc, self.rubric.formatting))
        all_issues.extend(validate_structure(doc, self.rubric.structure))
        all_issues.extend(validate_citations(doc, self.rubric.citations))
        all_issues.extend(validate_metadata(doc, self.rubric.metadata))
        all_issues.extend(validate_content_quality(doc, self.rubric.content_quality))

        # Calculate category pass rates
        category_issues: Dict[str, List[ValidationIssue]] = {}
        for issue in all_issues:
            cat_name = issue.category.value
            category_issues.setdefault(cat_name, []).append(issue)

        category_scores: Dict[str, float] = {}
        weighted_score_total = 0.0
        total_weight_applied = 0.0

        for cat_enum, weight in CATEGORY_WEIGHTS.items():
            cat_name = cat_enum.value
            cat_list = category_issues.get(cat_name, [])
            if cat_list:
                passed_in_cat = sum(1 for iss in cat_list if iss.passed)
                score_ratio = (passed_in_cat / len(cat_list)) * 100.0
                category_scores[cat_name] = round(score_ratio, 1)
                weighted_score_total += score_ratio * weight
                total_weight_applied += weight

        overall_score = round(weighted_score_total / total_weight_applied, 1) if total_weight_applied > 0 else 0.0
        letter_grade = calculate_letter_grade(overall_score)

        # Count issue severity breakdown
        total_rules = len(all_issues)
        passed_rules = sum(1 for iss in all_issues if iss.passed)
        failed_rules = total_rules - passed_rules

        critical_count = sum(1 for iss in all_issues if not iss.passed and iss.severity == IssueSeverity.CRITICAL)
        warning_count = sum(1 for iss in all_issues if not iss.passed and iss.severity == IssueSeverity.WARNING)
        info_count = sum(1 for iss in all_issues if not iss.passed and iss.severity == IssueSeverity.INFO)

        doc_summary = {
            "page_count": doc.page_count,
            "word_count": doc.total_word_count,
            "dominant_font": doc.dominant_font,
            "font_size_pt": doc.dominant_font_size_pt,
            "margins": doc.avg_margins,
            "line_spacing": doc.detected_line_spacing,
            "page_size": doc.page_size_label,
            "sections_found": [s.heading for s in doc.sections],
            "is_scanned": doc.is_scanned,
        }

        return ComplianceReport(
            filename=doc.filename,
            file_type=doc.file_type.upper(),
            rubric_title=self.rubric.title,
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            overall_score=overall_score,
            letter_grade=letter_grade,
            category_scores=category_scores,
            total_rules=total_rules,
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            critical_count=critical_count,
            warning_count=warning_count,
            info_count=info_count,
            issues=all_issues,
            document_summary=doc_summary,
        )
