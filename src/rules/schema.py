"""Pydantic schemas defining the rubric rules."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class FormattingRules(BaseModel):
    """Formatting specifications for assignment submissions."""
    expected_font: str = Field(default="Times New Roman", description="Expected body font family")
    allowed_fonts: List[str] = Field(default_factory=lambda: ["Times New Roman", "Calibri", "Arial"])
    expected_font_size_pt: float = Field(default=12.0, description="Expected body font size in points")
    font_size_tolerance_pt: float = Field(default=0.75, description="Permissible deviation in points")
    expected_margin_inches: float = Field(default=1.0, description="Expected 4-side margin in inches")
    margin_tolerance_inches: float = Field(default=0.15, description="Margin deviation tolerance in inches")
    expected_line_spacing: float = Field(default=2.0, description="1.0 single, 1.5 one-and-a-half, 2.0 double")
    expected_page_size: str = Field(default="Letter", description="Letter, A4, or Any")
    min_word_count: Optional[int] = Field(default=1000, description="Minimum acceptable word count")
    max_word_count: Optional[int] = Field(default=4000, description="Maximum acceptable word count")
    min_page_count: Optional[int] = Field(default=3, description="Minimum page count")
    max_page_count: Optional[int] = Field(default=12, description="Maximum page count")

class StructureRules(BaseModel):
    """Structural section requirements."""
    required_sections: List[str] = Field(
        default_factory=lambda: [
            "Abstract",
            "Introduction",
            "Methodology",
            "Results",
            "Discussion",
            "Conclusion",
            "References",
        ]
    )
    enforce_order: bool = Field(default=True, description="Enforce strict sequential ordering of sections")
    min_words_per_section: Dict[str, int] = Field(
        default_factory=lambda: {
            "Abstract": 100,
            "Introduction": 150,
            "Conclusion": 100,
        }
    )

class CitationRules(BaseModel):
    """Citation and referencing rules."""
    citation_style: str = Field(default="APA", description="APA, MLA, IEEE, Harvard, or None")
    require_reference_list: bool = Field(default=True, description="Require a terminal references section")
    min_references_count: int = Field(default=3, description="Minimum count of references in bibliography")
    cross_reference_in_text: bool = Field(default=True, description="Cross-reference in-text citations against bibliography")

class MetadataRules(BaseModel):
    """Cover page and header submission metadata rules."""
    require_student_name: bool = Field(default=True)
    require_student_id: bool = Field(default=True)
    require_course_code: bool = Field(default=True)
    course_code_pattern: str = Field(default=r"[A-Z]{2,4}\s*[-_]?\s*\d{3,4}")
    require_date: bool = Field(default=True)
    header_or_cover_only: bool = Field(default=True)

class ContentQualityRules(BaseModel):
    """Content quality and clarity checks."""
    max_sentence_length_words: int = Field(default=35, description="Maximum sentence word length before run-on warning")
    forbidden_vague_words: List[str] = Field(
        default_factory=lambda: [
            "things",
            "stuff",
            "very good",
            "obviously",
            "a lot of",
            "basically",
            "bad",
        ]
    )
    min_lexical_diversity: float = Field(default=0.35, description="Minimum type-token ratio")
    enable_llm_quality_review: bool = Field(default=False, description="Invoke LLM for subjective writing review")

class RubricRuleSet(BaseModel):
    """Complete rubric rule configuration."""
    rubric_id: str = Field(default="custom_rubric_v1")
    title: str = Field(default="Custom Course Rubric")
    description: str = Field(default="Academic submission compliance criteria.")
    formatting: FormattingRules = Field(default_factory=FormattingRules)
    structure: StructureRules = Field(default_factory=StructureRules)
    citations: CitationRules = Field(default_factory=CitationRules)
    metadata: MetadataRules = Field(default_factory=MetadataRules)
    content_quality: ContentQualityRules = Field(default_factory=ContentQualityRules)
