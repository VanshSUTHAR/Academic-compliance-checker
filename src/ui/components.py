"""Streamlit UI visual styling components, CSS styles, and badges."""

CUSTOM_CSS = """
<style>
    /* Global modern clean font styling */
    .compliance-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        color: white;
        padding: 24px 32px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .compliance-header h1 {
        color: #F8FAFC !important;
        font-size: 28px;
        font-weight: 700;
        margin: 0 0 8px 0;
    }
    .compliance-header p {
        color: #94A3B8 !important;
        font-size: 14px;
        margin: 0;
    }

    /* Metric Cards */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-card-title {
        font-size: 12px;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .metric-card-val {
        font-size: 28px;
        font-weight: 700;
        color: #0F172A;
    }

    /* Score Badges */
    .badge-pass {
        background-color: #DCFCE7;
        color: #15803D;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 12px;
        display: inline-block;
    }
    .badge-critical {
        background-color: #FEE2E2;
        color: #B91C1C;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 12px;
        display: inline-block;
    }
    .badge-warning {
        background-color: #FEF9C3;
        color: #A16207;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 12px;
        display: inline-block;
    }
    .badge-info {
        background-color: #DBEAFE;
        color: #1D4ED8;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 12px;
        display: inline-block;
    }

    /* Score Ring Card */
    .score-banner {
        border-radius: 12px;
        padding: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .score-banner-high {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border: 1px solid #86EFAC;
    }
    .score-banner-mid {
        background: linear-gradient(135deg, #FEFCE8 0%, #FEF08A 100%);
        border: 1px solid #FDE047;
    }
    .score-banner-low {
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
        border: 1px solid #FCA5A5;
    }

    /* Action item cards */
    .issue-card {
        background: #FFFFFF;
        border-left: 4px solid #CBD5E1;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 10px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    .issue-card-critical {
        border-left-color: #EF4444;
    }
    .issue-card-warning {
        border-left-color: #F59E0B;
    }
    .issue-card-info {
        border-left-color: #3B82F6;
    }
</style>
"""

def render_score_badge(score: float, grade: str) -> str:
    """Return HTML banner for overall compliance score."""
    if score >= 85:
        banner_cls = "score-banner-high"
        text_color = "#15803D"
        status_text = "PASSED - Excellent Compliance"
    elif score >= 70:
        banner_cls = "score-banner-mid"
        text_color = "#A16207"
        status_text = "NEEDS MINOR REVISION"
    else:
        banner_cls = "score-banner-low"
        text_color = "#B91C1C"
        status_text = "NON-COMPLIANT - Grade Risk Detected"

    return f"""
    <div class="score-banner {banner_cls}">
        <div>
            <div style="font-size: 13px; text-transform: uppercase; font-weight: 700; color: {text_color}; letter-spacing: 0.05em;">
                {status_text}
            </div>
            <div style="font-size: 36px; font-weight: 800; color: #0F172A; margin: 4px 0;">
                {score}% <span style="font-size: 24px; color: {text_color};">Grade: {grade}</span>
            </div>
            <div style="font-size: 13px; color: #475569;">
                Comprehensive verification completed across all required rubric dimensions.
            </div>
        </div>
    </div>
    """
