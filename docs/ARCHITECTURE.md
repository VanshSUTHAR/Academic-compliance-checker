# Architecture Documentation: Assignment/Report Compliance Checker

## 1. System Overview

The **Assignment/Report Compliance Checker** is an automated auditing engine designed to eliminate grade penalties caused by formatting oversights, structural omissions, citation discrepancies, and metadata errors in academic and professional submissions.

Rather than relying purely on probabilistic LLM responses for deterministic formatting checks, this system adopts a **hybrid deterministic-AI architecture**:
- **Deterministic Geometric Engine**: Directly inspects the document binary/XML structure (PDF bounding boxes, DOCX XML paragraph styles, font dictionaries, margin dimensions in points/inches) to guarantee 100% reproducible, objective validation of margins, fonts, line spacing, page geometry, and word counts.
- **Structural & Citation Graph Validator**: Uses regular expressions and fuzzy string matching (RapidFuzz) to identify headings, cross-reference in-text citations against the reference list, and detect dangling or missing references.
- **Cognitive / Quality Layer**: Employs an LLM (OpenAI GPT-4o / Google Gemini) or deterministic stylistic NLP heuristics (for offline/local use) to assess lexical variety, vague phrasing, passive voice usage, and tone.

```
       +-------------------------------------------------------------+
       |                     User Document Input                     |
       |                   (PDF, DOCX, or Scanned)                   |
       +------------------------------+------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |               Document Extraction Subsystem                 |
       |  +---------------------+  +-------------------------------+ |
       |  |   pdfplumber & fitz |  |          python-docx          | |
       |  | (Spans, Fonts, BBox)|  | (Styles, Runs, Section Margins| |
       |  +---------------------+  +-------------------------------+ |
       +------------------------------+------------------------------+
                                      | ExtractedDocument Object
                                      v
+-----------------------------+       |
|    Rubric Rule Definition   |       |
|  (JSON Schema or Parsed)    | ----+ |
+-----------------------------+     | |
                                    v v
       +-------------------------------------------------------------+
       |                  Multi-Stage Rule Engine                    |
       |  1. Formatting Specs (Fonts, Margins, Spacing, Word Count)  |
       |  2. Structural Order & Required Sections (Fuzzy Synonyms)   |
       |  3. Citation Cross-Referencing (APA/MLA/IEEE In-text vs Ref)|
       |  4. Submission Metadata (Name, ID, Course Code, Date)       |
       |  5. Content Quality & Style (Lexical Density, Vague Words)  |
       +------------------------------+------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                Compliance Report Generation                 |
       |  - Weighted Score (0-100%) & Letter Grade (A-F)             |
       |  - Categorized Flags (Critical, Warning, Info)              |
       |  - Downloadable PDF Audit Certificate (ReportLab)           |
       |  - SQLite Persistent Audit History Record                   |
       +-------------------------------------------------------------+
```

---

## 2. Core Modules & Responsibilities

### 2.1 Extraction Subsystem (`src/extractor/`)
The extraction layer normalizes heterogeneous document formats (PDF, DOCX, Images) into a single strongly-typed dataclass: `ExtractedDocument`.

- **`pdf_extractor.py`**:
  - Uses `pdfplumber` to measure page dimensions, margins, and character-level positions.
  - Computes top, bottom, left, and right margins by taking the bounding box min/max coordinates of glyphs on body pages.
  - Uses `PyMuPDF` (`fitz`) to extract font descriptors (Font family, size in points, flags such as bold/italic) per text span.
  - Aggregates font distribution across the entire document to detect the dominant body font and identify outliers.
  - Extracts line spacing by measuring delta y-coordinates between consecutive baseline text spans.
- **`docx_extractor.py`**:
  - Leverages `python-docx` to inspect section properties (`section.top_margin`, `section.left_margin`, `section.page_width`, `section.page_height`).
  - Iterates through paragraphs and runs to capture explicit font name and size overrides, as well as inherited style properties.
  - Identifies heading styles (`Heading 1`, `Heading 2`, etc.) and bullet/numbered lists.
- **`vision_extractor.py`**:
  - Detects scanned PDFs (documents where text character density is near zero).
  - Renders page images to memory and invokes Vision LLM (OpenAI GPT-4o Vision or Google Gemini Vision) to perform OCR and layout reconstruction.
  - Includes a fallback heuristic extractor when API keys are not supplied.

### 2.2 Rule Engine & Schema (`src/rules/`)
The compliance rules are governed by strict Pydantic schemas (`RubricRuleSet`):
- **`FormattingRules`**: Expected font name, font size pt, margin inches (with tolerance), line spacing, min/max word count, min/max page count, page size (A4 / Letter).
- **`StructureRules`**: List of mandatory sections in sequence (e.g. `["Abstract", "Introduction", "Methodology", "Results", "Conclusion", "References"]`), tolerance for section order, heading capitalization.
- **`CitationRules`**: Target citation style (`APA`, `MLA`, `IEEE`, `Harvard`, `Chicago`), strict reference list check, cross-reference in-text citations against the reference entries.
- **`ContentQualityRules`**: Max sentence length, forbidden vague phrases list, passive voice threshold, lexical diversity threshold.
- **`MetadataRules`**: Require student name, student ID / roll number, course code (with optional regex pattern), submission date.

### 2.3 Validator Subsystem (`src/validator/`)
Each rule category is executed by an isolated validator module:
1. **`formatting.py`**: Evaluates numeric bounds with configurable tolerances. Calculates deviation percentages (e.g., margins found at 0.75" instead of 1.0").
2. **`structure.py`**: Uses token-based Levenshtein distance (`RapidFuzz`) against an alias dictionary (e.g., matching "Literature Review" to "Background", or "Works Cited" to "References") to ensure students are not falsely penalized for standard naming variants. Validates sequential order.
3. **`citations.py`**: Parses in-text citation markers:
   - APA: `([A-Z][a-z]+(?: & [A-Z][a-z]+)?, \d{4})`
   - MLA: `([A-Z][a-z]+ \d+)`
   - IEEE: `\[\d+\]`
   - Harvard: `([A-Z][a-z]+, \d{4})`
   Extracts entries from the bibliography and performs bidirectional cross-referencing:
   - **Type A violation**: In-text citation has no corresponding entry in references list.
   - **Type B violation**: Reference entry is listed in bibliography but never cited in body text.
4. **`metadata.py`**: Scans the cover page (Page 1) and headers for course codes (e.g. `CS-101`, `ENG300`), student IDs, student names, and dates using regex and keyword heuristics.
5. **`content_quality.py`**: Tokenizes body paragraphs into sentences, calculates average sentence length, flags run-on sentences (> 35 words), scans for vague terminology ("stuff", "things", "very good", "obviously"), and computes the Type-Token Ratio (TTR).

### 2.4 Orchestrator (`src/validator/engine.py`)
- Runs all validator modules in sequence.
- Tallies total rules evaluated, rules passed, and rules failed.
- Computes a weighted overall compliance score:
  - Formatting: 25%
  - Structure: 25%
  - Citations: 25%
  - Submission Metadata: 15%
  - Content Quality: 10%
- Maps the compliance score to an academic letter grade (A+, A, B, C, F).
- Classifies each failed check into a severity category:
  - **CRITICAL**: Guarantees mark deduction (e.g. missing Abstract, mismatched citation, word count below minimum).
  - **WARNING**: Inconsistency or slight deviation (e.g. margin at 0.9" instead of 1.0", font size 11pt instead of 12pt).
  - **INFO**: Stylistic suggestion (e.g. run-on sentence detected, vague phrasing).

### 2.5 Storage & Audit History (`src/database.py`)
- SQLite database (`compliance_history.db`) provides local persistence.
- Table `audit_logs`:
  - `id`: Auto-incrementing primary key
  - `timestamp`: UTC ISO timestamp
  - `filename`: Submission document name
  - `file_type`: PDF or DOCX
  - `rubric_name`: Name of the rubric rule set
  - `compliance_score`: Float (0-100)
  - `letter_grade`: String
  - `total_rules`: Integer
  - `passed_rules`: Integer
  - `failed_rules`: Integer
  - `critical_issues`: Integer
  - `warning_issues`: Integer
  - `info_issues`: Integer
  - `report_json`: Full serialized JSON audit payload for historical review

### 2.6 Reporting Subsystem (`src/reporting/`)
- **`pdf_report.py`**: Uses `reportlab` to compile a publication-grade PDF Compliance Certificate containing:
  - Header with audit timestamp and document checksum.
  - High-level score banner and compliance summary table.
  - Detailed findings table sorted by severity, with rule violated, current value, expected value, and suggested fix.
- **`json_exporter.py`**: Exports a machine-readable JSON representation suitable for integration with LMS platforms (Canvas, Blackboard, Moodle).

---

## 3. Data Flow Diagram

```
[User Uploads Assignment (PDF/DOCX) + Selects/Uploads Rubric]
                           |
                           v
              +--------------------------+
              | Load & Parse Rubric JSON |
              +--------------------------+
                           |
                           v
              +--------------------------+
              | Document Extractor       |
              | - Extracts Text & Layout |
              | - Measures Geometry      |
              | - Parses Font Metadata   |
              +--------------------------+
                           |
                           v
              +--------------------------+
              | Validation Engine        |
              | - Formatting Validator   |
              | - Structure Validator    |
              | - Citation Validator     |
              | - Metadata Validator     |
              | - Quality Validator      |
              +--------------------------+
                           |
                           v
              +--------------------------+
              | Compile ComplianceReport |
              | - Score & Grade Calc     |
              | - Categorized Flags      |
              +--------------------------+
                           |
             +-------------+-------------+
             |                           |
             v                           v
  [Save to SQLite DB]          [Render Streamlit UI]
                                         |
                               +---------+---------+
                               |                   |
                               v                   v
                       [Export PDF Cert]   [Export JSON]
```
