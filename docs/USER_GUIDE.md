# User Guide: Assignment & Report Compliance Checker

Welcome to the **Assignment/Report Compliance Checker** user manual. This guide walks you through using the application to verify your academic papers, lab reports, and conference submissions.

---

## 1. Quick Start Guide

### Step 1: Launch the Application
Run the Streamlit app from your terminal:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### Step 2: Select or Upload a Rubric
In the **Compliance Checker** tab:
1. Choose a pre-configured rubric from the dropdown:
   - **College Standard APA (7th Edition)**
   - **IEEE Conference / Journal Style**
   - **Harvard Academic Format**
2. Or switch to **Upload Custom Rubric** to upload a custom JSON rule file or plain-text guidelines.
3. You can also visit the **Rubric Studio** tab to visually edit rules or extract rules from course guideline documents.

### Step 3: Upload Your Assignment
Upload your submission file in either **PDF** (`.pdf`) or **Word Document** (`.docx`) format.
- Click **"Run Compliance Audit"**.
- The engine will immediately extract document geometry, fonts, text layers, citation networks, and metadata.

### Step 4: Review Your Compliance Report
- **Overall Score & Grade:** View your percentage score and letter grade (e.g., `88% (B+)`).
- **Category Status Badges:** Instantly see pass/fail status across Formatting, Structure, Citations, Metadata, and Content Quality.
- **Issues Filter:** Filter issues by Severity (`Critical`, `Warning`, `Info`) or Category.
- **Detailed Action Items:** Each flag lists the exact violation, current value, expected value, and the exact corrective action needed.

### Step 5: Export Your Audit Report
- Click **"Download Audit Certificate (PDF)"** to obtain a formal, formatted PDF report.
- Click **"Export Audit Report (JSON)"** to get raw data for record keeping.

---

## 2. Navigating the Tabs

### 1. 🔍 Compliance Checker
The primary workspace for auditing papers:
- **Upload Zone:** File drop zones with automatic file-type detection.
- **Executive Summary:** Metric cards showing Overall Score, Total Checks, Pass Count, and Fail Count.
- **Findings Table:** Interactive table highlighting specific line items and suggestions.
- **Document Inspector Preview:** View extracted font distributions, measured margins, and detected sections.

### 2. 🛠️ Rubric Studio
Design, modify, and test course compliance rubrics:
- **Visual Rule Builder:** Form-based editor to adjust font family, font size pt, margins, word count limits, and required sections.
- **Natural Language Ingestion:** Paste your syllabus or assignment prompt and let the parser construct the JSON rubric automatically.
- **JSON Editor & Validator:** Direct JSON editing with live schema validation.
- **Save & Export:** Save custom rubrics for repeated use.

### 3. 📊 Audit History & Analytics
- Review past submissions logged in the local SQLite database.
- Track score improvements across submission revisions.
- Inspect previously generated audit results without re-uploading documents.

### 4. ⚙️ Settings & API Configuration
- Add or update optional **OpenAI** or **Google Gemini** API keys for LLM features.
- Tune margin tolerances (default: $\pm 0.15$ in) and font size tolerances (default: $\pm 0.75$ pt).

---

## 3. Understanding Issue Severity Levels

| Severity | Color | Meaning | Academic Impact |
| :--- | :--- | :--- | :--- |
| **CRITICAL** | 🔴 Red | Fundamental structural or citation failure | High probability of severe mark deduction (e.g. missing required section, unreferenced citation, word count below minimum). |
| **WARNING** | 🟡 Yellow | Inconsistency or threshold violation | Minor penalty (e.g. margins slightly off, mismatched body font, course code missing from header). |
| **INFO** | 🔵 Blue | Quality or stylistic suggestion | Constructive advice (e.g. run-on sentence detected, vague words like "stuff" or "things" found). |

---

## 4. Tips for Perfect Submission Compliance
1. **Ensure Heading Consistency:** Use standard heading titles (e.g., "Abstract", "Introduction", "Methodology") so the structural parser recognizes them effortlessly.
2. **Include First-Page Metadata:** Always include your Student Name, Student ID, Course Code, and Date on the title page or header.
3. **Double-Check Citations:** Make sure every author mentioned in the text (e.g., `Smith, 2021`) has a corresponding entry in the References list, and vice versa.
