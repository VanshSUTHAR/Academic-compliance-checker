"""Formatting specifications validator."""

from typing import List
from src.extractor.base import ExtractedDocument
from src.rules.schema import FormattingRules
from src.validator.base import IssueSeverity, ValidationCategory, ValidationIssue

def validate_formatting(
    doc: ExtractedDocument,
    rules: FormattingRules,
) -> List[ValidationIssue]:
    """Validate font, font size, margins, line spacing, word and page counts."""
    issues: List[ValidationIssue] = []

    # 1. Font Family Check
    dominant_font = doc.dominant_font
    expected_font = rules.expected_font
    allowed_fonts = [f.lower() for f in rules.allowed_fonts] if rules.allowed_fonts else [expected_font.lower()]

    font_matched = any(f in dominant_font.lower() for f in allowed_fonts)
    issues.append(
        ValidationIssue(
            rule_id="fmt_font_family",
            rule_name="Body Font Family",
            category=ValidationCategory.FORMATTING,
            severity=IssueSeverity.WARNING if font_matched else IssueSeverity.CRITICAL,
            passed=font_matched,
            description="Checks if dominant body text uses required font family.",
            expected=f"{expected_font} (or: {', '.join(rules.allowed_fonts)})",
            actual=dominant_font,
            suggested_fix=f"Select all body text and change font to '{expected_font}'.",
        )
    )

    # 2. Font Size Check
    actual_size = doc.dominant_font_size_pt
    exp_size = rules.expected_font_size_pt
    tol_size = rules.font_size_tolerance_pt
    size_passed = abs(actual_size - exp_size) <= tol_size

    issues.append(
        ValidationIssue(
            rule_id="fmt_font_size",
            rule_name="Body Font Size",
            category=ValidationCategory.FORMATTING,
            severity=IssueSeverity.WARNING if not size_passed else IssueSeverity.INFO,
            passed=size_passed,
            description="Checks if body font size is within the allowed tolerance.",
            expected=f"{exp_size} pt (±{tol_size} pt)",
            actual=f"{actual_size} pt",
            suggested_fix=f"Ensure standard paragraphs are set to {exp_size} pt font size.",
        )
    )

    # 3. Margins Check
    exp_margin = rules.expected_margin_inches
    tol_margin = rules.margin_tolerance_inches
    margins = doc.avg_margins

    margin_failures = []
    for side in ["top", "bottom", "left", "right"]:
        val = margins.get(side, 1.0)
        if abs(val - exp_margin) > tol_margin:
            margin_failures.append(f"{side}: {val}\"")

    margins_passed = len(margin_failures) == 0
    actual_margin_str = f"Top: {margins.get('top', 0)}\", Bottom: {margins.get('bottom', 0)}\", Left: {margins.get('left', 0)}\", Right: {margins.get('right', 0)}\""
    
    issues.append(
        ValidationIssue(
            rule_id="fmt_margins",
            rule_name="Page Margins",
            category=ValidationCategory.FORMATTING,
            severity=IssueSeverity.WARNING if not margins_passed else IssueSeverity.INFO,
            passed=margins_passed,
            description="Checks if page margins conform to the standard layout dimensions.",
            expected=f"{exp_margin}\" on all sides (±{tol_margin}\")",
            actual=actual_margin_str if margins_passed else f"Non-conforming: {', '.join(margin_failures)}",
            suggested_fix=f"Set Document Margins to {exp_margin} inches (Normal Margins in Word / Page Setup).",
        )
    )

    # 4. Line Spacing Check
    exp_spacing = rules.expected_line_spacing
    act_spacing = doc.detected_line_spacing
    spacing_passed = abs(act_spacing - exp_spacing) < 0.4

    issues.append(
        ValidationIssue(
            rule_id="fmt_line_spacing",
            rule_name="Line Spacing",
            category=ValidationCategory.FORMATTING,
            severity=IssueSeverity.WARNING if not spacing_passed else IssueSeverity.INFO,
            passed=spacing_passed,
            description="Checks if paragraph line spacing matches specification (1.0, 1.5, or 2.0).",
            expected=f"{exp_spacing}x ({'Double' if exp_spacing == 2.0 else '1.5x' if exp_spacing == 1.5 else 'Single'})",
            actual=f"{act_spacing}x",
            suggested_fix=f"Adjust line spacing in paragraph settings to {exp_spacing}x.",
        )
    )

    # 5. Page Size Check
    if rules.expected_page_size and rules.expected_page_size != "Any":
        page_size_passed = doc.page_size_label == rules.expected_page_size
        issues.append(
            ValidationIssue(
                rule_id="fmt_page_size",
                rule_name="Page Paper Size",
                category=ValidationCategory.FORMATTING,
                severity=IssueSeverity.WARNING if not page_size_passed else IssueSeverity.INFO,
                passed=page_size_passed,
                description="Checks whether document uses standard paper dimension (Letter or A4).",
                expected=rules.expected_page_size,
                actual=doc.page_size_label,
                suggested_fix=f"Change Page Setup paper size to {rules.expected_page_size}.",
            )
        )

    # 6. Word Count Check
    total_words = doc.total_word_count
    word_count_passed = True
    word_err_msg = ""

    if rules.min_word_count and total_words < rules.min_word_count:
        word_count_passed = False
        word_err_msg = f"{total_words} words (Deficit of {rules.min_word_count - total_words} words)"
    elif rules.max_word_count and total_words > rules.max_word_count:
        word_count_passed = False
        word_err_msg = f"{total_words} words (Exceeds by {total_words - rules.max_word_count} words)"

    issues.append(
        ValidationIssue(
            rule_id="fmt_word_count",
            rule_name="Total Word Count",
            category=ValidationCategory.FORMATTING,
            severity=IssueSeverity.CRITICAL if not word_count_passed else IssueSeverity.INFO,
            passed=word_count_passed,
            description="Checks if total document length falls within permissible word count limits.",
            expected=f"{rules.min_word_count or 0} - {rules.max_word_count or 'Unlimited'} words",
            actual=f"{total_words} words" if word_count_passed else word_err_msg,
            suggested_fix="Expand your content or condense text to satisfy the required word count range.",
        )
    )

    # 7. Page Count Check
    if rules.min_page_count or rules.max_page_count:
        page_cnt = doc.page_count
        page_passed = True
        page_msg = f"{page_cnt} pages"
        if rules.min_page_count and page_cnt < rules.min_page_count:
            page_passed = False
            page_msg = f"{page_cnt} pages (Below minimum of {rules.min_page_count})"
        elif rules.max_page_count and page_cnt > rules.max_page_count:
            page_passed = False
            page_msg = f"{page_cnt} pages (Above maximum of {rules.max_page_count})"

        issues.append(
            ValidationIssue(
                rule_id="fmt_page_count",
                rule_name="Page Count",
                category=ValidationCategory.FORMATTING,
                severity=IssueSeverity.WARNING if not page_passed else IssueSeverity.INFO,
                passed=page_passed,
                description="Checks if the number of pages meets course guidelines.",
                expected=f"{rules.min_page_count or 1} - {rules.max_page_count or 'Unlimited'} pages",
                actual=page_msg,
                suggested_fix="Verify document layout and ensure content satisfies the page requirements.",
            )
        )

    return issues
