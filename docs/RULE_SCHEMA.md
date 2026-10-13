# Rubric Rule Schema Specification

## 1. Overview
The **Compliance Rule Set** defines the precise contractual expectations against which a student report or academic assignment is evaluated. The schema is serialized in standard JSON and validated in Python via `pydantic`.

---

## 2. JSON Schema Definition

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RubricRuleSet",
  "type": "object",
  "required": ["rubric_id", "title", "formatting", "structure", "citations", "metadata"],
  "properties": {
    "rubric_id": {
      "type": "string",
      "description": "Unique identifier for this rubric (e.g. 'apa_college_std_v1')"
    },
    "title": {
      "type": "string",
      "description": "Human-readable rubric name"
    },
    "description": {
      "type": "string",
      "description": "Brief explanation of the course or target journal/conference requirements"
    },
    "formatting": {
      "type": "object",
      "required": ["expected_font", "expected_font_size_pt"],
      "properties": {
        "expected_font": {
          "type": "string",
          "description": "Target font family (e.g. 'Times New Roman', 'Arial', 'Calibri')"
        },
        "allowed_fonts": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Optional list of permissible alternate fonts"
        },
        "expected_font_size_pt": {
          "type": "number",
          "description": "Expected body font size in points (e.g. 12.0)"
        },
        "font_size_tolerance_pt": {
          "type": "number",
          "default": 0.5,
          "description": "Permissible deviation in points (default: 0.5pt)"
        },
        "expected_margin_inches": {
          "type": "number",
          "default": 1.0,
          "description": "Expected margin in inches on all 4 borders (e.g. 1.0 inch)"
        },
        "margin_tolerance_inches": {
          "type": "number",
          "default": 0.15,
          "description": "Permissible margin deviation (e.g. +/- 0.15 in)"
        },
        "expected_line_spacing": {
          "type": "number",
          "default": 2.0,
          "description": "Expected line spacing (e.g. 1.0 for single, 1.5 for 1.5x, 2.0 for double)"
        },
        "expected_page_size": {
          "type": "string",
          "enum": ["Letter", "A4", "Any"],
          "default": "Letter"
        },
        "min_word_count": {
          "type": "integer",
          "description": "Minimum acceptable total word count"
        },
        "max_word_count": {
          "type": "integer",
          "description": "Maximum acceptable total word count"
        },
        "min_page_count": {
          "type": "integer",
          "description": "Minimum page count"
        },
        "max_page_count": {
          "type": "integer",
          "description": "Maximum page count"
        }
      }
    },
    "structure": {
      "type": "object",
      "required": ["required_sections"],
      "properties": {
        "required_sections": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Mandatory sections that must appear in the assignment"
        },
        "enforce_order": {
          "type": "boolean",
          "default": true,
          "description": "Whether the sections must appear in the strictly defined sequence"
        },
        "min_words_per_section": {
          "type": "object",
          "additionalProperties": { "type": "integer" },
          "description": "Optional minimum word count for specific sections (e.g. {'Abstract': 150})"
        }
      }
    },
    "citations": {
      "type": "object",
      "required": ["citation_style"],
      "properties": {
        "citation_style": {
          "type": "string",
          "enum": ["APA", "MLA", "IEEE", "Harvard", "Chicago", "None"],
          "description": "Citation style expected throughout the paper"
        },
        "require_reference_list": {
          "type": "boolean",
          "default": true,
          "description": "Whether a terminal References / Bibliography section is required"
        },
        "min_references_count": {
          "type": "integer",
          "default": 3,
          "description": "Minimum number of references expected in the bibliography"
        },
        "cross_reference_in_text": {
          "type": "boolean",
          "default": true,
          "description": "Check that all in-text citations appear in the reference list and vice-versa"
        }
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "require_student_name": { "type": "boolean", "default": true },
        "require_student_id": { "type": "boolean", "default": true },
        "require_course_code": { "type": "boolean", "default": true },
        "course_code_pattern": {
          "type": "string",
          "default": "[A-Z]{2,4}\\s*[-_]?\\s*\\d{3,4}",
          "description": "Regex pattern used to validate course code (e.g. CS-101, BIO202)"
        },
        "require_date": { "type": "boolean", "default": true },
        "header_or_cover_only": {
          "type": "boolean",
          "default": true,
          "description": "Restricts search for metadata to the first page and headers"
        }
      }
    },
    "content_quality": {
      "type": "object",
      "properties": {
        "max_sentence_length_words": {
          "type": "integer",
          "default": 35,
          "description": "Sentences longer than this count will trigger a run-on sentence flag"
        },
        "forbidden_vague_words": {
          "type": "array",
          "items": { "type": "string" },
          "default": ["things", "stuff", "very good", "bad", "obviously", "a lot of", "basically"],
          "description": "Words or colloquial phrases that weaken academic rigor"
        },
        "min_lexical_diversity": {
          "type": "number",
          "default": 0.35,
          "description": "Minimum Type-Token Ratio (unique words / total words)"
        },
        "enable_llm_quality_review": {
          "type": "boolean",
          "default": false,
          "description": "Whether to query LLM for qualitative tone and argument flow"
        }
      }
    }
  }
}
```

---

## 3. Example Rule Configuration (`rubrics/college_standard_apa.json`)

```json
{
  "rubric_id": "apa_college_std_v1",
  "title": "College Standard APA 7th Edition Paper",
  "description": "Standard university term paper following APA 7th edition student paper format.",
  "formatting": {
    "expected_font": "Times New Roman",
    "allowed_fonts": ["Times New Roman", "Calibri", "Arial", "Georgia"],
    "expected_font_size_pt": 12.0,
    "font_size_tolerance_pt": 0.5,
    "expected_margin_inches": 1.0,
    "margin_tolerance_inches": 0.15,
    "expected_line_spacing": 2.0,
    "expected_page_size": "Letter",
    "min_word_count": 1500,
    "max_word_count": 3500,
    "min_page_count": 4,
    "max_page_count": 12
  },
  "structure": {
    "required_sections": [
      "Title",
      "Abstract",
      "Introduction",
      "Methodology",
      "Results",
      "Discussion",
      "Conclusion",
      "References"
    ],
    "enforce_order": true,
    "min_words_per_section": {
      "Abstract": 100,
      "Introduction": 200,
      "Conclusion": 150
    }
  },
  "citations": {
    "citation_style": "APA",
    "require_reference_list": true,
    "min_references_count": 4,
    "cross_reference_in_text": true
  },
  "metadata": {
    "require_student_name": true,
    "require_student_id": true,
    "require_course_code": true,
    "course_code_pattern": "[A-Z]{2,4}\\s*[-_]?\\s*\\d{3,4}",
    "require_date": true,
    "header_or_cover_only": true
  },
  "content_quality": {
    "max_sentence_length_words": 35,
    "forbidden_vague_words": ["stuff", "things", "very good", "obviously", "a lot of", "basically"],
    "min_lexical_diversity": 0.35,
    "enable_llm_quality_review": false
  }
}
```
