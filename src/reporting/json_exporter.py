"""JSON export utility for compliance reports."""

import json
from src.validator.base import ComplianceReport

def export_report_to_json(report: ComplianceReport, indent: int = 2) -> str:
    """Serialize compliance report into formatted JSON string."""
    return json.dumps(report.to_dict(), indent=indent, default=str)
