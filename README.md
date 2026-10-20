<div align="center">

# 🎓 Academic Compliance Checker (ACE)

**Automated Pre-Flight Auditing for Academic Submissions, Papers & Course Reports**

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![PyMuPDF](https://img.shields.io/badge/PDF_Engine-PyMuPDF-2A8554?style=for-the-badge)](https://pymupdf.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

<p align="center">
  <a href="#-overview--motivation">Overview</a> •
  <a href="#-features">Features</a> •
  <a href="#-quickstart">Quickstart</a> •
  <a href="#-project-architecture">Architecture</a> •
  <a href="#-scoring-model">Scoring Model</a> •
  <a href="#-license">License</a>
</p>

</div>

---

## 🌟 Overview & Motivation

Students routinely lose **10% to 25% of their total grade** on mechanical formatting and submission technicalities—such as incorrect margin dimensions, non-compliant font sizes, missing mandatory sections, mismatched citations, or missing cover page metadata—even when their research and core content are exemplary.

**Academic Compliance Checker (ACE)** provides an automated, deterministic pre-flight check to verify documents before uploading to university LMS platforms (Canvas, Blackboard, Moodle) or conference submission portals.

> [!TIP]
> **Deterministic Inspection Without Hallucinations:** ACE computes real physical margins (in inches), font pt sizes, and spacing directly from document vector & XML streams (`PyMuPDF`, `pdfplumber`, `python-docx`), with an optional Google Gemini vision OCR fallback for scanned papers.

---

## 🚀 Features

### 1. Two-Slot Submission & Built-in Rubrics
- Select from built-in standard rubrics:
  - 📘 **College Standard APA 7th Edition**
  - ⚡ **IEEE Conference Proceedings**
  - 🏛️ **Harvard Academic Report Format**
- Or upload **custom rubrics** via structured JSON or natural-language guideline text/PDFs.

### 2. Multi-Category Verification Engine
- 📐 **Formatting Specs:** Body font family, font size tolerance, 4-border margins (top, bottom, left, right in inches), line spacing, page count, word count, paper dimensions (Letter / A4).
- 🏗️ **Structural Integrity:** Mandatory section presence (Abstract, Introduction, Methodology, Results, Conclusion, References) validated with fuzzy synonym matching and sequence checking.
- 📚 **Citation & Bibliography Engine:** Style syntax checks (APA, MLA, IEEE, Harvard), reference count validation, and **bidirectional in-text cross-referencing** to catch orphaned citations and unreferenced bibliography entries.
- 🏷️ **Submission Metadata:** Automatic verification of student name, student ID / roll number, course code (e.g., `CS-401`), and date on cover pages or headers.
- ✍️ **Writing Flow & Quality:** Detection of colloquial/vague phrasing, run-on sentences (> 35 words), and lexical diversity (Type-Token Ratio).

### 3. Comprehensive Reports & Analytics
- **Compliance Score Gauge:** Overall percentage score and letter grade (A+ through F).
- **Issue Breakdown:** Grouped by severity (Error, Warning, Info) with exact expected vs. actual values and actionable fixes.
- **Official PDF Certificate:** Downloadable audit report generated via ReportLab.
- **Audit History Dashboard:** Embedded SQLite analytics tracking student progress over time.

---

## 📂 Project Architecture

```
Academic-compliance-checker/
├── app.py                         # Streamlit application UI & dashboards
├── conftest.py                    # Pytest test suite configuration
├── requirements.txt               # Python package dependencies
├── .env.example                   # Environment configuration template
├── IMPLEMENTATION_PLAN.md         # Detailed engineering plan
├── docs/
│   ├── ARCHITECTURE.md            # Deep system design & data flow
│   ├── RULE_SCHEMA.md             # JSON rubric rule specifications
│   ├── PORTFOLIO_WRITEUP.md       # Case study & portfolio writeup
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
│   └── ui/                        # CSS styling, theme toggles & gauge components
└── tests/
    ├── test_database.py           # SQLite database persistence tests
    ├── test_extractors.py         # PDF & DOCX extraction tests
    ├── test_validators.py         # Compliance evaluation tests
    └── test_ui_streamlit.py       # Streamlit AppTest frontend tests
```

---

## ⚡ Quickstart

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/VanshSUTHAR/Academic-compliance-checker.git
cd Academic-compliance-checker
```

```bash
# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. (Optional) Configure Google Gemini API Key

Copy `.env.example` to `.env` and insert your Gemini API key (optional; powers Vision OCR for scanned PDFs, automated syllabus parsing, and AI qualitative writing review, while the core deterministic engine runs completely offline):

```bash
cp .env.example .env
```

### 3. Generate Sample Test Documents

```bash
python samples/generate_sample_docs.py
```

### 4. Run the Automated Test Suite

```bash
python -m pytest -v
```

### 5. Launch the Web Application

```bash
streamlit run app.py
```

Open your browser at **`http://localhost:8501`**.

---

## 📑 Scoring Model

| Category | Weight | Evaluated Rules |
| :--- | :---: | :--- |
| **Formatting Specs** | **25%** | Body font family, font size (pt), 4-border margins (inches), line spacing, word count, page count, paper dimensions |
| **Structure** | **25%** | Required sections presence (fuzzy synonym matching), sequential order, section word counts |
| **Citations** | **25%** | Reference list presence, bibliography entry count, style syntax (APA / IEEE / MLA / Harvard), bidirectional cross-reference match |
| **Submission Metadata** | **15%** | Student name, Student ID / Roll number, Course code regex, Submission date on title page / header |
| **Content Quality** | **10%** | Colloquial vague phrases, run-on sentences (> 35 words), Type-Token Ratio lexical diversity |

---

## 📜 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
