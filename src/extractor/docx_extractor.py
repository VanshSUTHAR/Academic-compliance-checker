"""DOCX extractor using python-docx to inspect styles, margins, and structure."""

import os
import re
from collections import Counter
from io import BytesIO
from typing import Dict, List, Optional, Tuple, Union
import docx
from docx.shared import Inches, Pt

from src.extractor.base import ExtractedDocument, PageMetadata, SectionBlock
from src.extractor.pdf_extractor import SECTION_CANDIDATE_PATTERNS, classify_page_size

def extract_docx_document(
    file_source: Union[str, bytes, BytesIO],
    filename: str = "document.docx",
) -> ExtractedDocument:
    """Extract formatting, structure, and text from a Word DOCX document."""
    if isinstance(file_source, (bytes, bytearray)):
        doc = docx.Document(BytesIO(file_source))
    elif isinstance(file_source, BytesIO):
        doc = docx.Document(file_source)
    else:
        doc = docx.Document(file_source)

    # 1. Inspect Sections for Margins and Page Geometry
    top_margins = []
    bottom_margins = []
    left_margins = []
    right_margins = []
    widths = []
    heights = []
    headers_footers = []

    for section in doc.sections:
        try:
            top_margins.append(section.top_margin.inches)
            bottom_margins.append(section.bottom_margin.inches)
            left_margins.append(section.left_margin.inches)
            right_margins.append(section.right_margin.inches)
            widths.append(section.page_width.inches)
            heights.append(section.page_height.inches)
            
            # Header text
            if section.header:
                h_text = " ".join(p.text.strip() for p in section.header.paragraphs if p.text.strip())
                if h_text:
                    headers_footers.append(h_text)
        except Exception:
            pass

    avg_top = round(sum(top_margins) / len(top_margins), 2) if top_margins else 1.0
    avg_bottom = round(sum(bottom_margins) / len(bottom_margins), 2) if bottom_margins else 1.0
    avg_left = round(sum(left_margins) / len(left_margins), 2) if left_margins else 1.0
    avg_right = round(sum(right_margins) / len(right_margins), 2) if right_margins else 1.0
    avg_margins = {"top": avg_top, "bottom": avg_bottom, "left": avg_left, "right": avg_right}

    page_width = widths[0] if widths else 8.5
    page_height = heights[0] if heights else 11.0
    page_size_label = classify_page_size(page_width, page_height)

    # 2. Iterate paragraphs for fonts, line spacing, and sections
    all_fonts_counter: Counter = Counter()
    all_font_sizes: List[float] = []
    line_spacings: List[float] = []
    sections: List[SectionBlock] = []
    full_text_paragraphs: List[str] = []

    # Get default Normal style font
    default_font = "Times New Roman"
    default_size = 12.0
    try:
        normal_font = doc.styles["Normal"].font
        if normal_font.name:
            default_font = normal_font.name
        if normal_font.size:
            default_size = normal_font.size.pt
    except Exception:
        pass

    current_section: Optional[SectionBlock] = None
    section_texts: Dict[str, List[str]] = {}

    for p in doc.paragraphs:
        p_text = p.text.strip()
        if not p_text:
            continue
        full_text_paragraphs.append(p_text)

        # Check line spacing
        if p.paragraph_format.line_spacing is not None:
            try:
                line_spacings.append(float(p.paragraph_format.line_spacing))
            except Exception:
                pass

        # Inspect runs for fonts and font sizes
        p_font = default_font
        p_size = default_size
        for run in p.runs:
            if run.font.name:
                p_font = run.font.name
            if run.font.size:
                try:
                    p_size = round(run.font.size.pt, 1)
                except Exception:
                    pass
            if run.text.strip():
                all_fonts_counter[p_font] += len(run.text.strip())
                all_font_sizes.append(p_size)

        # Check if paragraph is a heading style or matches candidate section
        is_heading_style = p.style.name and "Heading" in p.style.name
        matched_section_name = None

        p_lower = p_text.lower()
        for pat in SECTION_CANDIDATE_PATTERNS:
            if re.match(pat, p_lower) and len(p_text) < 60:
                matched_section_name = re.sub(r"^(?:[0-9]+(?:\.[0-9]+)*|[IVXLCDM]+)[\.\:\-]?\s+", "", p_text, flags=re.IGNORECASE).strip()
                break

        if is_heading_style or matched_section_name:
            heading_title = matched_section_name or p_text
            if current_section:
                current_section.content = "\n".join(section_texts.get(current_section.heading, []))
                current_section.word_count = len(current_section.content.split())
            
            new_sec = SectionBlock(
                heading=heading_title,
                normalized_heading=heading_title.title(),
                page_number=1, # Estimated
            )
            sections.append(new_sec)
            current_section = new_sec
            section_texts[heading_title] = []
        else:
            if current_section:
                section_texts.setdefault(current_section.heading, []).append(p_text)

    if current_section and current_section.heading in section_texts:
        current_section.content = "\n".join(section_texts[current_section.heading])
        current_section.word_count = len(current_section.content.split())

    full_text = "\n\n".join(full_text_paragraphs)
    total_words = len(full_text.split())

    # Dominant font and size
    dominant_font = all_fonts_counter.most_common(1)[0][0] if all_fonts_counter else default_font
    dominant_font_size = Counter(all_font_sizes).most_common(1)[0][0] if all_font_sizes else default_size

    # Line spacing
    detected_line_spacing = 2.0
    if line_spacings:
        med_spacing = sum(line_spacings) / len(line_spacings)
        if med_spacing <= 1.2:
            detected_line_spacing = 1.0
        elif med_spacing <= 1.7:
            detected_line_spacing = 1.5
        else:
            detected_line_spacing = 2.0

    # Approximate page count (approx 350 words per page if double-spaced)
    estimated_page_count = max(1, round(total_words / 320))

    # First page text snippet (first 300 words)
    first_page_words = full_text.split()[:300]
    first_page_text = " ".join(first_page_words)

    return ExtractedDocument(
        filename=filename,
        file_type="docx",
        page_count=estimated_page_count,
        total_word_count=total_words,
        dominant_font=dominant_font,
        dominant_font_size_pt=dominant_font_size,
        font_distribution=dict(all_fonts_counter),
        font_sizes=all_font_sizes,
        avg_margins=avg_margins,
        detected_line_spacing=detected_line_spacing,
        page_size_label=page_size_label,
        full_text=full_text,
        first_page_text=first_page_text,
        sections=sections,
        headers_and_footers=headers_footers,
        is_scanned=False,
    )
