"""Citations and references validator with cross-referencing capabilities."""

import re
from typing import Dict, List, Set, Tuple
from src.extractor.base import ExtractedDocument
from src.rules.schema import CitationRules
from src.validator.base import IssueSeverity, ValidationCategory, ValidationIssue

APA_IN_TEXT_REGEX = re.compile(
    r"\(([A-Z][a-zA-Z\.\s\-]+?(?:\s*(?:&|and)\s*[A-Z][a-zA-Z\.\s\-]+?|\s+et\s+al\.)?),\s*(\d{4}[a-z]?)(?:,\s*p\.?\s*\d+)?\)",
)
IEEE_IN_TEXT_REGEX = re.compile(r"\[(\d{1,3})\]")
MLA_IN_TEXT_REGEX = re.compile(r"\(([A-Z][a-zA-Z\-]+)\s+(\d{1,4})\)")
HARVARD_IN_TEXT_REGEX = re.compile(r"\(([A-Z][a-zA-Z\-]+(?:,\s*\d{4}|\s+\d{4}))\)")

def extract_references_section_text(doc: ExtractedDocument) -> str:
    """Find and return the text belonging to the References / Bibliography section."""
    for sec in doc.sections:
        if sec.heading.lower().strip() in ["references", "bibliography", "works cited", "reference list"]:
            if sec.content.strip():
                return sec.content

    # Fallback search within full text
    matches = list(re.finditer(r"(?:\n|^)(?:references|bibliography|works cited)\s*\n", doc.full_text, flags=re.IGNORECASE))
    if matches:
        last_match = matches[-1]
        return doc.full_text[last_match.end():]

    return ""

def parse_reference_entries(ref_text: str) -> List[str]:
    """Split reference block into individual source entries."""
    if not ref_text.strip():
        return []
    lines = [ln.strip() for ln in ref_text.split("\n") if ln.strip()]
    entries: List[str] = []
    current_entry = ""

    for line in lines:
        # Check if line begins a new reference (e.g. [1], author last name, hanging indent)
        if re.match(r"^(?:\[\d+\]|\d+\.|\([A-Z]\)|[A-Z][a-zA-Z\-]+,)", line):
            if current_entry:
                entries.append(current_entry)
            current_entry = line
        else:
            if current_entry:
                current_entry += " " + line
            else:
                current_entry = line

    if current_entry:
        entries.append(current_entry)

    # If simple splitting didn't yield multiple, treat non-empty lines as entries
    if len(entries) <= 1 and len(lines) > 1:
        return lines

    return entries

def validate_citations(
    doc: ExtractedDocument,
    rules: CitationRules,
) -> List[ValidationIssue]:
    """Validate reference list presence, minimum references count, citation style, and cross-references."""
    issues: List[ValidationIssue] = []

    if rules.citation_style == "None":
        return issues

    ref_text = extract_references_section_text(doc)
    has_ref_section = bool(ref_text.strip())
    entries = parse_reference_entries(ref_text)
    entry_count = len(entries)

    # 1. Reference List Present
    issues.append(
        ValidationIssue(
            rule_id="cite_reference_list_present",
            rule_name="References Section Present",
            category=ValidationCategory.CITATIONS,
            severity=IssueSeverity.CRITICAL if not has_ref_section else IssueSeverity.INFO,
            passed=has_ref_section,
            description="Checks if a dedicated References or Bibliography section exists at the end of the document.",
            expected="References section present",
            actual="Present" if has_ref_section else "Missing",
            suggested_fix="Append a terminal 'References' section containing all cited literature.",
        )
    )

    # 2. Minimum References Count
    min_refs = rules.min_references_count
    count_passed = entry_count >= min_refs
    issues.append(
        ValidationIssue(
            rule_id="cite_minimum_count",
            rule_name="Minimum Reference Sources",
            category=ValidationCategory.CITATIONS,
            severity=IssueSeverity.WARNING if not count_passed else IssueSeverity.INFO,
            passed=count_passed,
            description=f"Checks if bibliography contains at least {min_refs} peer-reviewed or authoritative sources.",
            expected=f"≥ {min_refs} sources",
            actual=f"{entry_count} sources detected",
            suggested_fix=f"Include at least {min_refs} complete bibliographic entries in your References list.",
        )
    )

    # 3. Detect In-Text Citations based on Style
    target_style = rules.citation_style.upper()
    body_text = doc.full_text
    if ref_text and ref_text in body_text:
        # Exclude references section when scanning for body in-text citations
        body_text = body_text.replace(ref_text, "")

    in_text_authors: Set[str] = set()
    in_text_numbers: Set[int] = set()

    if target_style == "IEEE":
        num_matches = IEEE_IN_TEXT_REGEX.findall(body_text)
        in_text_numbers = {int(n) for n in num_matches if int(n) < 500}
        style_detected = len(in_text_numbers) > 0
    elif target_style == "MLA":
        mla_matches = MLA_IN_TEXT_REGEX.findall(body_text)
        in_text_authors = {m[0].strip() for m in mla_matches}
        style_detected = len(in_text_authors) > 0
    else:  # APA or Harvard
        apa_matches = APA_IN_TEXT_REGEX.findall(body_text)
        for author_str, year in apa_matches:
            # Get primary author last name
            first_author = author_str.split()[0].replace(",", "").replace(".", "").strip()
            if len(first_author) > 2:
                in_text_authors.add(first_author)
        style_detected = len(in_text_authors) > 0

    issues.append(
        ValidationIssue(
            rule_id="cite_style_consistency",
            rule_name=f"Citation Style Consistency ({target_style})",
            category=ValidationCategory.CITATIONS,
            severity=IssueSeverity.WARNING if not style_detected else IssueSeverity.INFO,
            passed=style_detected,
            description=f"Checks if in-text citations follow standard {target_style} formatting.",
            expected=f"{target_style} format (e.g. {'[1], [2]' if target_style == 'IEEE' else '(Author, Year)'})",
            actual=f"Found {len(in_text_numbers) if target_style == 'IEEE' else len(in_text_authors)} {target_style} citation markers" if style_detected else "No matching citation patterns detected in body",
            suggested_fix=f"Ensure citations in the text follow {target_style} style standards.",
        )
    )

    # 4. In-text vs References Cross-Referencing
    if rules.cross_reference_in_text and has_ref_section:
        missing_in_refs: List[str] = []
        unreferenced_in_body: List[str] = []

        if target_style == "IEEE":
            for num in in_text_numbers:
                if not any(f"[{num}]" in ent or f"{num}." in ent for ent in entries):
                    missing_in_refs.append(f"[{num}]")
        else:
            # Check APA / Author-Date
            for author in in_text_authors:
                found = any(author.lower() in ent.lower() for ent in entries)
                if not found:
                    missing_in_refs.append(author)

        cross_ref_passed = len(missing_in_refs) == 0
        issues.append(
            ValidationIssue(
                rule_id="cite_in_text_cross_reference",
                rule_name="In-Text to Bibliography Match",
                category=ValidationCategory.CITATIONS,
                severity=IssueSeverity.CRITICAL if not cross_ref_passed else IssueSeverity.INFO,
                passed=cross_ref_passed,
                description="Cross-references each in-text citation against the references list to identify missing entries.",
                expected="All in-text citations present in References",
                actual="100% Match" if cross_ref_passed else f"Missing from References: {', '.join(missing_in_refs[:5])}",
                suggested_fix="Add the corresponding bibliographic citation entries for all cited sources in the References list.",
            )
        )

    return issues
