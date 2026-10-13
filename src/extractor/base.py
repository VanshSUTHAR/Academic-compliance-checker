"""Base data structures and classes for document extraction."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class FontUsage:
    """Represents a distinct font specification found in the document."""
    font_name: str
    size_pt: float
    frequency: int
    is_bold: bool = False
    is_italic: bool = False

@dataclass
class PageMetadata:
    """Detailed structural and geometric information for an individual page."""
    page_number: int
    width_inches: float
    height_inches: float
    margin_top_inches: float
    margin_bottom_inches: float
    margin_left_inches: float
    margin_right_inches: float
    word_count: int
    char_count: int
    text: str
    fonts_detected: List[str] = field(default_factory=list)
    line_spacings: List[float] = field(default_factory=list)

@dataclass
class SectionBlock:
    """Represents an identified structural section or chapter."""
    heading: str
    normalized_heading: str
    page_number: int
    word_count: int = 0
    content: str = ""

@dataclass
class ExtractedDocument:
    """Unified document representation output by all extractors."""
    filename: str
    file_type: str  # 'pdf', 'docx', 'image'
    page_count: int
    total_word_count: int
    dominant_font: str
    dominant_font_size_pt: float
    font_distribution: Dict[str, int] = field(default_factory=dict)
    font_sizes: List[float] = field(default_factory=list)
    avg_margins: Dict[str, float] = field(
        default_factory=lambda: {
            "top": 1.0,
            "bottom": 1.0,
            "left": 1.0,
            "right": 1.0,
        }
    )
    detected_line_spacing: float = 1.5
    page_size_label: str = "Letter"  # 'Letter', 'A4', or 'Custom'
    full_text: str = ""
    first_page_text: str = ""
    pages: List[PageMetadata] = field(default_factory=list)
    sections: List[SectionBlock] = field(default_factory=list)
    headers_and_footers: List[str] = field(default_factory=list)
    is_scanned: bool = False
    extraction_warnings: List[str] = field(default_factory=list)
