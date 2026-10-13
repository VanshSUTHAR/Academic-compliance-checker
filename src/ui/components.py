"""Streamlit UI visual styling components with Dark & Light theme engines and Pro SaaS UI designs."""

from typing import Any, Dict, List, Optional
from src.validator.base import IssueSeverity, ValidationIssue

def get_theme_css(theme: str = "dark") -> str:
    """Generate dynamic CSS variables and layout styles for Dark or Light theme."""
    is_dark = theme == "dark"

    if is_dark:
        bg_page = "#0B0F19"
        bg_card = "#161F30"
        bg_card_alt = "#1E293B"
        bg_card_border = "#2A374A"
        text_primary = "#F8FAFC"
        text_secondary = "#94A3B8"
        text_muted = "#64748B"
        accent_gradient = "linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #D946EF 100%)"
        accent_blue = "#38BDF8"
        glow_shadow = "0 8px 32px 0 rgba(0, 0, 0, 0.37)"
        card_shadow = "0 4px 20px -2px rgba(0, 0, 0, 0.4)"
        sidebar_bg = "#0F172A"
        input_bg = "#111827"
        input_border = "#374151"
        tag_pass_bg = "rgba(16, 185, 129, 0.15)"
        tag_pass_text = "#34D399"
        tag_crit_bg = "rgba(239, 68, 68, 0.15)"
        tag_crit_text = "#F87171"
        tag_warn_bg = "rgba(245, 158, 11, 0.15)"
        tag_warn_text = "#FBBF24"
        tag_info_bg = "rgba(59, 130, 246, 0.15)"
        tag_info_text = "#60A5FA"
    else:
        bg_page = "#F8FAFC"
        bg_card = "#FFFFFF"
        bg_card_alt = "#F1F5F9"
        bg_card_border = "#E2E8F0"
        text_primary = "#0F172A"
        text_secondary = "#475569"
        text_muted = "#94A3B8"
        accent_gradient = "linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #C026D3 100%)"
        accent_blue = "#0284C7"
        glow_shadow = "0 8px 30px rgba(0, 0, 0, 0.08)"
        card_shadow = "0 4px 15px -1px rgba(0, 0, 0, 0.06)"
        sidebar_bg = "#F8FAFC"
        input_bg = "#FFFFFF"
        input_border = "#CBD5E1"
        tag_pass_bg = "#DCFCE7"
        tag_pass_text = "#15803D"
        tag_crit_bg = "#FEE2E2"
        tag_crit_text = "#B91C1C"
        tag_warn_bg = "#FEF9C3"
        tag_warn_text = "#A16207"
        tag_info_bg = "#DBEAFE"
        tag_info_text = "#1D4ED8"

    return f"""
<style>
    /* Global Root & Layout */
    .stApp {{
        background-color: {bg_page} !important;
        color: {text_primary} !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}

    /* Global Text Styles */
    h1, h2, h3, h4, h5, h6 {{
        color: {text_primary} !important;
        font-weight: 700;
        letter-spacing: -0.02em;
    }}
    p, span, label, div {{
        color: {text_secondary};
    }}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid {bg_card_border} !important;
    }}
    section[data-testid="stSidebar"] .stMarkdown h1, 
    section[data-testid="stSidebar"] .stMarkdown h2, 
    section[data-testid="stSidebar"] .stMarkdown h3 {{
        color: {text_primary} !important;
    }}

    /* Hero Header */
    .hero-container {{
        background: {bg_card};
        border: 1px solid {bg_card_border};
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 28px;
        box-shadow: {card_shadow};
        position: relative;
        overflow: hidden;
    }}
    .hero-container::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: {accent_gradient};
    }}
    .hero-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.3);
        color: #818CF8 !important;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 4px 12px;
        border-radius: 9999px;
        margin-bottom: 12px;
    }}
    .hero-title {{
        font-size: 32px !important;
        font-weight: 800 !important;
        color: {text_primary} !important;
        margin: 0 0 8px 0;
        line-height: 1.2;
    }}
    .hero-gradient-text {{
        background: {accent_gradient};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .hero-subtitle {{
        font-size: 15px !important;
        color: {text_secondary} !important;
        margin: 0 0 16px 0;
        max-width: 900px;
        line-height: 1.5;
    }}
    .hero-badges-row {{
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
        margin-top: 12px;
    }}
    .hero-chip {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        font-weight: 500;
        color: {text_muted} !important;
        background: {bg_card_alt};
        padding: 5px 12px;
        border-radius: 8px;
        border: 1px solid {bg_card_border};
    }}

    /* Card Panels */
    .pro-card {{
        background: {bg_card};
        border: 1px solid {bg_card_border};
        border-radius: 14px;
        padding: 22px;
        box-shadow: {card_shadow};
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .pro-card:hover {{
        border-color: rgba(99, 102, 241, 0.4);
    }}
    .pro-card-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid {bg_card_border};
    }}
    .pro-card-header h3 {{
        font-size: 17px !important;
        margin: 0 !important;
        color: {text_primary} !important;
    }}

    /* Metric Counters */
    .metric-grid-card {{
        background: {bg_card};
        border: 1px solid {bg_card_border};
        border-radius: 12px;
        padding: 16px 18px;
        text-align: center;
        box-shadow: {card_shadow};
        position: relative;
        overflow: hidden;
    }}
    .metric-grid-card::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: {accent_gradient};
    }}
    .metric-grid-title {{
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
        color: {text_muted};
        margin-bottom: 4px;
    }}
    .metric-grid-value {{
        font-size: 30px;
        font-weight: 800;
        line-height: 1.1;
    }}

    /* Score Ring Hero */
    .score-showcase {{
        background: {bg_card};
        border: 1px solid {bg_card_border};
        border-radius: 16px;
        padding: 28px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 24px;
        box-shadow: {card_shadow};
    }}
    .score-grade-badge {{
        font-size: 26px;
        font-weight: 800;
        padding: 6px 18px;
        border-radius: 10px;
        display: inline-block;
        letter-spacing: -0.02em;
    }}

    /* Status Badges */
    .status-pill {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 11px;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }}
    .status-pass {{ background: {tag_pass_bg}; color: {tag_pass_text} !important; }}
    .status-critical {{ background: {tag_crit_bg}; color: {tag_crit_text} !important; }}
    .status-warning {{ background: {tag_warn_bg}; color: {tag_warn_text} !important; }}
    .status-info {{ background: {tag_info_bg}; color: {tag_info_text} !important; }}

    /* Findings / Issue Card */
    .issue-panel {{
        background: {bg_card};
        border: 1px solid {bg_card_border};
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
    }}
    .issue-panel-critical {{
        border-left: 5px solid #EF4444;
    }}
    .issue-panel-warning {{
        border-left: 5px solid #F59E0B;
    }}
    .issue-panel-info {{
        border-left: 5px solid #3B82F6;
    }}
    .issue-panel-pass {{
        border-left: 5px solid #10B981;
    }}

    /* Styled Buttons */
    .stButton > button {{
        background: {accent_gradient} !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-size: 14px !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
    }}

    /* File uploader styling */
    div[data-testid="stFileUploader"] {{
        background: {bg_card_alt};
        border: 2px dashed {bg_card_border};
        border-radius: 12px;
        padding: 14px;
        text-align: center;
    }}
    div[data-testid="stFileUploader"]:hover {{
        border-color: #6366F1;
    }}

    /* Expander styling */
    div[data-testid="stExpander"] {{
        background: {bg_card} !important;
        border: 1px solid {bg_card_border} !important;
        border-radius: 12px !important;
        overflow: hidden;
    }}

    /* Radio buttons & Pills */
    div[data-testid="stRadio"] > div {{
        gap: 16px;
    }}

    /* Pulse dot */
    .live-dot {{
        width: 8px;
        height: 8px;
        background: #10B981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
        0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
        70% {{ transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }}
        100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
    }}
</style>
"""

def render_hero_banner(theme: str = "dark") -> str:
    """Render the ultra-modern SaaS Hero header."""
    return f"""
    <div class="hero-container">
        <div class="hero-pill">
            <span class="live-dot"></span>
            AI-Powered Rubric Engine &bull; Pro Edition
        </div>
        <h1 class="hero-title">
            Academic &amp; Report <span class="hero-gradient-text">Compliance Checker</span>
        </h1>
        <p class="hero-subtitle">
            Automated pre-flight submission auditing engine. Eliminates avoidable grade deductions by rigorously verifying physical layout geometry, mandatory section order, in-text citation networks, and metadata before final LMS upload.
        </p>
        <div class="hero-badges-row">
            <div class="hero-chip">📐 Deterministic PDF/DOCX Geometry</div>
            <div class="hero-chip">📚 Bi-Directional Citation Cross-Check</div>
            <div class="hero-chip">⚡ Google Gemini AI Core</div>
            <div class="hero-chip">📜 Downloadable PDF Audit Certificate</div>
        </div>
    </div>
    """

def render_score_showcase(
    score: float,
    grade: str,
    total_rules: int,
    passed_rules: int,
    critical_count: int,
    theme: str = "dark",
) -> str:
    """Render the high-end circular score gauge and grade card."""
    is_dark = theme == "dark"

    if score >= 85:
        score_color = "#10B981"
        grade_bg = "rgba(16, 185, 129, 0.15)" if is_dark else "#DCFCE7"
        grade_text = "#34D399" if is_dark else "#15803D"
        status_msg = "COMPLIANT &bull; Excellent Submission Quality"
    elif score >= 70:
        score_color = "#F59E0B"
        grade_bg = "rgba(245, 158, 11, 0.15)" if is_dark else "#FEF9C3"
        grade_text = "#FBBF24" if is_dark else "#A16207"
        status_msg = "REVISION RECOMMENDED &bull; Minor Non-Compliance Flags"
    else:
        score_color = "#EF4444"
        grade_bg = "rgba(239, 68, 68, 0.15)" if is_dark else "#FEE2E2"
        grade_text = "#F87171" if is_dark else "#B91C1C"
        status_msg = "CRITICAL PENALTY RISK &bull; Immediate Action Required"

    # SVG circular progress gauge calculations
    radius = 54
    circumference = 2 * 3.14159 * radius
    stroke_dashoffset = circumference - (score / 100.0) * circumference
    track_color = "#334155" if is_dark else "#E2E8F0"

    svg_gauge = f"""
    <svg width="140" height="140" viewBox="0 0 140 140" style="transform: rotate(-90deg);">
        <circle cx="70" cy="70" r="{radius}" fill="transparent" stroke="{track_color}" stroke-width="10"></circle>
        <circle cx="70" cy="70" r="{radius}" fill="transparent" stroke="{score_color}" stroke-width="10"
                stroke-dasharray="{circumference}" stroke-dashoffset="{stroke_dashoffset}"
                stroke-linecap="round" style="transition: stroke-dashoffset 1s ease;"></circle>
    </svg>
    """

    return f"""
    <div class="score-showcase">
        <div style="display: flex; align-items: center; gap: 28px;">
            <div style="position: relative; width: 140px; height: 140px; display: flex; align-items: center; justify-content: center;">
                {svg_gauge}
                <div style="position: absolute; text-align: center;">
                    <div style="font-size: 28px; font-weight: 800; color: {score_color}; line-height: 1;">{score}%</div>
                    <div style="font-size: 11px; font-weight: 600; color: #94A3B8; text-transform: uppercase; margin-top: 2px;">Score</div>
                </div>
            </div>
            <div>
                <div style="font-size: 12px; font-weight: 700; color: {score_color}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                    {status_msg}
                </div>
                <div style="font-size: 24px; font-weight: 800; margin-bottom: 6px;">
                    Audit Compliance Grade: 
                    <span class="score-grade-badge" style="background: {grade_bg}; color: {grade_text};">
                        {grade}
                    </span>
                </div>
                <div style="font-size: 13px; color: #94A3B8;">
                    <b>{passed_rules} of {total_rules}</b> criteria satisfied. 
                    {f'<span style="color: #EF4444; font-weight: 600;">{critical_count} critical mark-loss errors found.</span>' if critical_count > 0 else '<span style="color: #10B981; font-weight: 600;">No critical formatting violations detected!</span>'}
                </div>
            </div>
        </div>
    </div>
    """

def render_metric_card(
    title: str,
    value: Any,
    subtext: str = "",
    val_color: str = "#6366F1",
    theme: str = "dark",
) -> str:
    """Render a metric card with glowing accent border."""
    return f"""
    <div class="metric-grid-card">
        <div class="metric-grid-title">{title}</div>
        <div class="metric-grid-value" style="color: {val_color};">{value}</div>
        {f'<div style="font-size: 11px; color: #94A3B8; margin-top: 4px;">{subtext}</div>' if subtext else ''}
    </div>
    """

def render_status_badge(passed: bool, severity: IssueSeverity) -> str:
    """Return HTML status badge."""
    if passed:
        return '<span class="status-pill status-pass">PASSED</span>'
    if severity == IssueSeverity.CRITICAL:
        return '<span class="status-pill status-critical">CRITICAL</span>'
    if severity == IssueSeverity.WARNING:
        return '<span class="status-pill status-warning">WARNING</span>'
    return '<span class="status-pill status-info">INFO</span>'

# Backward compatibility aliases
CUSTOM_CSS = get_theme_css("dark")

def render_score_badge(score: float, grade: str) -> str:
    """Backward compatible score banner."""
    return render_score_showcase(score, grade, 25, 20, 0, "dark")
