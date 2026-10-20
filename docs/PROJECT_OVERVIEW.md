# Project Overview: Dimension (Academic Pre-Flight Auditing)

## 📌 In Simple Words: What is this project?

Imagine an **airport pre-flight safety check**, but for **student assignments, reports, and research papers**.

Before a student submits their assignment to a university portal (like Canvas, Blackboard, or Moodle), **Dimension** automatically checks the document to make sure it follows all the college rules (like APA 7th, Harvard, or IEEE styles).

It flags mistakes **before** the professor grades the paper, so students don't lose marks for simple formatting errors!

---

## 🎯 What Problem Does It Solve?

Students often lose 10% to 30% of their assignment marks not because their content is bad, but because of:
- **Wrong margins** (e.g. 0.75 inches instead of 1.0 inch).
- **Wrong font or font size** (e.g. Arial 10pt instead of Times New Roman 12pt).
- **Missing mandatory sections** (e.g. forgot Abstract, Conclusion, or References).
- **Broken citations** (e.g. mentioning a source in text like `(Smith, 2020)` but forgetting to add it in the References list, or vice-versa).
- **Wrong page count or word count**.

Checking all of this manually is time-consuming and prone to human error. **Dimension does it in seconds with a single click.**

---

## 🚀 How Does It Work? (Step-by-Step)

```
[Student Uploads PDF or Word DOCX]
               │
               ▼
   [1. Text & Layout Inspection]
   Extracts physical page margins, fonts, line spacing, and headings
               │
               ▼
   [2. Citation & Reference Matching]
   Finds every in-text citation and cross-checks with bibliography
               │
               ▼
   [3. Rule Evaluation (APA / Harvard / IEEE)]
   Compares measurements against university standards
               │
               ▼
   [4. AI Verification (Google Gemini)]
   Inspects overall coherence, abstract clarity, and structure
               │
               ▼
[Final Report: Score, Letter Grade & Exact Fixes]
```

1. **Upload**: You drag-and-drop a **PDF** or **Word document** (`.docx`).
2. **Select Rules**: Choose a standard style (like **APA 7th Edition**, **IEEE**, or **Harvard**) or upload custom course guidelines.
3. **Audit**: Click **Run Comprehensive Compliance Audit**.
4. **Results**:
   - You get an **overall score** (e.g., `85%`) and a **letter grade** (`B+`).
   - You see a list of **critical penalties** (errors that lose marks) and **actionable fixes** explaining exactly how to fix them.
   - You can download an official **PDF Audit Certificate** or **JSON data report**.

---

## 🖥️ What Are the Main Features in the App?

The application has 4 main modules accessible from the left sidebar:

### 1. 🔍 Compliance Checker
- Drop your file here and click audit.
- Shows your overall score circular gauge, pass rate, and critical flags.
- Gives a breakdown by category: **Formatting**, **Structure**, **Citations**, **Metadata**, and **Content Quality**.
- Lists exact fixes (e.g., *"Change left margin from 0.8 inches to 1.0 inch"*).

### 2. 🛠️ Rubric Studio
- Lets teachers or students create custom rules for specific classes.
- You can paste assignment instructions or a syllabus, and Gemini AI will automatically convert it into structured rules.

### 3. 📊 Audit History
- Keeps track of all past checks in a local SQLite database.
- Allows students to see if their score improved after fixing errors.

### 4. ⚙️ Settings
- Shows system connection status (Database, Gemini AI API key, measurement tolerances).

---

## 💡 Summary of Technologies Used

- **Frontend**: Streamlit with custom CSS (modern, clean SaaS dashboard).
- **Document Extractors**: `PyMuPDF` (for PDFs) and `python-docx` (for Word documents).
- **Rule Engine**: Python algorithms that measure margins, fonts, line heights, and section order deterministically.
- **AI Core**: Google Gemini AI for understanding complex guidelines and natural language rubrics.
- **Database**: SQLite for lightweight, reliable history storage.
- **Reporting**: ReportLab for generating downloadable PDF certificates.
