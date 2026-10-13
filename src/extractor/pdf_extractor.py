"""Deep PDF extractor using PyMuPDF (fitz) and pdfplumber."""

import os
import re
from collections import Counter
from io import BytesIO
from typing import Dict, List, Optional, Tuple, Union
import pymupdf as fitz
import pdfplumber

from src.extractor.base import ExtractedDocument, PageMetadata, SectionBlock

KNOWN_FONT_FAMILIES = {
    "times": "Times New Roman",
    "arial": "Arial",
    "calibri": "Calibri",
    "georgia": "Georgia",
    "helvetica": "Helvetica",
    "courier": "Courier New",
    "cambria": "Cambria",
    "garamond": "Garamond",
    "palatino": "Palatino",
}

SECTION_CANDIDATE_PATTERNS = [
    r"^(?:[0-9IVX]+\.?\s+)?abstract\b",
    r"^(?:[0-9IVX]+\.?\s+)?introduction\b",
    r"^(?:[0-9IVX]+\.?\s+)?background\b",
    r"^(?:[0-9IVX]+\.?\s+)?literature review\b",
    r"^(?:[0-9IVX]+\.?\s+)?related work\b",
    r"^(?:[0-9IVX]+\.?\s+)?methodology\b",
    r"^(?:[0-9IVX]+\.?\s+)?materials?\s*(?:&|and)\s*methods\b",
    r"^(?:[0-9IVX]+\.?\s+)?methods\b",
    r"^(?:[0-9IVX]+\.?\s+)?experimental results\b",
    r"^(?:[0-9IVX]+\.?\s+)?results\b",
    r"^(?:[0-9IVX]+\.?\s+)?discussion\b",
    r"^(?:[0-9IVX]+\.?\s+)?analysis\b",
    r"^(?:[0-9IVX]+\.?\s+)?recommendations\b",
    r"^(?:[0-9IVX]+\.?\s+)?conclusion\b",
    r"^(?:[0-9IVX]+\.?\s+)?future work\b",
    r"^(?:[0-9IVX]+\.?\s+)?references\b",
    r"^(?:[0-9IVX]+\.?\s+)?bibliography\b",
    r"^(?:[0-9IVX]+\.?\s+)?works cited\b",
]

def normalize_font_name(raw_name: str) -> str:
    """Normalize raw font names like 'BCDEEE+TimesNewRomanPSMT' to 'Times New Roman'."""
    clean = re.sub(r"^[A-Z]{6}\+", "", raw_name)
    clean_lower = clean.lower()
    for key, normalized in KNOWN_FONT_FAMILIES.items():
        if key in clean_lower:
            return normalized
    # Fallback cleanup
    clean = re.sub(r"-(?:Regular|Bold|Italic|BoldItalic|MT|PSMT)$", "", clean, flags=re.IGNORECASE)
    return clean.strip() or "Standard Font"

def classify_page_size(width_in: float, height_in: float) -> str:
    """Classify page dimensions into standard formats (Letter, A4, or Custom)."""
    # Standard dimensions
    # Letter: 8.5 x 11.0 in
    # A4: 8.27 x 11.69 in
    w, h = min(width_in, height_in), max(width_in, height_in)
    if abs(w - 8.5) < 0.35 and abs(h - 11.0) < 0.35:
        return "Letter"
    if abs(w - 8.27) < 0.35 and abs(h - 11.69) < 0.35:
        return "A4"
    return "Custom"

def extract_pdf_document(
    file_source: Union[str, bytes, BytesIO],
    filename: str = "document.pdf",
) -> ExtractedDocument:
    """Extract full structural, formatting, and text data from a PDF file."""
    if isinstance(file_source, (bytes, bytearray)):
        doc_fitz = fitz.open(stream=file_source, filetype="pdf")
        pdf_plumber_file = BytesIO(file_source)
    elif isinstance(file_source, BytesIO):
        file_bytes = file_source.getvalue()
        doc_fitz = fitz.open(stream=file_bytes, filetype="pdf")
        pdf_plumber_file = BytesIO(file_bytes)
    else:
        doc_fitz = fitz.open(file_source)
        pdf_plumber_file = file_source

    total_pages = len(doc_fitz)
    pages_meta: List[PageMetadata] = []
    all_fonts_counter: Counter = Counter()
    all_font_sizes: List[float] = []
    full_text_list: List[str] = []
    sections: List[SectionBlock] = []
    line_spacing_estimates: List[float] = []
    warnings: List[str] = []

    # Process page by page with PyMuPDF
    for page_idx in range(total_pages):
        page = doc_fitz[page_idx]
        rect = page.rect
        width_in = rect.width / 72.0
        height_in = rect.height / 72.0

        # Extract text blocks and spans
        text_page = page.get_text("dict")
        page_text_blocks: List[str] = []
        page_fonts: List[str] = []
        spans_on_page = []

        for block in text_page.get("blocks", []):
            if block.get("type") == 0:  # text block
                for line in block.get("lines", []):
                    line_text = ""
                    y_bottom = line.get("bbox", [0, 0, 0, 0])[3]
                    y_top = line.get("bbox", [0, 0, 0, 0])[1]
                    for span in line.get("spans", []):
                        text = span.get("text", "")
                        line_text += text
                        font_name = normalize_font_name(span.get("font", ""))
                        size = round(float(span.get("size", 12.0)), 1)
                        if text.strip():
                            all_fonts_counter[font_name] += len(text)
                            all_font_sizes.append(size)
                            page_fonts.append(font_name)
                            spans_on_page.append({
                                "text": text,
                                "size": size,
                                "font": font_name,
                                "flags": span.get("flags", 0),
                                "bbox": span.get("bbox", [0, 0, 0, 0]),
                            })
                    if line_text.strip():
                        page_text_blocks.append(line_text)

        page_text = "\n".join(page_text_blocks)
        full_text_list.append(page_text)
        words = page_text.split()
        word_count = len(words)
        char_count = len(page_text)

        # Estimate margins via text words bounding box
        words_fitz = page.get_text("words")  # [x0, y0, x1, y1, word, block_no, line_no, word_no]
        if words_fitz:
            min_x0 = min(w[0] for w in words_fitz)
            min_y0 = min(w[1] for w in words_fitz)
            max_x1 = max(w[2] for w in words_fitz)
            max_y1 = max(w[3] for w in words_fitz)

            margin_top = max(0.2, min_y0 / 72.0)
            margin_bottom = max(0.2, (rect.height - max_y1) / 72.0)
            margin_left = max(0.2, min_x0 / 72.0)
            margin_right = max(0.2, (rect.width - max_x1) / 72.0)
        else:
            margin_top = 1.0
            margin_bottom = 1.0
            margin_left = 1.0
            margin_right = 1.0

        # Estimate line spacing across consecutive lines on the page
        page_line_spacings = []
        for block in text_page.get("blocks", []):
            if block.get("type") == 0 and len(block.get("lines", [])) >= 3:
                lines = block.get("lines", [])
                for i in range(len(lines) - 1):
                    y_curr = lines[i]["bbox"][1]
                    y_next = lines[i + 1]["bbox"][1]
                    delta_y = y_next - y_curr
                    if delta_y > 4 and lines[i]["spans"]:
                        span_size = lines[i]["spans"][0].get("size", 12.0)
                        if span_size > 0:
                            ratio = delta_y / span_size
                            # typical: 1.0 to 1.3 -> single, 1.4 to 1.7 -> 1.5x, 1.8 to 2.4 -> double
                            page_line_spacings.append(ratio)
        if page_line_spacings:
            avg_spacing = sum(page_line_spacings) / len(page_line_spacings)
            line_spacing_estimates.append(avg_spacing)

        page_meta = PageMetadata(
            page_number=page_idx + 1,
            width_inches=round(width_in, 2),
            height_inches=round(height_in, 2),
            margin_top_inches=round(margin_top, 2),
            margin_bottom_inches=round(margin_bottom, 2),
            margin_left_inches=round(margin_left, 2),
            margin_right_inches=round(margin_right, 2),
            word_count=word_count,
            char_count=char_count,
            text=page_text,
            fonts_detected=list(set(page_fonts)),
            line_spacings=page_line_spacings,
        )
        pages_meta.append(page_meta)

    # Detect structural sections across text lines
    current_section: Optional[SectionBlock] = None
    section_texts: Dict[str, List[str]] = {}

    for page_idx, page_m in enumerate(pages_meta):
        lines = [ln.strip() for ln in page_m.text.split("\n") if ln.strip()]
        for line in lines:
            line_lower = line.lower()
            # Check if this line is a section heading
            matched = False
            for pat in SECTION_CANDIDATE_PATTERNS:
                if re.match(pat, line_lower) and len(line) < 60:
                    matched = True
                    # Clean section heading name (strip leading numbers like 1., I., 2.1)
                    cleaned_heading = re.sub(r"^(?:[0-9]+(?:\.[0-9]+)*|[IVXLCDM]+)[\.\:\-]?\s+", "", line, flags=re.IGNORECASE).strip()
                    if current_section:
                        current_section.content = "\n".join(section_texts.get(current_section.heading, []))
                        current_section.word_count = len(current_section.content.split())
                    
                    new_sec = SectionBlock(
                        heading=cleaned_heading,
                        normalized_heading=cleaned_heading.title(),
                        page_number=page_idx + 1,
                    )
                    sections.append(new_sec)
                    current_section = new_sec
                    section_texts[cleaned_heading] = []
                    break
            if not matched and current_section:
                section_texts.setdefault(current_section.heading, []).append(line)

    if current_section and current_section.heading in section_texts:
        current_section.content = "\n".join(section_texts[current_section.heading])
        current_section.word_count = len(current_section.content.split())

    # Calculate overall document aggregates
    full_text = "\n\n".join(full_text_list)
    total_words = sum(p.word_count for p in pages_meta)

    dominant_font = all_fonts_counter.most_common(1)[0][0] if all_fonts_counter else "Times New Roman"
    dominant_font_size = 12.0
    if all_font_sizes:
        size_counts = Counter(all_font_sizes)
        dominant_font_size = size_counts.most_common(1)[0][0]

    # Calculate average margins across non-cover pages (page 2+ if available)
    eval_pages = pages_meta[1:] if len(pages_meta) > 1 else pages_meta
    if eval_pages:
        avg_margins = {
            "top": round(sum(p.margin_top_inches for p in eval_pages) / len(eval_pages), 2),
            "bottom": round(sum(p.margin_bottom_inches for p in eval_pages) / len(eval_pages), 2),
            "left": round(sum(p.margin_left_inches for p in eval_pages) / len(eval_pages), 2),
            "right": round(sum(p.margin_right_inches for p in eval_pages) / len(eval_pages), 2),
        }
    else:
        avg_margins = {"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0}

    # Normalized line spacing classification
    detected_line_spacing = 2.0
    if line_spacing_estimates:
        median_ratio = sum(line_spacing_estimates) / len(line_spacing_estimates)
        if median_ratio < 1.35:
            detected_line_spacing = 1.0
        elif median_ratio < 1.75:
            detected_line_spacing = 1.5
        else:
            detected_line_spacing = 2.0

    page_size_label = "Letter"
    if pages_meta:
        page_size_label = classify_page_size(pages_meta[0].width_inches, pages_meta[0].height_inches)

    first_page_text = pages_meta[0].text if pages_meta else ""
    is_scanned = total_words < 40 and total_pages > 0
    if is_scanned:
        warnings.append("Document appears to be scanned or contains very sparse text layers. Consider running OCR.")

    doc_fitz.close()

    return ExtractedDocument(
        filename=filename,
        file_type="pdf",
        page_count=total_pages,
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
        pages=pages_meta,
        sections=sections,
        is_scanned=is_scanned,
        extraction_warnings=warnings,
    )
