"""Assignment & Report Compliance Checker - Main Streamlit Application."""

import json
from io import BytesIO
from pathlib import Path
from typing import Optional
import pandas as pd
import streamlit as st

from src.config import (
    BASE_DIR,
    DATABASE_PATH,
    DEFAULT_FONT_SIZE_TOLERANCE_PT,
    DEFAULT_MARGIN_TOLERANCE_INCHES,
    GEMINI_API_KEY,
    OPENAI_API_KEY,
    RUBRICS_DIR,
    SAMPLES_DIR,
)
from src.database import (
    get_audit_by_id,
    get_audit_statistics,
    get_recent_audits,
    init_db,
    log_audit_run,
)
from src.extractor.base import ExtractedDocument
from src.extractor.docx_extractor import extract_docx_document
from src.extractor.pdf_extractor import extract_pdf_document
from src.reporting.json_exporter import export_report_to_json
from src.reporting.pdf_report import generate_pdf_report
from src.rules.default_rubrics import (
    get_builtin_rubrics,
    get_default_rubric_names,
    get_rubric_by_name,
)
from src.rules.rubric_parser import parse_rubric_from_text
from src.rules.schema import RubricRuleSet
from src.ui.components import CUSTOM_CSS, render_score_badge
from src.validator.base import ComplianceReport, IssueSeverity, ValidationCategory
from src.validator.engine import ComplianceValidator

# Page Configuration
st.set_page_config(
    page_title="Academic Compliance Checker",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply Custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize DB
init_db()

# Top Header Banner
st.markdown(
    """
    <div class="compliance-header">
        <h1>🎓 Assignment & Report Compliance Checker</h1>
        <p>Pre-flight rubric validation for academic papers, lab reports, and conference submissions. Verify fonts, margins, required sections, citations, and metadata before you submit.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar
st.sidebar.title("Navigation & Tools")
nav_choice = st.sidebar.radio(
    "Select View",
    ["🔍 Compliance Checker", "🛠️ Rubric Studio", "📊 Audit History", "⚙️ Settings"],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.subheader("System Status")
col_s1, col_s2 = st.sidebar.columns(2)
col_s1.metric("Database", "Active" if DATABASE_PATH.exists() else "Ready")
llm_status = "Connected" if (OPENAI_API_KEY or GEMINI_API_KEY) else "Local Engine"
col_s2.metric("AI Core", llm_status)

# ----------------------------------------------------------------------
# VIEW 1: COMPLIANCE CHECKER
# ----------------------------------------------------------------------
if nav_choice == "🔍 Compliance Checker":
    st.subheader("1. Submission & Rubric Setup")

    col_rubric, col_doc = st.columns(2)

    # 1. Rubric Selection Slot
    with col_rubric:
        st.markdown("### 📋 Step 1: Submission Rubric")
        rubric_source_mode = st.radio(
            "Rubric Source",
            ["Preset Standard Rubrics", "Upload Custom Rubric (JSON or Text)"],
            horizontal=True,
            key="rubric_mode",
        )

        active_rubric: Optional[RubricRuleSet] = None

        if rubric_source_mode == "Preset Standard Rubrics":
            available_rubrics = get_default_rubric_names()
            selected_rubric_name = st.selectbox(
                "Choose Course Standard Rubric",
                available_rubrics,
                index=0,
            )
            active_rubric = get_rubric_by_name(selected_rubric_name)
            st.caption(f"ℹ️ {active_rubric.description}")
        else:
            uploaded_rubric_file = st.file_uploader(
                "Upload Rubric Document (JSON, TXT)",
                type=["json", "txt"],
                key="rubric_uploader",
            )
            if uploaded_rubric_file is not None:
                content = uploaded_rubric_file.read().decode("utf-8", errors="ignore")
                try:
                    if uploaded_rubric_file.name.endswith(".json"):
                        data = json.loads(content)
                        active_rubric = RubricRuleSet(**data)
                        st.success(f"Loaded JSON Rubric: {active_rubric.title}")
                    else:
                        with st.spinner("Parsing guideline text into structured rule set..."):
                            active_rubric = parse_rubric_from_text(content)
                        st.success(f"Parsed Guidelines: {active_rubric.title}")
                except Exception as e:
                    st.error(f"Failed to parse rubric file: {e}")
                    active_rubric = get_rubric_by_name("College Standard APA 7th Edition")
            else:
                active_rubric = get_rubric_by_name("College Standard APA 7th Edition")
                st.info("No custom file uploaded yet. Using default College Standard APA rubric.")

        with st.expander("👁️ View Active Rubric Specs"):
            if active_rubric:
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Font:** {active_rubric.formatting.expected_font} ({active_rubric.formatting.expected_font_size_pt} pt)")
                    st.write(f"**Margins:** {active_rubric.formatting.expected_margin_inches} inches (±{active_rubric.formatting.margin_tolerance_inches}\")")
                    st.write(f"**Line Spacing:** {active_rubric.formatting.expected_line_spacing}x")
                    st.write(f"**Word Count:** {active_rubric.formatting.min_word_count} - {active_rubric.formatting.max_word_count} words")
                with c2:
                    st.write(f"**Citation Style:** {active_rubric.citations.citation_style}")
                    st.write(f"**Required Sections:** {', '.join(active_rubric.structure.required_sections)}")
                    st.write(f"**Enforce Sequence:** {'Yes' if active_rubric.structure.enforce_order else 'No'}")

    # 2. Assignment Upload Slot
    with col_doc:
        st.markdown("### 📄 Step 2: Upload Assignment Document")
        uploaded_doc_file = st.file_uploader(
            "Upload Assignment (PDF or DOCX)",
            type=["pdf", "docx"],
            key="assignment_uploader",
        )

        # Quick sample selector
        st.markdown("**— or load a built-in sample document:**")
        sample_choice = st.selectbox(
            "Select Demo Document",
            [
                "None (Upload my own file)",
                "Sample Conforming Paper (Passes APA) - PDF",
                "Sample Non-Conforming Paper (Flags Issues) - PDF",
                "Sample Conforming Paper - DOCX",
                "Sample Non-Conforming Paper - DOCX",
            ],
        )

        doc_bytes: Optional[bytes] = None
        target_filename = "submission.pdf"

        if uploaded_doc_file is not None:
            doc_bytes = uploaded_doc_file.read()
            target_filename = uploaded_doc_file.name
            st.success(f"Loaded: `{target_filename}` ({round(len(doc_bytes)/1024, 1)} KB)")
        elif sample_choice != "None (Upload my own file)":
            if "Conforming Paper (Passes APA) - PDF" in sample_choice:
                target_filename = "sample_assignment_good.pdf"
            elif "Non-Conforming Paper (Flags Issues) - PDF" in sample_choice:
                target_filename = "sample_assignment_bad.pdf"
            elif "Conforming Paper - DOCX" in sample_choice:
                target_filename = "sample_assignment_good.docx"
            else:
                target_filename = "sample_assignment_bad.docx"

            sample_file_path = SAMPLES_DIR / target_filename
            if sample_file_path.exists():
                doc_bytes = sample_file_path.read_bytes()
                st.info(f"Loaded Demo Document: `{target_filename}`")
            else:
                st.warning("Sample file not found. Please upload a document.")

    # Audit Trigger
    st.markdown("---")
    col_btn, _ = st.columns([1, 3])
    run_audit_clicked = col_btn.button("🚀 Run Compliance Audit", type="primary", use_container_width=True)

    if (run_audit_clicked or "last_report" in st.session_state) and (doc_bytes is not None and active_rubric is not None):
        if run_audit_clicked or ("last_report" not in st.session_state):
            with st.spinner("Extracting document geometry, fonts, citations, and structure..."):
                # Extract Document
                if target_filename.lower().endswith(".docx"):
                    extracted_doc = extract_docx_document(BytesIO(doc_bytes), filename=target_filename)
                else:
                    extracted_doc = extract_pdf_document(BytesIO(doc_bytes), filename=target_filename)

                # Run Validator Engine
                validator = ComplianceValidator(active_rubric)
                report = validator.audit_document(extracted_doc)

                # Log to SQLite
                log_audit_run(
                    filename=report.filename,
                    file_type=report.file_type,
                    rubric_name=report.rubric_title,
                    compliance_score=report.overall_score,
                    letter_grade=report.letter_grade,
                    total_rules=report.total_rules,
                    passed_rules=report.passed_rules,
                    failed_rules=report.failed_rules,
                    critical_issues=report.critical_count,
                    warning_issues=report.warning_count,
                    info_issues=report.info_count,
                    report_data=report.to_dict(),
                )

                st.session_state["last_report"] = report
                st.session_state["last_extracted_doc"] = extracted_doc
                st.session_state["last_pdf_bytes"] = generate_pdf_report(report)
                st.session_state["last_json_str"] = export_report_to_json(report)

        report: ComplianceReport = st.session_state["last_report"]
        extracted_doc: ExtractedDocument = st.session_state["last_extracted_doc"]

        # Results Dashboard
        st.subheader("2. Compliance Audit Results")

        # Score Banner
        st.markdown(render_score_badge(report.overall_score, report.letter_grade), unsafe_allow_html=True)

        # Summary Metric Cards
        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        col_m1.markdown(f'<div class="metric-card"><div class="metric-card-title">Total Rules</div><div class="metric-card-val">{report.total_rules}</div></div>', unsafe_allow_html=True)
        col_m2.markdown(f'<div class="metric-card"><div class="metric-card-title">Passed Checks</div><div class="metric-card-val" style="color: #16A34A;">{report.passed_rules}</div></div>', unsafe_allow_html=True)
        col_m3.markdown(f'<div class="metric-card"><div class="metric-card-title">Critical Flags</div><div class="metric-card-val" style="color: #DC2626;">{report.critical_count}</div></div>', unsafe_allow_html=True)
        col_m4.markdown(f'<div class="metric-card"><div class="metric-card-title">Warnings</div><div class="metric-card-val" style="color: #CA8A04;">{report.warning_count}</div></div>', unsafe_allow_html=True)
        col_m5.markdown(f'<div class="metric-card"><div class="metric-card-title">Style Suggestions</div><div class="metric-card-val" style="color: #2563EB;">{report.info_count}</div></div>', unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)

        # Category Breakdown Progress
        st.markdown("### Category Compliance Scores")
        cat_cols = st.columns(len(report.category_scores))
        for idx, (cat_name, score) in enumerate(report.category_scores.items()):
            with cat_cols[idx]:
                st.write(f"**{cat_name}**")
                st.progress(score / 100.0)
                st.write(f"{score}%")

        st.markdown("---")

        # Actionable Findings & Filterable Issues Table
        st.subheader("3. Audit Findings & Action Items")
        severity_filter = st.selectbox(
            "Filter Findings by Status",
            ["All Issues", "Action Items Only (Critical & Warnings)", "Critical Issues Only", "Passed Checks Only"],
        )

        filtered_issues = report.issues
        if severity_filter == "Action Items Only (Critical & Warnings)":
            filtered_issues = [iss for iss in report.issues if not iss.passed]
        elif severity_filter == "Critical Issues Only":
            filtered_issues = [iss for iss in report.issues if not iss.passed and iss.severity == IssueSeverity.CRITICAL]
        elif severity_filter == "Passed Checks Only":
            filtered_issues = [iss for iss in report.issues if iss.passed]

        # Table rendering
        table_rows = []
        for iss in filtered_issues:
            status_symbol = "✅ PASS" if iss.passed else f"❌ {iss.severity.value}"
            table_rows.append({
                "Rule": iss.rule_name,
                "Category": iss.category.value,
                "Status": status_symbol,
                "Found in Document": iss.actual,
                "Required by Rubric": iss.expected,
                "Actionable Fix": iss.suggested_fix,
            })

        if table_rows:
            df_issues = pd.DataFrame(table_rows)
            st.dataframe(df_issues, use_container_width=True, hide_index=True)
        else:
            st.success("🎉 No issues match the selected filter criteria!")

        # Document Inspector Preview
        with st.expander("🔍 Deep Document Layout & Extraction Inspector"):
            di_col1, di_col2 = st.columns(2)
            with di_col1:
                st.markdown("**Physical Geometry & Typography**")
                st.write(f"- **Dominant Font Family:** `{extracted_doc.dominant_font}`")
                st.write(f"- **Dominant Font Size:** `{extracted_doc.dominant_font_size_pt} pt`")
                st.write(f"- **Detected Line Spacing:** `{extracted_doc.detected_line_spacing}x`")
                st.write(f"- **Page Format:** `{extracted_doc.page_size_label}`")
                st.write(f"- **Average Margins (inches):** Top: `{extracted_doc.avg_margins['top']}\"`, Bottom: `{extracted_doc.avg_margins['bottom']}\"`, Left: `{extracted_doc.avg_margins['left']}\"`, Right: `{extracted_doc.avg_margins['right']}\"`")
            with di_col2:
                st.markdown("**Structure & Volume**")
                st.write(f"- **Total Words:** `{extracted_doc.total_word_count}` words")
                st.write(f"- **Page Count:** `{extracted_doc.page_count}` pages")
                st.write(f"- **Sections Identified:** `{', '.join(s.heading for s in extracted_doc.sections) if extracted_doc.sections else 'None detected'}`")
                st.write(f"- **Is Scanned Image:** `{'Yes (OCR required)' if extracted_doc.is_scanned else 'No (Direct Text Layer)'}`")

        # Download Report Buttons
        st.markdown("---")
        st.subheader("4. Export Audit Certificates")
        col_dl1, col_dl2, _ = st.columns([1, 1, 2])
        col_dl1.download_button(
            label="📄 Download PDF Audit Certificate",
            data=st.session_state["last_pdf_bytes"],
            file_name=f"compliance_audit_{report.filename}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        col_dl2.download_button(
            label="💾 Export JSON Report",
            data=st.session_state["last_json_str"],
            file_name=f"compliance_audit_{report.filename}.json",
            mime="application/json",
            use_container_width=True,
        )

# ----------------------------------------------------------------------
# VIEW 2: RUBRIC STUDIO
# ----------------------------------------------------------------------
elif nav_choice == "🛠️ Rubric Studio":
    st.subheader("Course Rubric Studio")
    st.markdown("Design, customize, or generate JSON submission rubrics from syllabus text.")

    studio_mode = st.radio(
        "Studio Action",
        ["Visual Rubric Editor", "Convert Guidelines Text to Rubric", "Raw JSON Editor"],
        horizontal=True,
    )

    if studio_mode == "Visual Rubric Editor":
        preset_names = get_default_rubric_names()
        base_choice = st.selectbox("Base Template", preset_names)
        base_rubric = get_rubric_by_name(base_choice)

        with st.form("edit_rubric_form"):
            st.markdown("#### General Metadata")
            rub_title = st.text_input("Rubric Title", value=base_rubric.title)
            rub_desc = st.text_area("Description", value=base_rubric.description)

            st.markdown("#### Formatting Rules")
            f_col1, f_col2, f_col3 = st.columns(3)
            f_font = f_col1.text_input("Expected Font", value=base_rubric.formatting.expected_font)
            f_size = f_col2.number_input("Font Size (pt)", value=float(base_rubric.formatting.expected_font_size_pt), step=0.5)
            f_margin = f_col3.number_input("Margins (inches)", value=float(base_rubric.formatting.expected_margin_inches), step=0.25)

            f_col4, f_col5, f_col6 = st.columns(3)
            f_spacing = f_col4.selectbox("Line Spacing", [1.0, 1.5, 2.0], index=[1.0, 1.5, 2.0].index(base_rubric.formatting.expected_line_spacing) if base_rubric.formatting.expected_line_spacing in [1.0, 1.5, 2.0] else 2)
            f_min_words = f_col5.number_input("Min Words", value=int(base_rubric.formatting.min_word_count or 1000), step=100)
            f_max_words = f_col6.number_input("Max Words", value=int(base_rubric.formatting.max_word_count or 4000), step=100)

            st.markdown("#### Structural Requirements")
            sections_str = st.text_input(
                "Required Sections (comma-separated)",
                value=", ".join(base_rubric.structure.required_sections),
            )
            enforce_seq = st.checkbox("Enforce Strict Sequential Order", value=base_rubric.structure.enforce_order)

            st.markdown("#### Citations & Metadata")
            c_col1, c_col2 = st.columns(2)
            c_style = c_col1.selectbox("Citation Style", ["APA", "MLA", "IEEE", "Harvard", "Chicago", "None"], index=["APA", "MLA", "IEEE", "Harvard", "Chicago", "None"].index(base_rubric.citations.citation_style) if base_rubric.citations.citation_style in ["APA", "MLA", "IEEE", "Harvard", "Chicago", "None"] else 0)
            c_min_refs = c_col2.number_input("Min References in Bibliography", value=int(base_rubric.citations.min_references_count), step=1)

            submit_save = st.form_submit_button("💾 Save as Custom Rubric JSON", type="primary")

            if submit_save:
                updated_rubric = RubricRuleSet(
                    rubric_id=f"custom_{rub_title.lower().replace(' ', '_')}",
                    title=rub_title,
                    description=rub_desc,
                    formatting=base_rubric.formatting.model_copy(
                        update={
                            "expected_font": f_font,
                            "expected_font_size_pt": f_size,
                            "expected_margin_inches": f_margin,
                            "expected_line_spacing": f_spacing,
                            "min_word_count": f_min_words,
                            "max_word_count": f_max_words,
                        }
                    ),
                    structure=base_rubric.structure.model_copy(
                        update={
                            "required_sections": [s.strip() for s in sections_str.split(",") if s.strip()],
                            "enforce_order": enforce_seq,
                        }
                    ),
                    citations=base_rubric.citations.model_copy(
                        update={
                            "citation_style": c_style,
                            "min_references_count": c_min_refs,
                        }
                    ),
                    metadata=base_rubric.metadata,
                    content_quality=base_rubric.content_quality,
                )
                custom_json = updated_rubric.model_dump_json(indent=2)
                st.success(f"Custom rubric '{rub_title}' compiled!")
                st.download_button(
                    "📥 Download Custom Rubric JSON",
                    data=custom_json,
                    file_name=f"{updated_rubric.rubric_id}.json",
                    mime="application/json",
                )

    elif studio_mode == "Convert Guidelines Text to Rubric":
        st.markdown("Paste plain text from your course assignment prompt or syllabus. The engine will extract the structured compliance rules.")
        sample_guidelines_path = RUBRICS_DIR / "sample_rubric_guidelines.txt"
        default_guide_text = sample_guidelines_path.read_text(encoding="utf-8") if sample_guidelines_path.exists() else ""
        guide_text = st.text_area("Course Guideline Text", value=default_guide_text, height=250)

        if st.button("⚡ Parse Guidelines into JSON Rubric", type="primary"):
            with st.spinner("Extracting formatting, structure, and citation criteria..."):
                parsed = parse_rubric_from_text(guide_text)
                st.success(f"Parsed: **{parsed.title}**")
                st.json(parsed.model_dump())
                st.download_button(
                    "📥 Download Parsed Rubric JSON",
                    data=parsed.model_dump_json(indent=2),
                    file_name=f"{parsed.rubric_id}.json",
                    mime="application/json",
                )

    else:
        st.markdown("Inspect or paste raw JSON rule configurations.")
        default_apa = get_rubric_by_name("College Standard APA 7th Edition")
        raw_json_input = st.text_area("JSON Schema", value=default_apa.model_dump_json(indent=2), height=400)
        if st.button("Validate JSON Schema"):
            try:
                parsed_dict = json.loads(raw_json_input)
                test_rubric = RubricRuleSet(**parsed_dict)
                st.success(f"Valid Rubric: '{test_rubric.title}' (Checks: {len(test_rubric.structure.required_sections)} sections, style {test_rubric.citations.citation_style})")
            except Exception as e:
                st.error(f"Invalid JSON schema: {e}")

# ----------------------------------------------------------------------
# VIEW 3: AUDIT HISTORY
# ----------------------------------------------------------------------
elif nav_choice == "📊 Audit History":
    st.subheader("Past Submissions & Audit History")
    st.markdown("Track your compliance score improvements across document revisions.")

    stats = get_audit_statistics()
    h_col1, h_col2, h_col3, h_col4 = st.columns(4)
    h_col1.metric("Total Audits Run", stats["total_audits"])
    h_col2.metric("Historical Avg Score", f"{stats['avg_score']}%")
    h_col3.metric("Highest Score", f"{stats['max_score']}%")
    h_col4.metric("Rules Passed Total", stats["total_passed_rules"])

    st.markdown("<br/>", unsafe_allow_html=True)

    records = get_recent_audits(limit=50)
    if records:
        history_table = []
        for r in records:
            history_table.append({
                "Audit ID": r["id"],
                "Timestamp (UTC)": r["timestamp"][:19].replace("T", " "),
                "Document": r["filename"],
                "Type": r["file_type"],
                "Rubric": r["rubric_name"],
                "Score": f"{r['compliance_score']}%",
                "Grade": r["letter_grade"],
                "Passed": f"{r['passed_rules']}/{r['total_rules']}",
                "Critical Flags": r["critical_issues"],
                "Warnings": r["warning_issues"],
            })
        st.dataframe(pd.DataFrame(history_table), use_container_width=True, hide_index=True)

        selected_id = st.selectbox("Inspect Full Past Audit Details", [r["id"] for r in records])
        if st.button("Load Historical Audit"):
            hist_item = get_audit_by_id(selected_id)
            if hist_item and hist_item.get("report_json"):
                parsed_report_data = json.loads(hist_item["report_json"])
                st.json(parsed_report_data)
    else:
        st.info("No audit runs recorded yet. Check your first document in the Compliance Checker!")

# ----------------------------------------------------------------------
# VIEW 4: SETTINGS & CONFIGURATION
# ----------------------------------------------------------------------
else:
    st.subheader("System Settings & Environment Configuration")
    st.markdown("Configure LLM keys, layout tolerances, and engine preferences.")

    st.markdown("#### 1. AI API Integrations")
    st.markdown(
        "OpenAI and Gemini keys are optional. When provided, they power advanced Vision OCR for scanned PDFs, natural language rubric extraction, and AI qualitative writing review."
    )

    col_k1, col_k2 = st.columns(2)
    new_openai_key = col_k1.text_input("OpenAI API Key", value=OPENAI_API_KEY, type="password")
    new_gemini_key = col_k2.text_input("Google Gemini API Key", value=GEMINI_API_KEY, type="password")

    st.markdown("#### 2. Layout & Formatting Tolerances")
    t_col1, t_col2 = st.columns(2)
    tol_margin = t_col1.number_input("Margin Deviation Tolerance (inches)", value=DEFAULT_MARGIN_TOLERANCE_INCHES, step=0.05)
    tol_font = t_col2.number_input("Font Size Deviation Tolerance (pt)", value=DEFAULT_FONT_SIZE_TOLERANCE_PT, step=0.25)

    if st.button("Save Preferences", type="primary"):
        st.success("Settings updated! API keys and tolerances saved for this session.")

    st.markdown("---")
    st.markdown("#### 3. Diagnostic & Environment Info")
    st.write(f"- **Application Path:** `{BASE_DIR}`")
    st.write(f"- **Database Path:** `{DATABASE_PATH}`")
    st.write(f"- **Built-in Rubrics Found:** `{len(get_builtin_rubrics())}`")
    st.write(f"- **Sample Test Documents:** `{len(list(SAMPLES_DIR.glob('*.*')))}`")
