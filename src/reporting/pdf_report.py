"""Generate professional PDF compliance audit reports using ReportLab."""

import io
from typing import Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.validator.base import ComplianceReport, IssueSeverity

def generate_pdf_report(report: ComplianceReport) -> bytes:
    """Compile a complete compliance audit certificate into PDF bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CertTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1E293B"),
    )
    subtitle_style = ParagraphStyle(
        "CertSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748B"),
    )
    heading_style = ParagraphStyle(
        "SectionHead",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=10,
        spaceAfter=6,
    )
    cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
    )
    bold_cell_style = ParagraphStyle(
        "BoldTableCell",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("ACADEMIC COMPLIANCE AUDIT CERTIFICATE", title_style))
    story.append(Paragraph(f"Evaluation of submission against rubric: <b>{report.rubric_title}</b>", subtitle_style))
    story.append(Paragraph(f"Generated on {report.timestamp} | Document: {report.filename} ({report.file_type})", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#CBD5E1"), spaceAfter=12))

    # 2. Executive Score Card Table
    score_color = colors.HexColor("#16A34A") if report.overall_score >= 85 else colors.HexColor("#CA8A04") if report.overall_score >= 70 else colors.HexColor("#DC2626")

    score_card_data = [
        [
            Paragraph("<b>Overall Compliance Score</b>", bold_cell_style),
            Paragraph(f"<font size=16 color='{score_color.hexval()}'><b>{report.overall_score}%</b></font>", bold_cell_style),
            Paragraph("<b>Letter Grade</b>", bold_cell_style),
            Paragraph(f"<font size=16 color='{score_color.hexval()}'><b>{report.letter_grade}</b></font>", bold_cell_style),
        ],
        [
            Paragraph("<b>Passed Checks</b>", bold_cell_style),
            Paragraph(f"<font color='#16A34A'><b>{report.passed_rules} / {report.total_rules}</b></font>", cell_style),
            Paragraph("<b>Critical Violations</b>", bold_cell_style),
            Paragraph(f"<font color='#DC2626'><b>{report.critical_count}</b></font>", cell_style),
        ],
        [
            Paragraph("<b>Warnings</b>", bold_cell_style),
            Paragraph(f"<font color='#CA8A04'><b>{report.warning_count}</b></font>", cell_style),
            Paragraph("<b>Style Tips / Info</b>", bold_cell_style),
            Paragraph(f"<font color='#2563EB'><b>{report.info_count}</b></font>", cell_style),
        ],
    ]

    score_table = Table(score_card_data, colWidths=[2.0 * inch, 1.5 * inch, 1.8 * inch, 1.7 * inch])
    score_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    story.append(score_table)
    story.append(Spacer(1, 14))

    # 3. Category Breakdown Table
    story.append(Paragraph("Category Compliance Breakdown", heading_style))
    cat_table_data = [
        [
            Paragraph("<b>Category</b>", bold_cell_style),
            Paragraph("<b>Score</b>", bold_cell_style),
            Paragraph("<b>Status</b>", bold_cell_style),
        ]
    ]
    for cat_name, cat_score in report.category_scores.items():
        status_txt = "PASSED" if cat_score >= 80 else "NEEDS REVISION"
        status_color = "#16A34A" if cat_score >= 80 else "#DC2626"
        cat_table_data.append([
            Paragraph(cat_name, cell_style),
            Paragraph(f"{cat_score}%", bold_cell_style),
            Paragraph(f"<font color='{status_color}'><b>{status_txt}</b></font>", bold_cell_style),
        ])

    cat_table = Table(cat_table_data, colWidths=[3.5 * inch, 1.5 * inch, 2.0 * inch])
    cat_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 1), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ])
    )
    story.append(cat_table)
    story.append(Spacer(1, 14))

    # 4. Detailed Audit Findings Table
    story.append(Paragraph("Detailed Audit Findings & Action Items", heading_style))
    issues_table_data = [
        [
            Paragraph("<b>Rule & Category</b>", bold_cell_style),
            Paragraph("<b>Status / Severity</b>", bold_cell_style),
            Paragraph("<b>Expected vs Found</b>", bold_cell_style),
            Paragraph("<b>Recommended Action</b>", bold_cell_style),
        ]
    ]

    for iss in report.issues:
        sev_color = "#16A34A" if iss.passed else ("#DC2626" if iss.severity == IssueSeverity.CRITICAL else "#CA8A04" if iss.severity == IssueSeverity.WARNING else "#2563EB")
        status_label = "PASS" if iss.passed else iss.severity.value

        col1 = Paragraph(f"<b>{iss.rule_name}</b><br/><font color='#64748B'>{iss.category.value}</font>", cell_style)
        col2 = Paragraph(f"<font color='{sev_color}'><b>{status_label}</b></font>", bold_cell_style)
        col3 = Paragraph(f"<b>Exp:</b> {iss.expected}<br/><b>Act:</b> {iss.actual}", cell_style)
        col4 = Paragraph(iss.suggested_fix if not iss.passed else "Compliant.", cell_style)

        issues_table_data.append([col1, col2, col3, col4])

    issues_table = Table(
        issues_table_data,
        colWidths=[2.0 * inch, 1.1 * inch, 2.0 * inch, 1.9 * inch],
    )
    issues_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(issues_table)

    # Build document
    doc.build(story)
    return buffer.getvalue()
