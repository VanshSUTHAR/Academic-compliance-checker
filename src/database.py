"""Database access layer for storing compliance check history and audit logs."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.config import DATABASE_PATH

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    rubric_name TEXT NOT NULL,
    compliance_score REAL NOT NULL,
    letter_grade TEXT NOT NULL,
    total_rules INTEGER NOT NULL,
    passed_rules INTEGER NOT NULL,
    failed_rules INTEGER NOT NULL,
    critical_issues INTEGER NOT NULL,
    warning_issues INTEGER NOT NULL,
    info_issues INTEGER NOT NULL,
    report_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_filename ON audit_logs(filename);
"""

@contextmanager
def get_connection(db_path: Optional[Path] = None):
    """Yield an active connection with Row factory enabled and close on exit."""
    target_path = db_path or DATABASE_PATH
    conn = sqlite3.connect(str(target_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db(db_path: Optional[Path] = None) -> None:
    """Initialize the audit logs table and indices."""
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()

def log_audit_run(
    filename: str,
    file_type: str,
    rubric_name: str,
    compliance_score: float,
    letter_grade: str,
    total_rules: int,
    passed_rules: int,
    failed_rules: int,
    critical_issues: int,
    warning_issues: int,
    info_issues: int,
    report_data: Dict[str, Any],
    db_path: Optional[Path] = None,
) -> int:
    """Log an audit run and return the newly inserted row ID."""
    init_db(db_path)
    now_iso = datetime.now(timezone.utc).isoformat()
    serialized_report = json.dumps(report_data, default=str)

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO audit_logs (
                timestamp, filename, file_type, rubric_name,
                compliance_score, letter_grade, total_rules,
                passed_rules, failed_rules, critical_issues,
                warning_issues, info_issues, report_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                now_iso,
                filename,
                file_type,
                rubric_name,
                round(compliance_score, 1),
                letter_grade,
                total_rules,
                passed_rules,
                failed_rules,
                critical_issues,
                warning_issues,
                info_issues,
                serialized_report,
            ),
        )
        conn.commit()
        return cursor.lastrowid or 0

def get_recent_audits(limit: int = 50, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Retrieve the most recent audit runs."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, timestamp, filename, file_type, rubric_name,
                   compliance_score, letter_grade, total_rules,
                   passed_rules, failed_rules, critical_issues,
                   warning_issues, info_issues, report_json
            FROM audit_logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_audit_by_id(audit_id: int, db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Retrieve a single audit log by its ID."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, timestamp, filename, file_type, rubric_name,
                   compliance_score, letter_grade, total_rules,
                   passed_rules, failed_rules, critical_issues,
                   warning_issues, info_issues, report_json
            FROM audit_logs
            WHERE id = ?
            """,
            (audit_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

def get_audit_statistics(db_path: Optional[Path] = None) -> Dict[str, Any]:
    """Retrieve aggregate statistics across all past audits."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total_audits,
                AVG(compliance_score) as avg_score,
                MAX(compliance_score) as max_score,
                MIN(compliance_score) as min_score,
                SUM(passed_rules) as total_passed_rules,
                SUM(failed_rules) as total_failed_rules
            FROM audit_logs
            """
        )
        row = cursor.fetchone()
        if not row or row["total_audits"] == 0:
            return {
                "total_audits": 0,
                "avg_score": 0.0,
                "max_score": 0.0,
                "min_score": 0.0,
                "total_passed_rules": 0,
                "total_failed_rules": 0,
            }
        return {
            "total_audits": row["total_audits"],
            "avg_score": round(row["avg_score"] or 0.0, 1),
            "max_score": round(row["max_score"] or 0.0, 1),
            "min_score": round(row["min_score"] or 0.0, 1),
            "total_passed_rules": row["total_passed_rules"] or 0,
            "total_failed_rules": row["total_failed_rules"] or 0,
        }
