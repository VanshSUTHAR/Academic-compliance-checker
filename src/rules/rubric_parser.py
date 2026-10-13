"""Converts raw guideline text or syllabus files into structured RubricRuleSet JSON."""

import json
import re
from typing import Optional
from src.config import GEMINI_API_KEY, GEMINI_MODEL, OPENAI_API_KEY, OPENAI_MODEL
from src.rules.schema import (
    CitationRules,
    ContentQualityRules,
    FormattingRules,
    MetadataRules,
    RubricRuleSet,
    StructureRules,
)

LLM_PROMPT = """You are an academic compliance rubric parser. 
Convert the provided assignment guidelines into a valid JSON object matching this schema:

{
  "rubric_id": "parsed_custom_rubric",
  "title": "<Short descriptive title>",
  "description": "<Summary of requirements>",
  "formatting": {
    "expected_font": "Times New Roman",
    "allowed_fonts": ["Times New Roman", "Arial"],
    "expected_font_size_pt": 12.0,
    "font_size_tolerance_pt": 0.75,
    "expected_margin_inches": 1.0,
    "margin_tolerance_inches": 0.15,
    "expected_line_spacing": 2.0,
    "expected_page_size": "Letter",
    "min_word_count": 1500,
    "max_word_count": 3500,
    "min_page_count": 3,
    "max_page_count": 10
  },
  "structure": {
    "required_sections": ["Abstract", "Introduction", "Methodology", "Results", "Discussion", "Conclusion", "References"],
    "enforce_order": true,
    "min_words_per_section": {"Abstract": 100}
  },
  "citations": {
    "citation_style": "APA",
    "require_reference_list": true,
    "min_references_count": 3,
    "cross_reference_in_text": true
  },
  "metadata": {
    "require_student_name": true,
    "require_student_id": true,
    "require_course_code": true,
    "course_code_pattern": "[A-Z]{2,4}\\\\s*[-_]?\\\\s*\\\\d{3,4}",
    "require_date": true,
    "header_or_cover_only": true
  },
  "content_quality": {
    "max_sentence_length_words": 35,
    "forbidden_vague_words": ["things", "stuff", "very good", "obviously"],
    "min_lexical_diversity": 0.35,
    "enable_llm_quality_review": false
  }
}

Return ONLY the raw JSON block without any markdown wrapping or explanation.
"""

def parse_guidelines_with_openai(text: str) -> Optional[RubricRuleSet]:
    """Parse rubric text using OpenAI."""
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": LLM_PROMPT},
            {"role": "user", "content": f"Assignment Guidelines:\n\n{text}"},
        ],
        temperature=0.0,
    )
    raw_content = response.choices[0].message.content or "{}"
    raw_content = re.sub(r"^```json\s*", "", raw_content, flags=re.MULTILINE)
    raw_content = re.sub(r"```$", "", raw_content, flags=re.MULTILINE).strip()
    data = json.loads(raw_content)
    return RubricRuleSet(**data)

def parse_guidelines_with_gemini(text: str) -> Optional[RubricRuleSet]:
    """Parse rubric text using Google Gemini."""
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(f"{LLM_PROMPT}\n\nAssignment Guidelines:\n\n{text}")
    raw_content = response.text or "{}"
    raw_content = re.sub(r"^```json\s*", "", raw_content, flags=re.MULTILINE)
    raw_content = re.sub(r"```$", "", raw_content, flags=re.MULTILINE).strip()
    data = json.loads(raw_content)
    return RubricRuleSet(**data)

def parse_guidelines_heuristically(text: str) -> RubricRuleSet:
    """Deterministic regex heuristic parser for offline / local mode."""
    lower = text.lower()

    # Font
    font = "Times New Roman"
    if "arial" in lower:
        font = "Arial"
    elif "calibri" in lower:
        font = "Calibri"
    elif "georgia" in lower:
        font = "Georgia"

    # Font size
    size_pt = 12.0
    size_match = re.search(r"(\d{1,2}(?:\.\d)?)\s*(?:pt|point|px)\b", lower)
    if size_match:
        try:
            size_pt = float(size_match.group(1))
        except ValueError:
            pass

    # Margins
    margins_in = 1.0
    margin_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:inch|inches|\"|-inch)\b", lower)
    if margin_match:
        try:
            margins_in = float(margin_match.group(1))
        except ValueError:
            pass

    # Line spacing
    line_spacing = 2.0
    if "single" in lower:
        line_spacing = 1.0
    elif "1.5" in lower:
        line_spacing = 1.5
    elif "double" in lower:
        line_spacing = 2.0

    # Word count
    min_words = 1500
    max_words = 3500
    word_range_match = re.search(r"(\d{3,5})\s*(?:to|-)\s*(\d{3,5})\s*words?", lower)
    if word_range_match:
        min_words = int(word_range_match.group(1))
        max_words = int(word_range_match.group(2))
    else:
        single_word_match = re.search(r"(?:min|at least|minimum)\s*(\d{3,5})\s*words?", lower)
        if single_word_match:
            min_words = int(single_word_match.group(1))
            max_words = min_words * 2

    # Citation style
    cit_style = "APA"
    if "ieee" in lower:
        cit_style = "IEEE"
    elif "mla" in lower:
        cit_style = "MLA"
    elif "harvard" in lower:
        cit_style = "Harvard"
    elif "chicago" in lower:
        cit_style = "Chicago"

    # Required sections
    candidate_sections = [
        "Abstract",
        "Introduction",
        "Methodology",
        "Results",
        "Discussion",
        "Conclusion",
        "References",
    ]
    detected_sections = []
    for sec in candidate_sections:
        if sec.lower() in lower:
            detected_sections.append(sec)
    if not detected_sections:
        detected_sections = candidate_sections

    return RubricRuleSet(
        rubric_id="heuristic_parsed_rubric",
        title="Parsed Course Guideline Rubric",
        description="Extracted automatically from course guideline text.",
        formatting=FormattingRules(
            expected_font=font,
            expected_font_size_pt=size_pt,
            expected_margin_inches=margins_in,
            expected_line_spacing=line_spacing,
            min_word_count=min_words,
            max_word_count=max_words,
        ),
        structure=StructureRules(
            required_sections=detected_sections,
            enforce_order=True,
        ),
        citations=CitationRules(
            citation_style=cit_style,
            require_reference_list=True,
        ),
        metadata=MetadataRules(
            require_student_name=True,
            require_student_id=True,
            require_course_code=True,
            require_date=True,
        ),
        content_quality=ContentQualityRules(),
    )

def parse_rubric_from_text(text: str) -> RubricRuleSet:
    """Master rubric conversion function trying Gemini first, falling back to heuristics."""
    if GEMINI_API_KEY:
        try:
            parsed = parse_guidelines_with_gemini(text)
            if parsed:
                return parsed
        except Exception:
            pass

    if OPENAI_API_KEY:
        try:
            parsed = parse_guidelines_with_openai(text)
            if parsed:
                return parsed
        except Exception:
            pass

    return parse_guidelines_heuristically(text)
