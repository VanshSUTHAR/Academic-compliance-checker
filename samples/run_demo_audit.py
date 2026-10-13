"""Interactive demonstration script performing an end-to-end compliance audit from the CLI."""

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.database import get_recent_audits, log_audit_run
from src.extractor.pdf_extractor import extract_pdf_document
from src.reporting.pdf_report import generate_pdf_report
from src.rules.default_rubrics import get_rubric_by_name
from src.validator.engine import ComplianceValidator

# Configure stdout for UTF-8 on Windows
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def run_demo():
    print("=" * 70)
    print("[ACE] ACADEMIC COMPLIANCE AUDIT ENGINE -- CLI DEMONSTRATION")
    print("=" * 70)

    # 1. Load Rubric
    rubric_name = "College Standard APA 7th Edition"
    rubric = get_rubric_by_name(rubric_name)
    print(f"\n[1] Loaded Rubric: {rubric.title}")
    print(f"    Expected Font: {rubric.formatting.expected_font} ({rubric.formatting.expected_font_size_pt} pt)")
    print(f"    Required Margins: {rubric.formatting.expected_margin_inches} inch")
    print(f"    Required Sections: {', '.join(rubric.structure.required_sections)}")
    print(f"    Citation Style: {rubric.citations.citation_style}")

    # 2. Audit Conforming Paper
    good_pdf = root_dir / "samples" / "sample_assignment_good.pdf"
    print(f"\n[2] Auditing Conforming Submission: {good_pdf.name}")
    doc_good = extract_pdf_document(good_pdf, filename=good_pdf.name)
    validator = ComplianceValidator(rubric)
    report_good = validator.audit_document(doc_good)

    print(f"    ⭐ Overall Compliance Score: {report_good.overall_score}% (Grade: {report_good.letter_grade})")
    print(f"    ✅ Passed Rules: {report_good.passed_rules} / {report_good.total_rules}")
    print(f"    🔴 Critical Violations: {report_good.critical_count}")
    print(f"    🟡 Warnings: {report_good.warning_count}")
    print("    Category Breakdown:")
    for cat, score in report_good.category_scores.items():
        print(f"      - {cat:<22}: {score:>5.1f}%")

    # 3. Audit Non-Conforming Paper
    bad_pdf = root_dir / "samples" / "sample_assignment_bad.pdf"
    print(f"\n[3] Auditing Non-Conforming Submission: {bad_pdf.name}")
    doc_bad = extract_pdf_document(bad_pdf, filename=bad_pdf.name)
    report_bad = validator.audit_document(doc_bad)

    print(f"    ⚠️  Overall Compliance Score: {report_bad.overall_score}% (Grade: {report_bad.letter_grade})")
    print(f"    ❌ Passed Rules: {report_bad.passed_rules} / {report_bad.total_rules}")
    print(f"    🔴 Critical Violations: {report_bad.critical_count}")
    print(f"    🟡 Warnings: {report_bad.warning_count}")
    print("\n    Flagged Non-Compliance Issues:")
    for iss in report_bad.issues:
        if not iss.passed:
            badge = "[CRITICAL]" if iss.severity.value == "CRITICAL" else "[WARNING]"
            print(f"      {badge:<10} {iss.rule_name}")
            print(f"                 Expected: {iss.expected}")
            print(f"                 Found:    {iss.actual}")
            print(f"                 Fix:      {iss.suggested_fix}")

    # 4. Generate PDF Certificate
    out_cert_path = root_dir / "samples" / "sample_audit_certificate.pdf"
    pdf_bytes = generate_pdf_report(report_good)
    out_cert_path.write_bytes(pdf_bytes)
    print(f"\n[4] Generated PDF Audit Certificate: {out_cert_path.name} ({len(pdf_bytes)} bytes)")

    # 5. Log to SQLite
    row_id = log_audit_run(
        filename=report_good.filename,
        file_type=report_good.file_type,
        rubric_name=report_good.rubric_title,
        compliance_score=report_good.overall_score,
        letter_grade=report_good.letter_grade,
        total_rules=report_good.total_rules,
        passed_rules=report_good.passed_rules,
        failed_rules=report_good.failed_rules,
        critical_issues=report_good.critical_count,
        warning_issues=report_good.warning_count,
        info_issues=report_good.info_count,
        report_data=report_good.to_dict(),
    )
    print(f"[5] Audit logged to SQLite database (Row ID: {row_id})")

    # 6. Verify SQLite
    recent = get_recent_audits(limit=1)
    print(f"    Verified from DB: Most recent audit = {recent[0]['filename']} ({recent[0]['compliance_score']}%)")

    print("\n" + "=" * 70)
    print("✅ DEMONSTRATION & VERIFICATION COMPLETE — ALL SYSTEMS OPERATIONAL")
    print("=" * 70)

if __name__ == "__main__":
    run_demo()
