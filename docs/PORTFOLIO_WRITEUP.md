# Portfolio Project Case Study: Assignment & Report Compliance Checker

## 1. Executive Summary
- **Project Name:** Academic Compliance Engine (ACE) / Report Compliance Checker
- **Tech Stack:** Python 3.12, Streamlit, PyMuPDF (fitz), pdfplumber, python-docx, ReportLab, RapidFuzz, SQLite, OpenAI / Google Gemini Vision & LLMs
- **Domain:** EdTech, Document Engineering, Natural Language Processing, Compliance Automation

---

## 2. The Problem & Motivation
In collegiate and postgraduate programs, students routinely produce high-quality original research only to suffer severe mark deductions—often 10% to 25% of their total grade—for minor non-compliance with submission rubrics:
- Inconsistent margins (e.g. 0.75" instead of standard 1.0" APA borders).
- Font family/size mismatches across body text or copied figure captions.
- Missing mandatory rubric sections (e.g., Abstract or Methodology).
- Citation mismatches: in-text citations without matching references, or bibliography entries that were never cited.
- Missing cover page metadata (Course code, Student ID, Submission Date).

Manual proofreading is tedious, error-prone, and misses micro-formatting flaws. Standard word processors fail to audit documents against complex external rubrics.

---

## 3. The Solution: A Hybrid Deterministic & AI Compliance Engine
The **Assignment/Report Compliance Checker** solves this problem through an automated auditing pipeline:
1. **Rubric Ingestion**: Ingests university rubric guidelines as structured JSON schemas (with instant conversion from guideline PDFs/text via multi-provider LLMs or built-in templates).
2. **Deterministic Geometry Extraction**: Avoids hallucination by directly inspecting the binary/XML layers of PDFs and DOCX files. It measures bounding box coordinates, font flags, baseline deltas, and margin metrics.
3. **Multi-Category Verification Engine**:
   - **Formatting**: Font family, font size tolerance, 4-border margins, line spacing, page and word count boundaries.
   - **Structural Alignment**: Sequential heading extraction with RapidFuzz alias mapping (e.g. recognizing "Works Cited" as an alias for "References").
   - **Citation Bi-directional Cross-Referencing**: Parses in-text citation markers (APA, MLA, IEEE, Harvard) and cross-checks them against the terminal bibliography to catch missing and dangling citations.
   - **Metadata Verification**: Coversheet regex matching for Course Code (`CS-101`), Student ID, Student Name, and submission dates.
   - **Content Quality**: Flags run-on sentences, vague jargon ("stuff", "things", "obviously"), and computes lexical diversity.
4. **Audit Reporting & Analytics**:
   - Calculates a weighted compliance score (0-100%) and academic letter grade (A+ through F).
   - Generates downloadable, publication-grade PDF audit certificates via ReportLab.
   - Persists all audit records in an SQLite database with historical analytics.

---

## 4. Key Engineering Challenges & Technical Solutions

### Challenge 1: PDF Font and Margin Inspection Without Visual Hallucination
*Issue:* Passing a PDF to an LLM image model to "guess" margins or font size is fundamentally inaccurate and expensive.
*Solution:* Leveraged a hybrid extractor using `pdfplumber` and `PyMuPDF` (`fitz`).
- Extracted exact glyph bounding boxes per page to compute physical margins:
  $$\text{margin}_{\text{top}} = \min(y_0), \quad \text{margin}_{\text{left}} = \min(x_0)$$
- Inspected font descriptors across all text spans to calculate the true body font distribution and detect formatting deviations.

### Challenge 2: Fuzzy Section Heading Recognition
*Issue:* Rubrics require "Methodology", but student papers might title it "Materials & Methods" or "Methodological Framework".
*Solution:* Implemented token-based fuzzy Levenshtein matching using `RapidFuzz` mapped to an academic synonym dictionary. This ensures students aren't penalized for legitimate academic stylistic variations while still detecting missing sections.

### Challenge 3: Citation Bi-directional Graph Validation
*Issue:* Academic citation integrity requires that every in-text citation has a corresponding entry in the References list, and every bibliography entry is cited in the paper.
*Solution:* Built an algorithm that extracts regularized citation tokens (e.g., `Smith, 2020` or IEEE `[3]`), strips punctuation, and queries against the parsed bibliography entries with fuzzy string similarity to catch both orphaned in-text citations and unreferenced bibliography items.

---

## 5. System Architecture & Component Diagram

```
+-------------------------------------------------------------------------------+
|                                Streamlit Frontend                             |
|  - Real-Time Compliance Audit Dashboard                                       |
|  - Interactive Rubric Studio (Visual Rule Editor)                             |
|  - SQLite Historical Submissions Tracker                                      |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                             Extraction Pipeline                               |
|   +--------------------------+  +--------------------------+                  |
|   |   pdfplumber + PyMuPDF   |  |        python-docx       |                  |
|   | (Margins, Fonts, BBoxes) |  | (Styles, Runs, Geometry) |                  |
|   +--------------------------+  +--------------------------+                  |
+---------------------------------------+---------------------------------------+
                                        | ExtractedDocument
                                        v
+-------------------------------------------------------------------------------+
|                        Modular Verification Engine                            |
|   +-----------------------------------------------------------------------+   |
|   |  FormattingValidator | StructureValidator | CitationValidator         |   |
|   |  MetadataValidator   | ContentQualityValidator                        |   |
|   +-----------------------------------------------------------------------+   |
+---------------------------------------+---------------------------------------+
                                        | ComplianceReport
                                        v
+-------------------------------------------------------------------------------+
|                             Output & Persistence                              |
|   - ReportLab PDF Certificate Generation                                      |
|   - SQLite Audit Log Repository                                               |
|   - JSON LMS Interoperability Export                                          |
+-------------------------------------------------------------------------------+
```

---

## 6. Business & Academic Impact
- **Zero Grade Loss:** Prevents the 10-25% marks frequently forfeited due to avoidable formatting oversights.
- **Instant Turnaround:** Audits a 15-page research paper across 15+ complex checks in less than 2 seconds.
- **LMS Ready:** Designed to be extensible into automated grading pre-flight pipelines for Canvas, Blackboard, and Google Classroom.
