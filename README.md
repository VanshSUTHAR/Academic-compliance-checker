# 🎓 Assignment & Report Compliance Checker (ACE)

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/frontend-Streamlit-red.svg)](https://streamlit.io/)
[![PyMuPDF](https://img.shields.io/badge/PDF_Engine-PyMuPDF%20%2B%20pdfplumber-green.svg)](https://pymupdf.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An automated pre-flight auditing tool that verifies academic papers, student assignments, and conference submissions against course rubrics to eliminate avoidable mark deductions on formatting, structure, citations, and metadata.

---

## 🌟 The Story & Motivation
Students routinely lose **10% to 25% of their total grade** on technical formatting and submission rules—such as incorrect margins, non-compliant font sizes, missing sections, mismatched citations, or missing cover page metadata—even when their core content and research are exemplary.

The **Assignment/Report Compliance Checker** solves this by providing a reliable pre-flight check before you hit "Submit" on your university LMS.

---

## 🚀 Key Features

1. **Two-Slot Upload / Preset Rubrics**:
   - Select from built-in standard rubrics (College Standard APA 7th, IEEE Conference Proceedings, Harvard Academic Report) or upload custom rubrics (JSON or natural-language guideline text/PDF).
2. **Deep Document Layout & Metadata Extraction**:
   - **Deterministic Geometry Inspection:** Real physical margins (top, bottom, left, right in inches), body font family, font size in points, line spacing, and page dimensions extracted directly from PDF binary/XML layers (`PyMuPDF` + `pdfplumber`) and DOCX XML (`python-docx`).
   - **No Hallucinations:** Avoids inaccurate LLM vision guesses for deterministic formatting specs.
   - **Scanned Document Support:** Vision OCR fallback for scanned submissions.
3. **Multi-Category Verification Engine**:
   - 📐 **Formatting Specs:** Font family, font size tolerance, 4-border margins, line spacing, page count, word count, paper dimensions (Letter / A4).
   - 🏗️ **Structural Requirements:** Mandatory sections presence (Abstract, Introduction, Methodology, Results, Conclusion, References) using fuzzy synonym matching and sequence validation.
   - 📚 **Citation & Reference Checks:** Citation style consistency (APA, MLA, IEEE, Harvard), reference list present and count validation, **bidirectional in-text citation cross-referencing** to catch orphaned citations and unreferenced bibliography sources.
   - 🏷️ **Submission Metadata:** Verifies student name, student ID / roll number, course code (e.g. `CS-401`), and date on cover page or headers.
   - ✍️ **Content Quality & Writing Flow:** Flags colloquial / vague phrasing ("things", "stuff", "obviously"), run-on sentences (> 35 words), and calculates lexical diversity (Type-Token Ratio).
4. **Audit Reports & Certificates**:
   - Overall compliance percentage score and letter grade (A+ through F).
   - Filterable issues table with specific rule violated, expected value, actual value, and suggested fix.
   - **Downloadable PDF Audit Certificate** generated via `ReportLab`.
   - **JSON Export** for LMS integration.
5. **Audit History & SQLite Analytics**:
   - Automatically logs submission runs with timestamps, scores, and issue tallies.
   - Historical analytics dashboard tracking score improvements over time.

---

## 📂 Project Architecture

```
student/
├── app.py                         # Streamlit application UI
├── conftest.py                    # Pytest configuration
├── requirements.txt               # Dependencies
├── .env.example                   # Environment configuration template
├── IMPLEMENTATION_PLAN.md         # Detailed engineering plan
├── docs/
│   ├── ARCHITECTURE.md            # Deep system design & data flow
│   ├── RULE_SCHEMA.md             # JSON rubric rule specifications
│   ├── PORTFOLIO_WRITEUP.md       # High-impact portfolio case study writeup
│   └── USER_GUIDE.md              # User manual & troubleshooting
├── rubrics/
│   ├── college_standard_apa.json  # College Standard APA 7th Edition
│   ├── ieee_conference.json       # IEEE Conference Proceedings
│   ├── harvard_academic.json      # Harvard Report Format
│   └── sample_rubric_guidelines.txt
├── samples/
│   ├── generate_sample_docs.py    # Synthetic test document generator
│   ├── sample_assignment_good.pdf # Conforming test document (PDF)
│   ├── sample_assignment_good.docx# Conforming test document (DOCX)
│   ├── sample_assignment_bad.pdf  # Non-conforming test document (PDF)
│   └── sample_assignment_bad.docx # Non-conforming test document (DOCX)
├── src/
│   ├── config.py                  # Environment & tolerance thresholds
│   ├── database.py                # SQLite audit history logging
│   ├── extractor/                 # PDF, DOCX, and Vision extractors
│   ├── rules/                     # Pydantic schemas & rubric parser
│   ├── validator/                 # Formatting, structure, citation validators
│   ├── reporting/                 # PDF certificate & JSON generators
│   └── ui/                        # CSS styling & visual components
└── tests/
    ├── test_database.py           # SQLite tests
    ├── test_extractors.py         # PDF & DOCX extraction tests
    └── test_validators.py         # Compliance evaluation tests
```

---

## ⚡ Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. (Optional) Configure API Keys
Copy `.env.example` to `.env` and add your OpenAI or Gemini key (only required for LLM-based qualitative review or vision OCR; the core deterministic engine runs completely offline):
```bash
cp .env.example .env
```

### 3. Generate Sample Test Documents
```bash
python samples/generate_sample_docs.py
```

### 4. Run the Test Suite
```bash
python -m pytest -v
```

### 5. Launch the Streamlit App
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📑 Rule Categories & Scoring Model

| Category | Weight | Evaluated Rules |
| :--- | :---: | :--- |
| **Formatting Specs** | 25% | Body font family, font size (pt), 4 margins (inches), line spacing, word count, page count, paper size |
| **Structure** | 25% | Required sections presence (fuzzy synonym matching), sequential order, section word counts |
| **Citations** | 25% | Reference list presence, bibliography entry count, style syntax (APA / IEEE / MLA / Harvard), bidirectional cross-reference match |
| **Submission Metadata** | 15% | Student name, Student ID / Roll number, Course code regex, Submission date on title page / header |
| **Content Quality** | 10% | Colloquial vague phrases, run-on sentences (> 35 words), Type-Token Ratio lexical diversity |

---

## 📜 License
MIT License. Free for educational and commercial use.
