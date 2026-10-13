"""Submission metadata validator for verifying student information on cover page / headers."""

import re
from typing import List, Tuple
from src.extractor.base import ExtractedDocument
from src.rules.schema import MetadataRules
from src.validator.base import IssueSeverity, ValidationCategory, ValidationIssue

STUDENT_NAME_PATTERNS = [
    re.compile(r"(?:student\s*name|name|author|submitted\s*by)\s*[:\-]\s*([A-Za-z\.\s]{3,40})", re.IGNORECASE),
    re.compile(r"(?:by\s+)([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})"),
]

STUDENT_ID_PATTERNS = [
    re.compile(r"(?:student\s*id|id\s*(?:no|number)?|roll\s*no|reg\s*no|matriculation)\s*[:#\-]?\s*([A-Za-z0-9\-_]{4,20})", re.IGNORECASE),
    re.compile(r"\b(?:stu|id|roll)[\-_]\d{4,10}\b", re.IGNORECASE),
]

DATE_PATTERNS = [
    re.compile(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b", re.IGNORECASE),
    re.compile(r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b", re.IGNORECASE),
    re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"),
    re.compile(r"\b\d{4}[/-]\d{2}[/-]\d{2}\b"),
    re.compile(r"(?:date|submitted\s*on)\s*[:\-]\s*([A-Za-z0-9\s,\/\-]+)", re.IGNORECASE),
]

def search_text_for_patterns(text: str, patterns: List[re.Pattern]) -> Tuple[bool, str]:
    """Search target text using a list of compiled regex patterns."""
    for pat in patterns:
        m = pat.search(text)
        if m:
            matched_val = m.group(1).strip() if m.groups() else m.group(0).strip()
            # Filter trivial matches
            if len(matched_val) >= 2 and not matched_val.lower().startswith("table"):
                return True, matched_val
    return False, ""

def validate_metadata(
    doc: ExtractedDocument,
    rules: MetadataRules,
) -> List[ValidationIssue]:
    """Validate student name, ID, course code, and date presence on the first page or header."""
    issues: List[ValidationIssue] = []

    # Scrape search space: First page text + headers
    search_space = doc.first_page_text + "\n" + "\n".join(doc.headers_and_footers)
    if not rules.header_or_cover_only:
        search_space = doc.full_text

    # 1. Student Name Check
    if rules.require_student_name:
        name_found, detected_name = search_text_for_patterns(search_space, STUDENT_NAME_PATTERNS)
        issues.append(
            ValidationIssue(
                rule_id="meta_student_name",
                rule_name="Student Name",
                category=ValidationCategory.METADATA,
                severity=IssueSeverity.WARNING if not name_found else IssueSeverity.INFO,
                passed=name_found,
                description="Checks if author or student name is present on the cover page or header.",
                expected="Student name displayed",
                actual=f"Found: '{detected_name}'" if name_found else "Missing",
                suggested_fix="Include your full name on the title page or document header.",
            )
        )

    # 2. Student ID Check
    if rules.require_student_id:
        id_found, detected_id = search_text_for_patterns(search_space, STUDENT_ID_PATTERNS)
        issues.append(
            ValidationIssue(
                rule_id="meta_student_id",
                rule_name="Student ID / Roll Number",
                category=ValidationCategory.METADATA,
                severity=IssueSeverity.WARNING if not id_found else IssueSeverity.INFO,
                passed=id_found,
                description="Checks if student ID, Roll number, or Matriculation code is clearly declared.",
                expected="Student ID / Roll number displayed",
                actual=f"Found: '{detected_id}'" if id_found else "Missing",
                suggested_fix="Add your Student ID / Roll number below your name on the cover page.",
            )
        )

    # 3. Course Code Check
    if rules.require_course_code:
        course_pattern = re.compile(rules.course_code_pattern, re.IGNORECASE) if rules.course_code_pattern else None
        course_found = False
        detected_course = ""

        if course_pattern:
            m = course_pattern.search(search_space)
            if m:
                course_found = True
                detected_course = m.group(0).strip()
        else:
            course_found = bool(re.search(r"course\s*[:\-]\s*[A-Z0-9\s]+", search_space, re.IGNORECASE))

        issues.append(
            ValidationIssue(
                rule_id="meta_course_code",
                rule_name="Course Code",
                category=ValidationCategory.METADATA,
                severity=IssueSeverity.WARNING if not course_found else IssueSeverity.INFO,
                passed=course_found,
                description="Checks if course identification code is provided (e.g. CS-101, BIO-204).",
                expected=f"Course code matching pattern '{rules.course_code_pattern}'",
                actual=f"Found: '{detected_course}'" if course_found else "Missing",
                suggested_fix="Add the course code (e.g., CS-401) on the cover page or header.",
            )
        )

    # 4. Date Check
    if rules.require_date:
        date_found, detected_date = search_text_for_patterns(search_space, DATE_PATTERNS)
        issues.append(
            ValidationIssue(
                rule_id="meta_submission_date",
                rule_name="Submission Date",
                category=ValidationCategory.METADATA,
                severity=IssueSeverity.INFO,
                passed=date_found,
                description="Checks if a submission date is recorded on the title page or header.",
                expected="Submission date present",
                actual=f"Found: '{detected_date}'" if date_found else "Missing",
                suggested_fix="Include the submission date (e.g., October 14, 2024) on the cover page.",
            )
        )

    return issues
