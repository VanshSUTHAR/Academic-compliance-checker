"""Base dataclasses and enums for validation results."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

class IssueSeverity(str, Enum):
    """Severity classification of an audit issue."""
    CRITICAL = "CRITICAL"   # Likely direct grade penalty
    WARNING = "WARNING"     # Inconsistency or guideline deviation
    INFO = "INFO"           # Stylistic suggestion or tip

class ValidationCategory(str, Enum):
    """Rule category classification."""
    FORMATTING = "Formatting"
    STRUCTURE = "Structure"
    CITATIONS = "Citations"
    METADATA = "Submission Metadata"
    CONTENT_QUALITY = "Content Quality"

@dataclass
class ValidationIssue:
    """Represents a single evaluated rule result."""
    rule_id: str
    rule_name: str
    category: ValidationCategory
    severity: IssueSeverity
    passed: bool
    description: str
    expected: str
    actual: str
    suggested_fix: str

@dataclass
class ComplianceReport:
    """Comprehensive compliance evaluation audit report."""
    filename: str
    file_type: str
    rubric_title: str
    timestamp: str
    overall_score: float
    letter_grade: str
    category_scores: Dict[str, float] = field(default_factory=dict)
    total_rules: int = 0
    passed_rules: int = 0
    failed_rules: int = 0
    critical_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)
    document_summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary format for JSON export and DB storage."""
        return {
            "filename": self.filename,
            "file_type": self.file_type,
            "rubric_title": self.rubric_title,
            "timestamp": self.timestamp,
            "overall_score": self.overall_score,
            "letter_grade": self.letter_grade,
            "category_scores": self.category_scores,
            "total_rules": self.total_rules,
            "passed_rules": self.passed_rules,
            "failed_rules": self.failed_rules,
            "critical_count": self.critical_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "issues": [
                {
                    "rule_id": iss.rule_id,
                    "rule_name": iss.rule_name,
                    "category": iss.category.value,
                    "severity": iss.severity.value,
                    "passed": iss.passed,
                    "description": iss.description,
                    "expected": iss.expected,
                    "actual": iss.actual,
                    "suggested_fix": iss.suggested_fix,
                }
                for iss in self.issues
            ],
            "document_summary": self.document_summary,
        }
