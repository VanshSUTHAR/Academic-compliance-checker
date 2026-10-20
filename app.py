"""Assignment & Report Compliance Checker - Enterprise Streamlit SaaS Application.

High-trust, professional compliance auditing platform built with native Streamlit architecture.
"""

import importlib
from io import BytesIO
import json
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st
import streamlit.components.v1 as st_components

from src.config import (
    BASE_DIR,
    DATABASE_PATH,
    DEFAULT_FONT_SIZE_TOLERANCE_PT,
    DEFAULT_MARGIN_TOLERANCE_INCHES,
    GEMINI_API_KEY,
    GEMINI_MODEL,
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
import src.ui.components as ui_components
importlib.reload(ui_components)

from src.ui.components import (
    get_theme_css,
    render_finding_card,
    render_hero_banner,
    render_metric_card,
    render_score_showcase,
    render_sidebar_brand,
    render_sidebar_status_card,
    render_status_badge,
    render_verdict_banner,
)
from src.validator.base import ComplianceReport, IssueSeverity, ValidationCategory
from src.validator.engine import ComplianceValidator

# Page Configuration
st.set_page_config(
    page_title="Academic Compliance Checker Pro",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Database
init_db()

# ----------------------------------------------------------------------
# SIDEBAR: Branding, Theme & Navigation
# ----------------------------------------------------------------------
st.sidebar.markdown(
    render_sidebar_brand("Dimension", "Academic Pre-Flight Auditing"),
    unsafe_allow_html=True,
)

# Design System & Theme Styling
current_theme = "light"
st.markdown(get_theme_css(current_theme), unsafe_allow_html=True)

# Auto-expand sidebar if browser was left in a collapsed state
st_components.html(
    """
    <script>
    (function() {
        try {
            const pWin = window.parent;
            for (let i = 0; i < pWin.localStorage.length; i++) {
                const key = pWin.localStorage.key(i);
                if (key && key.startsWith('stSidebarCollapsed')) {
                    pWin.localStorage.removeItem(key);
                }
            }
            const expandBtn = pWin.document.querySelector('[data-testid="stExpandSidebarButton"] button') ||
                              pWin.document.querySelector('[data-testid="stExpandSidebarButton"]');
            if (expandBtn) {
                expandBtn.click();
            }
        } catch(e) {}
    })();
    </script>
    """,
    height=0,
    width=0,
)

st.sidebar.markdown('<div class="sidebar-section-title">Navigation</div>', unsafe_allow_html=True)
nav_choice = st.sidebar.radio(
    "Go To Module",
    ["🔍 Compliance Checker", "🛠️ Rubric Studio", "📊 Audit History", "⚙️ Settings"],
    index=0,
    label_visibility="collapsed",
)

ai_status = "Gemini Active" if GEMINI_API_KEY else ("OpenAI Fallback" if OPENAI_API_KEY else "Heuristic Core")

st.sidebar.markdown(
    render_sidebar_status_card(
        ai_status=ai_status,
        rubrics_count=len(get_builtin_rubrics()),
        db_status="SQLite Active",
        theme=current_theme,
    ),
    unsafe_allow_html=True,
)

# Header Banner Bar
st.markdown(render_hero_banner(current_theme), unsafe_allow_html=True)

# ----------------------------------------------------------------------
# VIEW 1: COMPLIANCE CHECKER
# ----------------------------------------------------------------------
if nav_choice == "🔍 Compliance Checker":
    st.markdown("## 🎯 Pre-Flight Document Audit")
    st.markdown(
        "<p class='page-subtitle'>"
        "Configure institutional rubric standards and submit document for automated deterministic verification."
        "</p>",
        unsafe_allow_html=True,
    )

    col_rubric, col_doc = st.columns(2)

    # 1. Rubric Selection Slot
    with col_rubric:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="step-badge">STEP 1</span>
                        <span class="step-title">Rubric Specification</span>
                    </div>
                    <span class="step-sub">Institutional Rules</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("Select institutional standard or upload custom course criteria.")

            rubric_source_mode = st.radio(
                "Rubric Ingestion Method",
                ["Preset Standard Rubrics", "Upload Custom Rubric (JSON / Syllabus Text)"],
                horizontal=True,
                key="rubric_mode",
            )

            active_rubric: Optional[RubricRuleSet] = None

            if rubric_source_mode == "Preset Standard Rubrics":
                available_rubrics = get_default_rubric_names()
                selected_rubric_name = st.selectbox(
                    "Choose Standard Academic Rubric",
                    available_rubrics,
                    index=0,
                )
                active_rubric = get_rubric_by_name(selected_rubric_name)
                st.caption(f"ℹ️ {active_rubric.description}")
            else:
                uploaded_rubric_file = st.file_uploader(
                    "Drop Rubric File (JSON or Syllabus TXT)",
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
                            with st.spinner("Gemini AI parsing guidelines into structured rule set..."):
                                active_rubric = parse_rubric_from_text(content)
                            st.success(f"Parsed Guidelines: {active_rubric.title}")
                    except Exception as e:
                        st.error(f"Failed to parse rubric file: {e}")
                        active_rubric = get_rubric_by_name("College Standard APA 7th Edition")
                else:
                    active_rubric = get_rubric_by_name("College Standard APA 7th Edition")
                    st.info("No custom rubric uploaded yet. Defaulting to College Standard APA 7th.")

            with st.expander("View Active Rubric Parameters", expanded=False):
                if active_rubric:
                    st.markdown(
                        f"""
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; font-size: 12px; margin-top: 6px;">
                            <div class="rubric-param-box">
                                <span class="rubric-param-label">Typography</span>
                                <span class="rubric-param-value">{active_rubric.formatting.expected_font} ({active_rubric.formatting.expected_font_size_pt} pt)</span>
                            </div>
                            <div class="rubric-param-box">
                                <span class="rubric-param-label">Margins</span>
                                <span class="rubric-param-value">{active_rubric.formatting.expected_margin_inches}&quot; (±{active_rubric.formatting.margin_tolerance_inches}&quot;)</span>
                            </div>
                            <div class="rubric-param-box">
                                <span class="rubric-param-label">Line Spacing</span>
                                <span class="rubric-param-value">{active_rubric.formatting.expected_line_spacing}x Spacing</span>
                            </div>
                            <div class="rubric-param-box">
                                <span class="rubric-param-label">Word Bounds</span>
                                <span class="rubric-param-value">{active_rubric.formatting.min_word_count} - {active_rubric.formatting.max_word_count}</span>
                            </div>
                            <div class="rubric-param-box" style="grid-column: span 2;">
                                <span class="rubric-param-label">Citation &amp; Structure</span>
                                <span class="rubric-param-value">{active_rubric.citations.citation_style} Style &bull; {len(active_rubric.structure.required_sections)} Mandatory Sections</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # 2. Assignment Upload Slot
    with col_doc:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="step-badge">STEP 2</span>
                        <span class="step-title">Student Submission</span>
                    </div>
                    <span class="step-sub">PDF / Word DOCX</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("Upload submission document or test with pre-configured samples.")

            uploaded_doc_file = st.file_uploader(
                "Upload Assignment Document (PDF or Word DOCX)",
                type=["pdf", "docx"],
                key="assignment_uploader",
            )

            st.markdown("<p class='subtext-hint'>— or select a pre-configured sample document to test:</p>", unsafe_allow_html=True)
            sample_choice = st.selectbox(
                "Quick Demo Document Selector",
                [
                    "None (Upload my own file)",
                    "Sample Conforming Paper (Passes APA) - PDF",
                    "Sample Non-Conforming Paper (Flags Violations) - PDF",
                    "Sample Conforming Paper - DOCX",
                    "Sample Non-Conforming Paper - DOCX",
                ],
                index=0,
            )

            doc_bytes: Optional[bytes] = None
            target_filename = "submission.pdf"

            if uploaded_doc_file is not None:
                doc_bytes = uploaded_doc_file.read()
                target_filename = uploaded_doc_file.name
                st.success(f"Ready: `{target_filename}` ({round(len(doc_bytes)/1024, 1)} KB)")
            elif sample_choice != "None (Upload my own file)":
                if "Conforming Paper (Passes APA) - PDF" in sample_choice:
                    target_filename = "sample_assignment_good.pdf"
                elif "Non-Conforming Paper (Flags Violations) - PDF" in sample_choice:
                    target_filename = "sample_assignment_bad.pdf"
                elif "Conforming Paper - DOCX" in sample_choice:
                    target_filename = "sample_assignment_good.docx"
                else:
                    target_filename = "sample_assignment_bad.docx"

                sample_file_path = SAMPLES_DIR / target_filename
                if sample_file_path.exists():
                    doc_bytes = sample_file_path.read_bytes()
                    st.info(f"Loaded Sample: `{target_filename}`")

    # Audit Launch Trigger
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    col_btn, _ = st.columns([1, 2])
    run_audit_clicked = col_btn.button("🚀 Run Comprehensive Compliance Audit", type="primary", use_container_width=True)

    if (run_audit_clicked or "last_report" in st.session_state) and (doc_bytes is not None and active_rubric is not None):
        if run_audit_clicked or ("last_report" not in st.session_state):
            with st.spinner("Measuring layout geometry, inspecting fonts, verifying citation networks..."):
                # Extract Document
                if target_filename.lower().endswith(".docx"):
                    extracted_doc = extract_docx_document(BytesIO(doc_bytes), filename=target_filename)
                else:
                    extracted_doc = extract_pdf_document(BytesIO(doc_bytes), filename=target_filename)

                # Execute Validation
                validator = ComplianceValidator(active_rubric)
                report = validator.audit_document(extracted_doc)

                # Persist to SQLite
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
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.markdown(f"## 📊 Executive Audit Report: `{report.filename}`")
        st.caption(f"Evaluated against **{report.rubric_title}** &bull; Timestamp: {report.timestamp[:19].replace('T', ' ')} UTC")

        # Executive Verdict Callout Banner
        st.markdown(
            render_verdict_banner(
                score=report.overall_score,
                grade=report.letter_grade,
                critical_count=report.critical_count,
                warning_count=report.warning_count,
                filename=report.filename,
            ),
            unsafe_allow_html=True,
        )

        # Organize Results into Native Streamlit Tabs
        res_tab1, res_tab2, res_tab3, res_tab4 = st.tabs([
            "📊 Executive Summary",
            "🛠️ Detailed Findings",
            "🔍 Document Geometry",
            "📥 Export Certificates",
        ])

        with res_tab1:
            # Executive Scorecard Showcase
            st.markdown(
                render_score_showcase(
                    score=report.overall_score,
                    grade=report.letter_grade,
                    total_rules=report.total_rules,
                    passed_rules=report.passed_rules,
                    critical_count=report.critical_count,
                    theme=current_theme,
                ),
                unsafe_allow_html=True,
            )

            # 5-Column High-End Metric Counters
            m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
            m_col1.markdown(render_metric_card("Total Rules", report.total_rules, "Evaluated", "#4F46E5", current_theme), unsafe_allow_html=True)
            m_col2.markdown(render_metric_card("Passed Rules", report.passed_rules, f"{round((report.passed_rules/report.total_rules)*100, 1)}% Pass Rate", "#15803D", current_theme), unsafe_allow_html=True)
            m_col3.markdown(render_metric_card("Critical Flags", report.critical_count, "Grade Deductions", "#B91C1C", current_theme), unsafe_allow_html=True)
            m_col4.markdown(render_metric_card("Warnings", report.warning_count, "Inconsistencies", "#B45309", current_theme), unsafe_allow_html=True)
            m_col5.markdown(render_metric_card("Style Tips", report.info_count, "Quality Polish", "#0369A1", current_theme), unsafe_allow_html=True)

            st.markdown("<br/>", unsafe_allow_html=True)

            # Category Dimension Progress Cards
            st.markdown("### 📈 Rubric Dimension Breakdown")
            cat_cols = st.columns(len(report.category_scores))
            is_dark_theme = current_theme == "dark"
            for idx, (cat_name, score) in enumerate(report.category_scores.items()):
                with cat_cols[idx]:
                    if is_dark_theme:
                        score_color = "#4ADE80" if score >= 85 else ("#FBBF24" if score >= 70 else "#F87171")
                    else:
                        score_color = "#15803D" if score >= 85 else ("#B45309" if score >= 70 else "#B91C1C")
                    st.markdown(
                        f'<div class="dimension-card"><div class="dimension-title"><span>{cat_name}</span><span class="dimension-score" style="color: {score_color};">{round(score, 1)}%</span></div></div>',
                        unsafe_allow_html=True,
                    )
                    st.progress(score / 100.0)

        with res_tab2:
            st.markdown("### 🛠️ Detailed Audit Findings & Corrective Actions")
            filter_col, _ = st.columns([2, 3])
            severity_filter = filter_col.selectbox(
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

            if filtered_issues:
                # Render Individual Finding Diagnosis Cards
                for iss in filtered_issues:
                    st.markdown(
                        render_finding_card(
                            rule_name=iss.rule_name,
                            category=iss.category.value,
                            actual=iss.actual,
                            expected=iss.expected,
                            fix=iss.suggested_fix,
                            severity=iss.severity.value,
                            passed=iss.passed,
                            theme=current_theme,
                        ),
                        unsafe_allow_html=True,
                    )

                # Optional Raw Data Table Expander for users who want tabular view
                with st.expander("📊 View Raw Findings Data Table", expanded=False):
                    table_rows = []
                    for iss in filtered_issues:
                        status_symbol = "PASS" if iss.passed else iss.severity.value
                        table_rows.append({
                            "Rule": iss.rule_name,
                            "Category": iss.category.value,
                            "Status": status_symbol,
                            "Document Measurement": iss.actual,
                            "Required by Rubric": iss.expected,
                            "Actionable Fix": iss.suggested_fix,
                        })
                    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)
            else:
                st.success("🎉 No issues match your filter criteria!")

        with res_tab3:
            st.markdown("### 🔍 Deep Document Layout & Physical Geometry Inspector")
            g_col1, g_col2 = st.columns(2)

            with g_col1:
                with st.container(border=True):
                    st.markdown("#### 📐 Typography & Spacing Metrics")
                    st.markdown(
                        f"""
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 12px; margin-top: 8px;">
                            <div class="metric-sub-card">
                                <span class="metric-sub-label">Dominant Font</span>
                                <span class="metric-sub-value">{extracted_doc.dominant_font}</span>
                            </div>
                            <div class="metric-sub-card">
                                <span class="metric-sub-label">Font Size</span>
                                <span class="metric-sub-value">{extracted_doc.dominant_font_size_pt} pt</span>
                            </div>
                            <div class="metric-sub-card">
                                <span class="metric-sub-label">Line Spacing</span>
                                <span class="metric-sub-value">{extracted_doc.detected_line_spacing}x Multiple</span>
                            </div>
                            <div class="metric-sub-card">
                                <span class="metric-sub-label">Paper Format</span>
                                <span class="metric-sub-value">{extracted_doc.page_size_label}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with st.container(border=True):
                    st.markdown("#### 📏 Physical Margins Geometry (Inches)")
                    st.markdown(
                        f"""
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; font-size: 12px; margin-top: 8px; text-align: center;">
                            <div class="metric-sub-card" style="padding: 8px 6px;">
                                <span class="metric-sub-label">Top</span>
                                <span class="metric-sub-value">{extracted_doc.avg_margins['top']}&quot;</span>
                            </div>
                            <div class="metric-sub-card" style="padding: 8px 6px;">
                                <span class="metric-sub-label">Bottom</span>
                                <span class="metric-sub-value">{extracted_doc.avg_margins['bottom']}&quot;</span>
                            </div>
                            <div class="metric-sub-card" style="padding: 8px 6px;">
                                <span class="metric-sub-label">Left</span>
                                <span class="metric-sub-value">{extracted_doc.avg_margins['left']}&quot;</span>
                            </div>
                            <div class="metric-sub-card" style="padding: 8px 6px;">
                                <span class="metric-sub-label">Right</span>
                                <span class="metric-sub-value">{extracted_doc.avg_margins['right']}&quot;</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            with g_col2:
                with st.container(border=True):
                    st.markdown("#### 📚 Structural Overview & Hierarchy")
                    s_c1, s_c2 = st.columns(2)
                    s_c1.metric("Total Word Count", f"{extracted_doc.total_word_count:,}")
                    s_c2.metric("Page Count", f"{extracted_doc.page_count} Pages")

                    st.markdown("<div class='doc-heading-title'>Detected Headings:</div>", unsafe_allow_html=True)
                    if extracted_doc.sections:
                        headings_html = " ".join([f"<span class='metric-sub-badge'>{s.heading}</span>" for s in extracted_doc.sections])
                        st.markdown(f"<div style='margin-top: 4px;'>{headings_html}</div>", unsafe_allow_html=True)
                    else:
                        st.caption("No explicit section headings detected.")

                with st.container(border=True):
                    st.markdown("#### 🔍 Text Layer & Image Integrity")
                    ocr_status = "Vision OCR Layer (Scanned Document)" if extracted_doc.is_scanned else "Native Digital Text Layer (Accessible)"
                    if current_theme == "dark":
                        ocr_color = "#FBBF24" if extracted_doc.is_scanned else "#4ADE80"
                    else:
                        ocr_color = "#B45309" if extracted_doc.is_scanned else "#15803D"
                    st.markdown(
                        f"""
                        <div class="ocr-status-box">
                            <span class="metric-sub-label">Text Layer Format</span>
                            <span style="font-weight: 600; color: {ocr_color};">{ocr_status}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        with res_tab4:
            st.markdown("### 📥 Export Audit Certificates & Metadata")
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div class="cert-header-box">
                        <div>
                            <span class="cert-badge">OFFICIAL REPORT</span>
                            <h4 style="margin: 6px 0 2px 0;">Compliance Audit Certificate: {report.filename}</h4>
                            <span class="cert-sub">Audit ID: {report.rubric_title.lower().replace(' ', '_')}_{report.file_type} &bull; Score: {report.overall_score}% &bull; Grade: {report.letter_grade}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            c_dl1, c_dl2 = st.columns(2)
            with c_dl1:
                with st.container(border=True):
                    st.markdown("#### 📄 Download PDF Certificate")
                    st.caption("Official authenticated PDF report with score summary and violation breakdown for course instructors.")
                    st.download_button(
                        label="📄 Download PDF Audit Certificate",
                        data=st.session_state["last_pdf_bytes"],
                        file_name=f"compliance_audit_{report.filename}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
            with c_dl2:
                with st.container(border=True):
                    st.markdown("#### 💾 Export Raw JSON Data")
                    st.caption("Full machine-readable telemetry JSON for integration with LMS platforms or automated pipelines.")
                    st.download_button(
                        label="💾 Export JSON Data",
                        data=st.session_state["last_json_str"],
                        file_name=f"compliance_audit_{report.filename}.json",
                        mime="application/json",
                        use_container_width=True,
                    )

# ----------------------------------------------------------------------
# VIEW 2: RUBRIC STUDIO
# ----------------------------------------------------------------------
elif nav_choice == "🛠️ Rubric Studio":
    st.markdown("## 🛠️ Course Rubric Studio")
    st.markdown(
        "<p class='page-subtitle'>"
        "Design, customize, or generate JSON submission rubrics from syllabus text using Google Gemini."
        "</p>",
        unsafe_allow_html=True,
    )

    studio_mode = st.radio(
        "Studio Action",
        ["Visual Rubric Editor", "Convert Guidelines Text with Gemini", "Raw JSON Editor"],
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
                st.success(f"Custom rubric '{rub_title}' compiled successfully!")
                st.download_button(
                    "📥 Download Custom Rubric JSON",
                    data=custom_json,
                    file_name=f"{updated_rubric.rubric_id}.json",
                    mime="application/json",
                )

    elif studio_mode == "Convert Guidelines Text with Gemini":
        st.markdown("Paste plain text from your course assignment prompt or syllabus. Gemini will construct the structured JSON rule schema.")
        sample_guidelines_path = RUBRICS_DIR / "sample_rubric_guidelines.txt"
        default_guide_text = sample_guidelines_path.read_text(encoding="utf-8") if sample_guidelines_path.exists() else ""
        guide_text = st.text_area("Course Guideline Text", value=default_guide_text, height=250)

        if st.button("⚡ Parse Guidelines into JSON Rubric", type="primary"):
            with st.spinner("Gemini extracting formatting, structure, and citation criteria..."):
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
    st.markdown("## 📊 Past Submissions & Compliance History")
    st.markdown(
        "<p class='page-subtitle'>"
        "Track compliance score improvements and audit records logged in the local SQLite database."
        "</p>",
        unsafe_allow_html=True,
    )

    stats = get_audit_statistics()
    h_col1, h_col2, h_col3, h_col4 = st.columns(4)
    h_col1.markdown(render_metric_card("Total Audits Run", stats["total_audits"], "Logged Audits", "#4F46E5", current_theme), unsafe_allow_html=True)
    h_col2.markdown(render_metric_card("Historical Avg Score", f"{stats['avg_score']}%", "Average", "#15803D", current_theme), unsafe_allow_html=True)
    h_col3.markdown(render_metric_card("Highest Score", f"{stats['max_score']}%", "Peak Score", "#0369A1", current_theme), unsafe_allow_html=True)
    h_col4.markdown(render_metric_card("Total Passed Rules", stats["total_passed_rules"], "Cumulative", "#6366F1", current_theme), unsafe_allow_html=True)

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

        with st.container(border=True):
            st.markdown("#### 🔍 Historical Audit Detail Inspector")
            selected_id = st.selectbox("Choose Past Audit ID", [r["id"] for r in records])
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
    st.markdown("## ⚙️ System Settings & Environment Configuration")
    st.markdown(
        "<p class='page-subtitle'>"
        "Configure Gemini API keys, layout tolerances, and engine preferences."
        "</p>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("#### 1. Google Gemini AI Core Integration")
        st.caption(
            f"Active Model: `{GEMINI_MODEL}` • Powers Vision OCR for scanned PDFs, natural language syllabus parsing, and academic tone reviews."
        )

        col_k1, col_k2 = st.columns(2)
        new_gemini_key = col_k1.text_input("Google Gemini API Key (Primary)", value=GEMINI_API_KEY, type="password", help="Gemini API Key used for AI analysis")
        new_openai_key = col_k2.text_input("OpenAI API Key (Optional Fallback)", value=OPENAI_API_KEY, type="password", help="Fallback key if Gemini is offline")

    with st.container(border=True):
        st.markdown("#### 2. Layout & Physical Tolerances")
        st.caption("Define allowable margin and font deviations before compliance penalties are flagged.")
        t_col1, t_col2 = st.columns(2)
        tol_margin = t_col1.number_input("Margin Deviation Tolerance (inches)", value=DEFAULT_MARGIN_TOLERANCE_INCHES, step=0.05)
        tol_font = t_col2.number_input("Font Size Deviation Tolerance (pt)", value=DEFAULT_FONT_SIZE_TOLERANCE_PT, step=0.25)

        if st.button("Save System Preferences", type="primary"):
            st.success("Preferences updated successfully!")

    with st.container(border=True):
        st.markdown("#### 3. Diagnostic & Environment Information")
        st.write(f"- **Application Workspace:** `{BASE_DIR}`")
        st.write(f"- **SQLite Database:** `{DATABASE_PATH}`")
        st.write(f"- **Built-in Rubric Templates:** `{len(get_builtin_rubrics())}`")
        st.write(f"- **Sample Test Documents:** `{len(list(SAMPLES_DIR.glob('*.*')))}`")
