"""Tests for SQLite audit logging and persistence."""

import tempfile
from pathlib import Path
import pytest
from src.database import get_audit_by_id, get_audit_statistics, get_recent_audits, log_audit_run

def test_database_logging():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db_path = Path(tmp.name)

    try:
        report_data = {
            "overall_score": 92.5,
            "letter_grade": "A-",
            "issues": [],
        }

        row_id = log_audit_run(
            filename="test_paper.pdf",
            file_type="PDF",
            rubric_name="APA 7th",
            compliance_score=92.5,
            letter_grade="A-",
            total_rules=12,
            passed_rules=11,
            failed_rules=1,
            critical_issues=0,
            warning_issues=1,
            info_issues=0,
            report_data=report_data,
            db_path=db_path,
        )

        assert row_id > 0

        # Retrieve recent
        recents = get_recent_audits(limit=10, db_path=db_path)
        assert len(recents) == 1
        assert recents[0]["filename"] == "test_paper.pdf"
        assert recents[0]["compliance_score"] == 92.5

        # Retrieve by id
        record = get_audit_by_id(row_id, db_path=db_path)
        assert record is not None
        assert record["rubric_name"] == "APA 7th"

        # Statistics
        stats = get_audit_statistics(db_path=db_path)
        assert stats["total_audits"] == 1
        assert stats["avg_score"] == 92.5

    finally:
        if db_path.exists():
            db_path.unlink()
