# Implementation Plan: Assignment/Report Compliance Checker

## 1. Executive Summary & Purpose
The **Assignment/Report Compliance Checker** is an automated auditing engine designed to save students and academic researchers from losing critical grades due to technical, formatting, structural, and citation compliance violations. The system compares student submissions (PDF or DOCX) against course submission rubrics (JSON or natural-language guideline documents) using rigorous programmatic inspection (PyMuPDF, pdfplumber, python-docx), cross-referencing algorithms, and LLM-powered content quality checks.

---

## 2. System Architecture & Components

```
+-----------------------------------------------------------------------------------+
|                                Streamlit Frontend                                 |
|  [Rubric Studio & Selection] | [Document Uploader] | [Interactive Compliance Dash]|
+----------------------------------------+------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                              Document Extraction Layer                            |
|  +------------------------+  +------------------------+  +----------------------+ |
|  |   pdf_extractor.py     |  |   docx_extractor.py    |  | vision_extractor.py  | |
|  | (PyMuPDF & pdfplumber) |  |     (python-docx)      |  |  (OCR / Vision LLM)  | |
|  +------------------------+  +------------------------+  +----------------------+ |
|  - Font family & size     |  - Paragraphs & Headings  |  - Scanned text OCR     | |
|  - Margins & Page Size    |  - Margins & Spacing      |  - Layout geometry      | |
|  - Line spacing & BBoxes  |  - Run-level font styles  |                         | |
+----------------------------------------+------------------------------------------+
                                         | ExtractedDocument
                                         v
+-----------------------------------------------------------------------------------+
|                                Rule Engine & Schemas                              |
|  - RubricRuleSet (Pydantic Schema): Formatting, Structure, Citations, Quality, Meta|
|  - Rubric Parser: Converts free-text/PDF prompts -> JSON rule schema              |
|  - Pre-configured Templates: APA 7th, IEEE Conference, Harvard Style, College Std|
+----------------------------------------+------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                               Validation Engine                                   |
|  +------------------+ +------------------+ +------------------+ +---------------+ |
|  | formatting.py    | | structure.py     | | citations.py     | | metadata.py   | |
|  | - Font & sizes   | | - Required secs  | | - APA/MLA/IEEE   | | - Student name| |
|  | - Margin bounds  | | - Section order  | | - In-text <-> Ref| | - Roll/ID     | |
|  | - Line spacing   | | - Heading levels | | - Dangling refs  | | - Course code | |
|  | - Word/Page count| | - Fuzzy matching | | - Style match    | | - Date format | |
|  +------------------+ +------------------+ +------------------+ +---------------+ |
|  +------------------------------------------------------------------------------+ |
|  | content_quality.py: Vague phrases, run-on sentences, repetition, LLM review  | |
+----------------------------------------+------------------------------------------+
                                         | ComplianceReport
                                         v
+-----------------------------------------------------------------------------------+
|                             Reporting & Persistence                               |
|  - SQLite Database (`compliance_history.db`): Past audits, scores, detailed logs  |
|  - PDF Report Generator (`reportlab`): Professional downloadable audit summary    |
|  - JSON Exporter: Machine-readable audit output                                   |
+-----------------------------------------------------------------------------------+
```

---

## 3. Directory Layout

```
student/
|-- IMPLEMENTATION_PLAN.md
|-- README.md
|-- requirements.txt
|-- .env.example
|-- app.py
+-- docs/
|   |-- ARCHITECTURE.md
|   |-- RULE_SCHEMA.md
|   |-- PORTFOLIO_WRITEUP.md
|   +-- USER_GUIDE.md
+-- rubrics/
|   |-- college_standard_apa.json
|   |-- ieee_conference.json
|   |-- harvard_academic.json
|   +-- sample_rubric_guidelines.txt
+-- samples/
|   |-- generate_sample_docs.py
+-- src/
|   |-- __init__.py
|   |-- config.py
|   |-- database.py
|   +-- extractor/
|   |   |-- __init__.py
|   |   |-- base.py
|   |   |-- pdf_extractor.py
|   |   |-- docx_extractor.py
|   |   +-- vision_extractor.py
|   +-- rules/
|   |   |-- __init__.py
|   |   |-- schema.py
|   |   |-- rubric_parser.py
|   |   +-- default_rubrics.py
|   +-- validator/
|   |   |-- __init__.py
|   |   |-- base.py
|   |   |-- engine.py
|   |   |-- formatting.py
|   |   |-- structure.py
|   |   |-- citations.py
|   |   |-- metadata.py
|   |   +-- content_quality.py
|   +-- reporting/
|   |   |-- __init__.py
|   |   |-- pdf_report.py
|   |   +-- json_exporter.py
|   +-- ui/
|       |-- __init__.py
|       +-- components.py
+-- tests/
    |-- test_extractors.py
    |-- test_validators.py
    +-- test_database.py
```

---

## 4. Key Functional Requirements

1. **Extraction Capabilities**:
   - Native PDF extraction via `pdfplumber` and `fitz` (PyMuPDF): computes real margins (top, bottom, left, right in inches), dominant body font, font sizes across all spans, line spacing approximations, page dimensions, text per page, and structural headings.
   - DOCX extraction via `python-docx`: parses section geometry (page width, height, margins in inches), paragraph styles, run-level fonts, bold/italic, header/footer elements.
   - OCR fallback: gracefully detects scanned pages with low text density, offering vision extraction.

2. **Compliance Rules Engine**:
   - `FormattingSpecs`: Font family, font size, margins, line spacing, page count range, word count range, page size (A4 / Letter).
   - `StructuralRequirements`: Ordered mandatory sections (e.g. Abstract -> Introduction -> Methodology -> Results/Discussion -> Conclusion -> References), detects missing or out-of-order sections using fuzzy synonym matching.
   - `CitationChecks`: Identifies in-text citations (APA `(Smith, 2020)`, MLA `(Smith 45)`, IEEE `[1]`), extracts References/Bibliography entries, and validates bi-directional linkage (flags in-text citations missing from references and references never cited).
   - `ContentQuality`: Vague sentence detection, run-on sentences, repetitive vocabulary / lexical richness, passive voice ratio, plus optional LLM content review when API key is supplied.
   - `SubmissionMetadata`: Verifies presence of Student Name, Student ID / Roll Number, Course Code, and Date on the cover page or header.

3. **Report Generation & Persistence**:
   - Weighted overall compliance score (0 - 100%) and Letter Grade (A+, A, B, C, F).
   - Categorized issues: `Critical` (immediate mark loss), `Warning` (formatting inconsistency), `Info` (polish & style).
   - Export to formatted PDF audit certificate using `reportlab`.
   - SQLite persistence tracking timestamp, file name, rubric, pass/fail counts, and full JSON payload.

4. **Testing & Demonstration**:
   - Automated synthetic document generator (`samples/generate_sample_docs.py`) creating both a conforming and a non-conforming PDF and DOCX for instant testing without manual file creation.
   - Pytest unit tests for all validators, extractors, and database functions.
