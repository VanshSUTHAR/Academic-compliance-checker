"""Structural requirements validator."""

from typing import Dict, List, Optional, Set, Tuple
from rapidfuzz import fuzz

from src.extractor.base import ExtractedDocument, SectionBlock
from src.rules.schema import StructureRules
from src.validator.base import IssueSeverity, ValidationCategory, ValidationIssue

SECTION_ALIASES: Dict[str, List[str]] = {
    "abstract": ["abstract", "executive summary", "synopsis"],
    "introduction": ["introduction", "intro", "background", "problem statement", "overview"],
    "literature review": ["literature review", "related work", "prior research", "background"],
    "methodology": ["methodology", "methods", "materials and methods", "experimental setup", "proposed approach", "system architecture"],
    "results": ["results", "findings", "experimental results", "evaluation", "experiments"],
    "discussion": ["discussion", "analysis", "interpretation", "discussion of results"],
    "conclusion": ["conclusion", "conclusions", "concluding remarks", "summary", "conclusion and future work"],
    "references": ["references", "bibliography", "works cited", "reference list", "sources"],
}

def match_section_heading(target: str, candidate: str) -> bool:
    """Determine if a document heading matches a required section using alias and fuzzy matching."""
    t_clean = target.lower().strip()
    c_clean = candidate.lower().strip()

    # Direct match or substring
    if t_clean in c_clean or c_clean in t_clean:
        return True

    # Check aliases
    aliases = SECTION_ALIASES.get(t_clean, [t_clean])
    for alias in aliases:
        if alias in c_clean or c_clean in alias:
            return True
        if fuzz.ratio(alias, c_clean) >= 78:
            return True

    return False

def validate_structure(
    doc: ExtractedDocument,
    rules: StructureRules,
) -> List[ValidationIssue]:
    """Validate mandatory sections, sequence order, and section word counts."""
    issues: List[ValidationIssue] = []
    detected_sections = doc.sections

    # Collect all headings found in document
    found_headings: List[Tuple[str, SectionBlock]] = [
        (s.heading, s) for s in detected_sections
    ]

    matched_sections: Dict[str, Optional[SectionBlock]] = {}
    matched_order_indices: List[Tuple[str, int]] = []

    # 1. Check Presence of each required section
    for req in rules.required_sections:
        found_block: Optional[SectionBlock] = None
        found_index: int = -1

        for idx, (h_text, block) in enumerate(found_headings):
            if match_section_heading(req, h_text):
                found_block = block
                found_index = idx
                break

        matched_sections[req] = found_block
        if found_block:
            matched_order_indices.append((req, found_index))

        is_present = found_block is not None
        issues.append(
            ValidationIssue(
                rule_id=f"struct_sec_{req.lower().replace(' ', '_')}",
                rule_name=f"Required Section: '{req}'",
                category=ValidationCategory.STRUCTURE,
                severity=IssueSeverity.CRITICAL if not is_present else IssueSeverity.INFO,
                passed=is_present,
                description=f"Verifies presence of the mandatory '{req}' section.",
                expected=f"'{req}' section header present",
                actual=f"Found: '{found_block.heading}'" if is_present else "Missing",
                suggested_fix=f"Add a distinct '{req}' section heading with corresponding content.",
            )
        )

    # 2. Check Sequential Order
    if rules.enforce_order and len(matched_order_indices) >= 2:
        order_out_of_sync = []
        indices_list = [idx for (_, idx) in matched_order_indices]
        is_sorted = indices_list == sorted(indices_list)

        if not is_sorted:
            detected_order_names = [name for (name, _) in matched_order_indices]
            expected_order_names = [r for r in rules.required_sections if r in detected_order_names]
            issues.append(
                ValidationIssue(
                    rule_id="struct_section_order",
                    rule_name="Section Sequential Order",
                    category=ValidationCategory.STRUCTURE,
                    severity=IssueSeverity.WARNING,
                    passed=False,
                    description="Checks if required sections appear in the designated chronological sequence.",
                    expected=" -> ".join(expected_order_names),
                    actual=" -> ".join(detected_order_names),
                    suggested_fix="Reorder your document sections to match the rubric's standard sequence.",
                )
            )
        else:
            issues.append(
                ValidationIssue(
                    rule_id="struct_section_order",
                    rule_name="Section Sequential Order",
                    category=ValidationCategory.STRUCTURE,
                    severity=IssueSeverity.INFO,
                    passed=True,
                    description="Checks if required sections appear in the designated chronological sequence.",
                    expected="Sequential rubric order",
                    actual="Valid chronological sequence",
                    suggested_fix="No changes required.",
                )
            )

    # 3. Check Section-Level Word Counts (if specified)
    if rules.min_words_per_section:
        for sec_name, min_words in rules.min_words_per_section.items():
            matched_block = matched_sections.get(sec_name)
            if matched_block:
                actual_words = matched_block.word_count
                passed_word = actual_words >= min_words
                issues.append(
                    ValidationIssue(
                        rule_id=f"struct_word_{sec_name.lower().replace(' ', '_')}",
                        rule_name=f"Word Count: {sec_name}",
                        category=ValidationCategory.STRUCTURE,
                        severity=IssueSeverity.WARNING if not passed_word else IssueSeverity.INFO,
                        passed=passed_word,
                        description=f"Checks if '{sec_name}' section has sufficient depth.",
                        expected=f"≥ {min_words} words",
                        actual=f"{actual_words} words",
                        suggested_fix=f"Expand '{sec_name}' section to meet the minimum threshold of {min_words} words.",
                    )
                )

    return issues
