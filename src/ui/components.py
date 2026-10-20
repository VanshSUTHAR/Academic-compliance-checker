"""Streamlit UI styling components with an Enterprise SaaS design system.

Clean, high-trust, production-ready SaaS interface inspired by Linear and Stripe.
Carefully engineered to respect Streamlit DOM, icons, and accessibility.
"""

from typing import Any, Dict, List, Optional
from src.validator.base import IssueSeverity, ValidationIssue


def get_theme_css(theme: str = "light") -> str:
    """Generate dynamic CSS variables and layout styles for Light and Dark enterprise themes."""
    is_dark = "dark" in theme.lower()

    if is_dark:
        bg_page = "#090D16"
        bg_surface = "#111827"
        bg_surface_alt = "#1A2234"
        border_subtle = "#1F293D"
        border_strong = "#374151"
        text_primary = "#F8FAFC"
        text_secondary = "#94A3B8"
        text_muted = "#64748B"
        accent_primary = "#6366F1"
        accent_hover = "#4F46E5"
        accent_subtle = "rgba(99, 102, 241, 0.12)"
        sidebar_bg = "#0B0F19"
        card_shadow = "0 1px 3px 0 rgba(0, 0, 0, 0.3)"
        elevated_shadow = "0 4px 6px -1px rgba(0, 0, 0, 0.3)"
        tag_pass_bg = "rgba(21, 128, 61, 0.16)"
        tag_pass_text = "#4ADE80"
        tag_pass_border = "rgba(34, 197, 94, 0.25)"
        tag_crit_bg = "rgba(185, 28, 28, 0.18)"
        tag_crit_text = "#F87171"
        tag_crit_border = "rgba(239, 68, 68, 0.25)"
        tag_warn_bg = "rgba(180, 83, 9, 0.18)"
        tag_warn_text = "#FBBF24"
        tag_warn_border = "rgba(245, 158, 11, 0.25)"
        tag_info_bg = "rgba(3, 105, 161, 0.18)"
        tag_info_text = "#38BDF8"
        tag_info_border = "rgba(56, 189, 248, 0.25)"
        progress_track = "#1E293B"
    else:
        # Refined Light Palette (Linear / Stripe Standard)
        bg_page = "#F8FAFC"
        bg_surface = "#FFFFFF"
        bg_surface_alt = "#F1F5F9"
        border_subtle = "#E2E8F0"
        border_strong = "#CBD5E1"
        text_primary = "#0F172A"
        text_secondary = "#475569"
        text_muted = "#64748B"
        accent_primary = "#4F46E5"
        accent_hover = "#4338CA"
        accent_subtle = "#EEF2FF"
        sidebar_bg = "#FFFFFF"
        card_shadow = "0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.05)"
        elevated_shadow = "0 4px 6px -1px rgba(15, 23, 42, 0.07), 0 2px 4px -2px rgba(15, 23, 42, 0.05)"
        tag_pass_bg = "#DCFCE7"
        tag_pass_text = "#15803D"
        tag_pass_border = "#BBF7D0"
        tag_crit_bg = "#FEE2E2"
        tag_crit_text = "#B91C1C"
        tag_crit_border = "#FECACA"
        tag_warn_bg = "#FEF3C7"
        tag_warn_text = "#B45309"
        tag_warn_border = "#FDE68A"
        tag_info_bg = "#E0F2FE"
        tag_info_text = "#0369A1"
        tag_info_border = "#BAE6FD"
        progress_track = "#E2E8F0"

    return f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">

<style>
    /* ------------------------------------------------------------- */
    /* Clean Streamlit header - keep collapse toggle functional      */
    /* ------------------------------------------------------------- */
    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}
    .stDeployButton,
    [data-testid="stStatusWidget"],
    #MainMenu, footer {{
        display: none !important;
        visibility: hidden !important;
    }}

    /* Ensure sidebar toggle buttons are always visible, styled, and clickable */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stExpandSidebarButton"] {{
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 999999 !important;
    }}

    [data-testid="stExpandSidebarButton"] button {{
        background: {bg_surface} !important;
        border: 1px solid {border_subtle} !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 5px rgba(15, 23, 42, 0.08) !important;
        cursor: pointer !important;
    }}

    [data-testid="stExpandSidebarButton"] button:hover {{
        background: {bg_surface_alt} !important;
        border-color: {accent_primary} !important;
    }}

    /* Global Typography - target explicitly without breaking icons */
    .stApp {{
        background-color: {bg_page} !important;
        color: {text_primary} !important;
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}

    /* Explicit font protection for Streamlit's Material Icons & collapse toggles */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"] *,
    [data-testid="stExpandSidebarButton"],
    [data-testid="stExpandSidebarButton"] *,
    [data-testid="collapsedControl"],
    [data-testid="collapsedControl"] *,
    [data-testid="stIconMaterial"],
    [data-testid="stExpanderToggleIcon"],
    [data-testid="stExpanderToggleIcon"] *,
    span[data-testid="stIconMaterial"],
    .material-symbols-rounded,
    .material-symbols-outlined,
    [class*="material-symbols"],
    [class*="material-icons"] {{
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
        font-feature-settings: 'liga' 1 !important;
        text-rendering: optimizeLegibility !important;
        font-weight: normal !important;
        font-style: normal !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        display: inline-block !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
        -webkit-font-smoothing: antialiased !important;
    }}

    /* Typography hierarchy */
    h1, h2, h3, h4, h5, h6 {{
        color: {text_primary} !important;
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.025em !important;
    }}

    h1 {{ font-size: 22px !important; margin-bottom: 4px !important; }}
    h2 {{ font-size: 18px !important; margin-bottom: 4px !important; }}
    h3 {{ font-size: 15px !important; margin-bottom: 4px !important; font-weight: 600 !important; }}
    h4 {{ font-size: 13px !important; font-weight: 600 !important; }}

    .stMarkdown p, .stText, label {{
        color: {text_secondary};
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
    }}

    /* Main Container Spacing */
    .block-container {{
        padding-top: 1.25rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1220px !important;
    }}

    /* Sidebar Layout & Dimensions (280-320px) */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid {border_subtle} !important;
        box-shadow: none !important;
    }}

    section[data-testid="stSidebar"][aria-expanded="true"] {{
        width: 300px !important;
        min-width: 280px !important;
        max-width: 320px !important;
    }}

    section[data-testid="stSidebar"][aria-expanded="true"] [data-testid="stSidebarContent"] {{
        width: 300px !important;
        min-width: 280px !important;
        max-width: 320px !important;
        background-color: {sidebar_bg} !important;
    }}

    section[data-testid="stSidebar"][aria-expanded="false"] {{
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        border-right: none !important;
    }}

    @media (max-width: 768px) {{
        section[data-testid="stSidebar"][aria-expanded="true"] {{
            width: min(300px, 85vw) !important;
            min-width: 0 !important;
            max-width: 85vw !important;
        }}
        section[data-testid="stSidebar"][aria-expanded="true"] [data-testid="stSidebarContent"] {{
            width: min(300px, 85vw) !important;
            min-width: 0 !important;
            max-width: 85vw !important;
        }}
    }}

    /* Balanced Sidebar Content Spacing */
    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{
        padding: 0 16px 24px 16px !important;
        overflow-x: hidden !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {{
        padding: 0.75rem 1rem 0.25rem 1rem !important;
        background-color: {sidebar_bg} !important;
    }}

    /* Sidebar Brand Header */
    .sidebar-brand {{
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        padding: 4px 0 16px 0 !important;
        margin-bottom: 12px !important;
        border-bottom: 1px solid {border_subtle} !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }}

    .sidebar-brand-icon {{
        width: 38px !important;
        height: 38px !important;
        border-radius: 10px !important;
        background: linear-gradient(135deg, {accent_primary} 0%, {accent_hover} 100%) !important;
        color: #FFFFFF !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 10px rgba(79, 70, 229, 0.25) !important;
        flex-shrink: 0 !important;
    }}

    .sidebar-brand-text {{
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        min-width: 0 !important;
        flex: 1 !important;
    }}

    .sidebar-brand-name {{
        font-size: 16px !important;
        font-weight: 800 !important;
        color: {text_primary} !important;
        letter-spacing: -0.02em !important;
        line-height: 1.2 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }}

    .sidebar-brand-sub {{
        font-size: 11px !important;
        color: {text_muted} !important;
        font-weight: 500 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        margin-top: 2px !important;
    }}

    .sidebar-section-title {{
        font-size: 10.5px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: {text_muted} !important;
        margin-bottom: 8px !important;
        margin-top: 4px !important;
        padding: 0 4px !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }}

    /* Sleek SaaS Sidebar Navigation Menu */
    section[data-testid="stSidebar"] [data-testid="stRadioOption"] input[type="radio"],
    section[data-testid="stSidebar"] [data-testid="stRadioOption"] > label > div:first-child,
    section[data-testid="stSidebar"] [data-testid="stRadioGroup"] label > div:first-child,
    section[data-testid="stSidebar"] [data-testid="stRadioOption"] div[role="radio"],
    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioButton"] {{
        display: none !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stRadio"] {{
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioGroup"] {{
        display: flex !important;
        flex-direction: column !important;
        gap: 4px !important;
        width: 100% !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stRadioOption"],
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label {{
        display: flex !important;
        align-items: center !important;
        padding: 9px 12px !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stRadioOption"]:hover,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {{
        background: {bg_surface_alt} !important;
        border-color: {border_subtle} !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stRadioOption"]:has(input:checked),
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked),
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"] {{
        background: {accent_subtle} !important;
        border: 1px solid {accent_primary} !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stRadioOption"]:has(input:checked) p,
    section[data-testid="stSidebar"] [data-testid="stRadioOption"]:has(input:checked) span,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) span,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"] p {{
        color: {accent_primary} !important;
        font-weight: 700 !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stRadioOption"] p,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label p {{
        font-size: 13.5px !important;
        font-weight: 500 !important;
        color: {text_secondary} !important;
        margin: 0 !important;
        line-height: 1.4 !important;
        white-space: nowrap !important;
    }}

    /* System Status Card */
    .sidebar-status-card {{
        background: {bg_surface_alt} !important;
        border: 1px solid {border_subtle} !important;
        border-radius: 10px !important;
        padding: 14px 16px !important;
        margin-top: 20px !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }}

    .sidebar-status-header {{
        font-size: 10px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: {text_muted} !important;
        margin-bottom: 10px !important;
    }}

    .sidebar-status-row {{
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        font-size: 12px !important;
        padding: 6px 0 !important;
        border-bottom: 1px solid {border_subtle} !important;
        gap: 8px !important;
    }}

    .sidebar-status-row:last-child {{
        border-bottom: none !important;
        padding-bottom: 2px !important;
    }}

    .sidebar-status-label {{
        color: {text_muted} !important;
        font-weight: 500 !important;
        white-space: nowrap !important;
    }}

    .sidebar-status-val {{
        font-weight: 600 !important;
        color: {text_primary} !important;
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
        white-space: nowrap !important;
    }}

    .status-indicator-dot {{
        width: 7px !important;
        height: 7px !important;
        border-radius: 50% !important;
        display: inline-block !important;
        background: #10B981 !important;
        flex-shrink: 0 !important;
    }}

    /* Application Header Bar (Modern Linear / Stripe Style) */
    .saas-header {{
        background: {bg_surface};
        border: 1px solid {border_subtle};
        border-top: 3px solid {accent_primary};
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 22px;
        box-shadow: {card_shadow};
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 16px;
    }}

    .saas-header-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 11px;
        font-weight: 600;
        color: {accent_primary} !important;
        background: {accent_subtle};
        padding: 3px 10px;
        border-radius: 6px;
        width: fit-content;
        margin-bottom: 6px;
        letter-spacing: 0.01em;
    }}

    .saas-header-title {{
        font-size: 22px !important;
        font-weight: 800 !important;
        color: {text_primary} !important;
        margin: 0 !important;
        letter-spacing: -0.03em;
        line-height: 1.25;
    }}

    .saas-header-desc {{
        font-size: 13px !important;
        color: {text_secondary} !important;
        margin: 4px 0 0 0 !important;
        max-width: 720px;
        line-height: 1.5;
    }}

    .saas-header-chips {{
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }}

    .saas-chip {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 11px;
        font-weight: 600;
        color: {text_secondary} !important;
        background: {bg_surface_alt};
        border: 1px solid {border_subtle};
        padding: 5px 10px;
        border-radius: 6px;
        transition: border-color 0.15s ease;
    }}

    /* Native Streamlit Bordered Container Overrides */
    div[data-testid="stVerticalBlock"] > div[style*="border"] {{
        background-color: {bg_surface} !important;
        border-color: {border_subtle} !important;
        border-radius: 12px !important;
        padding: 18px 20px !important;
        box-shadow: {card_shadow} !important;
    }}

    /* Streamlit Tabs */
    button[data-baseweb="tab"] {{
        font-size: 13px !important;
        font-weight: 600 !important;
        color: {text_secondary} !important;
        padding: 10px 18px !important;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {accent_primary} !important;
        border-bottom-color: {accent_primary} !important;
        border-bottom-width: 2px !important;
    }}

    /* Metric Counters */
    .metric-grid-card {{
        background: {bg_surface};
        border: 1px solid {border_subtle};
        border-radius: 10px;
        padding: 14px 16px;
        box-shadow: {card_shadow};
        transition: border-color 0.15s ease;
    }}

    .metric-grid-card:hover {{
        border-color: {border_strong};
    }}

    .metric-grid-title {{
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        color: {text_muted};
        margin-bottom: 4px;
    }}

    .metric-grid-value {{
        font-size: 26px;
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.02em;
    }}

    .metric-grid-sub {{
        font-size: 11px;
        color: {text_secondary};
        margin-top: 4px;
        font-weight: 500;
    }}

    /* Executive Score Showcase */
    .score-showcase {{
        background: {bg_surface};
        border: 1px solid {border_subtle};
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 18px;
        box-shadow: {card_shadow};
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 20px;
    }}

    .score-left-cluster {{
        display: flex;
        align-items: center;
        gap: 22px;
    }}

    .score-grade-badge {{
        font-size: 20px;
        font-weight: 800;
        padding: 4px 14px;
        border-radius: 8px;
        display: inline-block;
        letter-spacing: -0.02em;
        vertical-align: middle;
        margin-left: 6px;
    }}

    /* Status Badges */
    .status-pill {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 8px;
        border-radius: 5px;
        font-weight: 600;
        font-size: 11px;
        letter-spacing: 0.02em;
        border: 1px solid transparent;
    }}

    .status-pass {{
        background: {tag_pass_bg};
        color: {tag_pass_text} !important;
        border-color: {tag_pass_border};
    }}

    .status-critical {{
        background: {tag_crit_bg};
        color: {tag_crit_text} !important;
        border-color: {tag_crit_border};
    }}

    .status-warning {{
        background: {tag_warn_bg};
        color: {tag_warn_text} !important;
        border-color: {tag_warn_border};
    }}

    .status-info {{
        background: {tag_info_bg};
        color: {tag_info_text} !important;
        border-color: {tag_info_border};
    }}

    /* Dimension Card */
    .dimension-card {{
        background: {bg_surface};
        border: 1px solid {border_subtle};
        border-radius: 10px;
        padding: 12px 14px;
        box-shadow: {card_shadow};
    }}

    .dimension-title {{
        font-size: 12px;
        font-weight: 600;
        color: {text_primary} !important;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 6px;
    }}

    .dimension-score {{
        font-size: 13px;
        font-weight: 700;
    }}

    /* Primary Action Buttons (High contrast, crisp text) */
    button[kind="primary"],
    .stButton > button[kind="primary"],
    .stButton > button {{
        background: {accent_primary} !important;
        border: 1px solid transparent !important;
        border-radius: 8px !important;
        padding: 10px 22px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05), 0 2px 4px rgba(79, 70, 229, 0.2) !important;
        transition: all 0.15s ease !important;
    }}

    /* Ensure text inside primary button is clean, crisp white */
    button[kind="primary"] p,
    button[kind="primary"] span,
    button[kind="primary"] div,
    .stButton > button p,
    .stButton > button span,
    .stButton > button div {{
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: -0.01em !important;
    }}

    button[kind="primary"]:hover,
    .stButton > button:hover {{
        background: {accent_hover} !important;
        border-color: transparent !important;
        box-shadow: {elevated_shadow} !important;
        transform: translateY(-1px);
    }}

    button[kind="primary"]:active,
    .stButton > button:active {{
        transform: translateY(0);
    }}

    /* Secondary / Download Buttons */
    .stDownloadButton > button {{
        background: {bg_surface} !important;
        color: {text_primary} !important;
        border: 1px solid {border_strong} !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        box-shadow: {card_shadow} !important;
        transition: all 0.15s ease !important;
    }}

    .stDownloadButton > button p,
    .stDownloadButton > button span {{
        color: {text_primary} !important;
        font-weight: 600 !important;
    }}

    .stDownloadButton > button:hover {{
        background: {bg_surface_alt} !important;
        border-color: {accent_primary} !important;
    }}

    .stDownloadButton > button:hover p,
    .stDownloadButton > button:hover span {{
        color: {accent_primary} !important;
    }}

    /* Form Controls & Inputs */
    input, textarea, select {{
        border-radius: 6px !important;
    }}

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"],
    div[data-baseweb="textarea"] > div {{
        background-color: {bg_surface_alt} !important;
        color: {text_primary} !important;
        border: 1px solid {border_subtle} !important;
        border-radius: 8px !important;
        font-size: 13px !important;
    }}

    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus,
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="textarea"]:focus-within {{
        border-color: {accent_primary} !important;
        box-shadow: 0 0 0 2px {accent_subtle} !important;
    }}

    /* Stepper buttons on number inputs */
    div[data-testid="stNumberInput"] button {{
        background-color: {bg_surface} !important;
        color: {text_primary} !important;
        border: 1px solid {border_subtle} !important;
    }}

    div[data-testid="stNumberInput"] button svg {{
        fill: {text_secondary} !important;
    }}

    /* Checkbox controls */
    div[data-testid="stCheckbox"] label,
    div[data-testid="stCheckbox"] label * {{
        color: {text_primary} !important;
    }}

    /* Form Labels, Captions and Secondary Text */
    div[data-testid="stWidgetLabel"],
    div[data-testid="stWidgetLabel"] *,
    label[data-testid="stWidgetLabel"],
    label[data-testid="stWidgetLabel"] *,
    .stWidgetLabel,
    .stWidgetLabel * {{
        color: {text_primary} !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }}

    .stCaption,
    .stCaption *,
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] * {{
        color: {text_secondary} !important;
    }}

    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] label span {{
        color: {text_primary} !important;
    }}

    /* File Uploader Container & Dropzone */
    div[data-testid="stFileUploader"] {{
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }}

    [data-testid="stFileUploaderDropzone"] {{
        background-color: {bg_surface_alt} !important;
        border: 1.5px dashed {border_strong} !important;
        border-radius: 10px !important;
        padding: 16px 20px !important;
        color: {text_primary} !important;
        transition: all 0.2s ease !important;
    }}

    [data-testid="stFileUploaderDropzone"]:hover {{
        border-color: {accent_primary} !important;
        background-color: {bg_surface} !important;
    }}

    [data-testid="stFileUploaderDropzone"] button,
    [data-testid="stFileUploaderDropzone"] [data-testid="baseButton-secondary"] {{
        background-color: {bg_surface} !important;
        color: {text_primary} !important;
        border: 1px solid {border_strong} !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 6px 14px !important;
        transition: all 0.15s ease !important;
    }}

    [data-testid="stFileUploaderDropzone"] button *,
    [data-testid="stFileUploaderDropzone"] [data-testid="baseButton-secondary"] * {{
        color: {text_primary} !important;
        font-weight: 600 !important;
    }}

    [data-testid="stFileUploaderDropzone"] button:hover,
    [data-testid="stFileUploaderDropzone"] [data-testid="baseButton-secondary"]:hover {{
        background-color: {accent_subtle} !important;
        border-color: {accent_primary} !important;
    }}

    [data-testid="stFileUploaderDropzone"] button:hover *,
    [data-testid="stFileUploaderDropzone"] [data-testid="baseButton-secondary"]:hover * {{
        color: {accent_primary} !important;
    }}

    [data-testid="stFileUploaderDropzoneInstructions"],
    [data-testid="stFileUploaderDropzoneInstructions"] *,
    [data-testid="stFileUploaderDropzone"] small,
    [data-testid="stFileUploaderDropzone"] span {{
        color: {text_secondary} !important;
    }}

    [data-testid="stFileUploaderDropzone"] svg {{
        stroke: {accent_primary} !important;
    }}

    [data-testid="stFileUploaderFileName"],
    [data-testid="stFileUploaderFile"],
    [data-testid="stFileUploaderFile"] * {{
        color: {text_primary} !important;
    }}

    /* Streamlit Selectbox & BaseWeb Dropdown */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {{
        background-color: transparent !important;
    }}

    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        background-color: {bg_surface_alt} !important;
        color: {text_primary} !important;
        border: 1px solid {border_subtle} !important;
        border-radius: 8px !important;
        min-height: 40px !important;
        transition: border-color 0.15s ease !important;
    }}

    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {{
        border-color: {accent_primary} !important;
    }}

    div[data-testid="stSelectbox"] div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] span,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] div {{
        color: {text_primary} !important;
    }}

    div[data-testid="stSelectbox"] div[data-baseweb="select"] svg {{
        fill: {text_secondary} !important;
    }}

    /* Popover Menu Dropdown Options */
    div[data-baseweb="popover"],
    ul[data-baseweb="menu"],
    div[data-baseweb="popover"] > div {{
        background-color: {bg_surface} !important;
        border: 1px solid {border_subtle} !important;
        border-radius: 8px !important;
        box-shadow: {elevated_shadow} !important;
    }}

    li[data-baseweb="menu-item"],
    li[role="option"] {{
        background-color: transparent !important;
        color: {text_primary} !important;
        font-size: 13px !important;
        border-radius: 6px !important;
        margin: 2px 4px !important;
        padding: 8px 12px !important;
    }}

    li[data-baseweb="menu-item"] *,
    li[role="option"] * {{
        color: {text_primary} !important;
    }}

    li[data-baseweb="menu-item"]:hover,
    li[role="option"]:hover,
    li[data-baseweb="menu-item"][aria-selected="true"],
    li[role="option"][aria-selected="true"] {{
        background-color: {accent_subtle} !important;
        color: {accent_primary} !important;
    }}

    li[data-baseweb="menu-item"]:hover *,
    li[role="option"]:hover *,
    li[data-baseweb="menu-item"][aria-selected="true"] *,
    li[role="option"][aria-selected="true"] * {{
        color: {accent_primary} !important;
    }}

    /* Step Card Badges and Subtext */
    .step-badge {{
        background: {accent_subtle} !important;
        color: {accent_primary} !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        padding: 2px 7px !important;
        border-radius: 4px !important;
        letter-spacing: 0.05em !important;
    }}

    .step-title {{
        font-weight: 700 !important;
        font-size: 15px !important;
        color: {text_primary} !important;
    }}

    .step-sub {{
        font-size: 11px !important;
        color: {text_muted} !important;
    }}

    .subtext-hint {{
        font-size: 12px !important;
        color: {text_secondary} !important;
        margin-top: 6px !important;
    }}

    .rubric-param-box {{
        background: {bg_surface_alt} !important;
        border: 1px solid {border_subtle} !important;
        padding: 6px 10px !important;
        border-radius: 6px !important;
    }}

    .rubric-param-label {{
        color: {text_muted} !important;
        font-size: 10px !important;
        text-transform: uppercase !important;
        font-weight: 700 !important;
        display: block !important;
    }}

    .rubric-param-value {{
        font-weight: 600 !important;
        color: {text_primary} !important;
    }}

    /* Expanders */
    div[data-testid="stExpander"] {{
        background: {bg_surface} !important;
        border: 1px solid {border_subtle} !important;
        border-radius: 10px !important;
        overflow: hidden;
        margin-bottom: 12px !important;
        box-shadow: {card_shadow} !important;
    }}

    /* Progress Bar */
    .stProgress > div > div > div > div {{
        background-color: {accent_primary} !important;
        border-radius: 4px !important;
    }}

    .stProgress > div > div > div {{
        background-color: {progress_track} !important;
        border-radius: 4px !important;
        height: 6px !important;
    }}

    /* Dataframe table styling */
    div[data-testid="stDataFrame"] {{
        border: 1px solid {border_subtle} !important;
        border-radius: 8px !important;
        overflow: hidden;
    }}

    /* JSON Viewer Container */
    div[data-testid="stJson"] {{
        background-color: {bg_surface_alt} !important;
        border: 1px solid {border_subtle} !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
    }}

    /* Alerts and Notification Boxes */
    div[data-testid="stAlert"] {{
        border-radius: 8px !important;
        border: 1px solid {border_subtle} !important;
    }}

    /* Sub-metric cards for Geometry & Physical Inspector */
    .metric-sub-card {{
        background: {bg_surface_alt} !important;
        border: 1px solid {border_subtle} !important;
        padding: 8px 12px !important;
        border-radius: 6px !important;
    }}

    .metric-sub-label {{
        color: {text_muted} !important;
        font-size: 10px !important;
        text-transform: uppercase !important;
        font-weight: 700 !important;
        display: block !important;
        margin-bottom: 2px !important;
    }}

    .metric-sub-value {{
        font-weight: 600 !important;
        color: {text_primary} !important;
        font-size: 13px !important;
    }}

    .metric-sub-badge {{
        background: {accent_subtle} !important;
        color: {accent_primary} !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        padding: 3px 8px !important;
        border-radius: 4px !important;
        display: inline-block !important;
        margin: 2px !important;
    }}

    .doc-heading-title {{
        margin-top: 10px !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        color: {text_primary} !important;
    }}

    .ocr-status-box {{
        background: {bg_surface_alt} !important;
        border: 1px solid {border_subtle} !important;
        padding: 10px 14px !important;
        border-radius: 6px !important;
        font-size: 12.5px !important;
    }}

    .cert-header-box {{
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        flex-wrap: wrap !important;
        gap: 12px !important;
        margin-bottom: 12px !important;
    }}

    .cert-badge {{
        background: {accent_subtle} !important;
        color: {accent_primary} !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        padding: 3px 8px !important;
        border-radius: 4px !important;
    }}

    .cert-sub {{
        font-size: 12px !important;
        color: {text_secondary} !important;
    }}

    .page-subtitle {{
        color: {text_secondary} !important;
        font-size: 13px !important;
        margin-top: -6px !important;
        margin-bottom: 18px !important;
    }}

    hr {{
        border-color: {border_subtle} !important;
        margin: 18px 0 !important;
    }}
</style>
"""


def _clean_html(html_str: str) -> str:
    """Clean HTML string by stripping indentation and removing blank lines.

    Markdown parsers (e.g. CommonMark / Remark in Streamlit) treat any line
    indented by 4+ spaces after an empty line as a <pre><code> block.
    Removing leading whitespace and empty lines ensures the HTML block is
    rendered as raw HTML without triggering code fences or escaping.
    """
    return "\n".join(line.strip() for line in html_str.splitlines() if line.strip())


def render_hero_banner(theme: str = "light") -> str:
    """Render the enterprise application header bar."""
    html = """
    <div class="saas-header">
        <div>
            <div class="saas-header-badge">
                <span class="status-indicator-dot"></span>
                Deterministic Geometry &amp; Citation Engine &bull; Academic Enterprise
            </div>
            <h1 class="saas-header-title">
                Academic &amp; Report Compliance Checker
            </h1>
            <p class="saas-header-desc">
                Automated pre-flight submission audit engine for universities and research institutes. Rigorously verifies physical layout geometry, mandatory section order, in-text citation networks, and metadata before final submission.
            </p>
        </div>
        <div class="saas-header-chips">
            <div class="saas-chip">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#4F46E5" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>
                AST &amp; Layout Geometry
            </div>
            <div class="saas-chip">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#4F46E5" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
                Citation Verification
            </div>
            <div class="saas-chip">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#4F46E5" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
                Gemini AI Core
            </div>
            <div class="saas-chip">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#4F46E5" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                PDF Audit Certificate
            </div>
        </div>
    </div>
    """
    return _clean_html(html)


def render_score_showcase(
    score: float,
    grade: str,
    total_rules: int,
    passed_rules: int,
    critical_count: int,
    theme: str = "light",
) -> str:
    """Render the Linear/Stripe style executive scorecard and grade badge."""
    is_dark = "dark" in theme.lower()

    if score >= 85:
        score_color = "#15803D" if not is_dark else "#4ADE80"
        grade_bg = "#DCFCE7" if not is_dark else "rgba(21, 128, 61, 0.2)"
        grade_text = "#15803D" if not is_dark else "#4ADE80"
        grade_border = "#BBF7D0" if not is_dark else "rgba(34, 197, 94, 0.3)"
        status_msg = "COMPLIANT &bull; Fully Meets Rubric Standards"
    elif score >= 70:
        score_color = "#B45309" if not is_dark else "#FBBF24"
        grade_bg = "#FEF3C7" if not is_dark else "rgba(180, 83, 9, 0.2)"
        grade_text = "#B45309" if not is_dark else "#FBBF24"
        grade_border = "#FDE68A" if not is_dark else "rgba(245, 158, 11, 0.3)"
        status_msg = "REVISION RECOMMENDED &bull; Minor Non-Compliance Flags"
    else:
        score_color = "#B91C1C" if not is_dark else "#F87171"
        grade_bg = "#FEE2E2" if not is_dark else "rgba(185, 28, 28, 0.2)"
        grade_text = "#B91C1C" if not is_dark else "#F87171"
        grade_border = "#FECACA" if not is_dark else "rgba(239, 68, 68, 0.3)"
        status_msg = "PENALTY RISK &bull; Immediate Corrective Action Required"

    radius = 50
    circumference = 2 * 3.14159 * radius
    stroke_dashoffset = circumference - (score / 100.0) * circumference
    track_color = "#E2E8F0" if not is_dark else "#1E293B"

    svg_gauge = (
        f'<svg width="124" height="124" viewBox="0 0 124 124" style="transform: rotate(-90deg); flex-shrink: 0;">'
        f'<circle cx="62" cy="62" r="{radius}" fill="transparent" stroke="{track_color}" stroke-width="8"></circle>'
        f'<circle cx="62" cy="62" r="{radius}" fill="transparent" stroke="{score_color}" stroke-width="8" '
        f'stroke-dasharray="{circumference}" stroke-dashoffset="{stroke_dashoffset}" '
        f'stroke-linecap="round" style="transition: stroke-dashoffset 0.8s ease;"></circle>'
        f'</svg>'
    )

    critical_msg = (
        f'<span style="color: #B91C1C; font-weight: 600;">{critical_count} critical deduction violations identified.</span>'
        if critical_count > 0
        else '<span style="color: #15803D; font-weight: 600;">All critical formatting constraints met.</span>'
    )

    html = f"""<div class="score-showcase">
<div class="score-left-cluster">
<div style="position: relative; width: 124px; height: 124px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
{svg_gauge}
<div style="position: absolute; text-align: center;">
<div style="font-size: 24px; font-weight: 800; color: {score_color}; line-height: 1; letter-spacing: -0.02em;">{round(score, 1)}%</div>
<div style="font-size: 10px; font-weight: 600; color: #94A3B8; text-transform: uppercase; margin-top: 2px;">Score</div>
</div>
</div>
<div>
<div style="font-size: 11px; font-weight: 700; color: {score_color}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">{status_msg}</div>
<div style="font-size: 20px; font-weight: 800; margin-bottom: 6px; letter-spacing: -0.02em;">
Audit Compliance Grade: <span class="score-grade-badge" style="background: {grade_bg}; color: {grade_text}; border: 1px solid {grade_border};">{grade}</span>
</div>
<div style="font-size: 13px; color: #64748B;">Satisfied <b>{passed_rules} of {total_rules}</b> criteria. {critical_msg}</div>
</div>
</div>
</div>"""

    return _clean_html(html)


def render_metric_card(
    title: str,
    value: Any,
    subtext: str = "",
    val_color: str = "#4F46E5",
    theme: str = "light",
) -> str:
    """Render a minimal, high-trust SaaS metric card."""
    is_dark = "dark" in theme.lower()
    if is_dark:
        color_map = {
            "#4F46E5": "#818CF8",
            "#15803D": "#4ADE80",
            "#B91C1C": "#F87171",
            "#B45309": "#FBBF24",
            "#0369A1": "#38BDF8",
            "#0F172A": "#F8FAFC",
        }
        val_color = color_map.get(val_color, val_color)

    html = f"""<div class="metric-grid-card">
<div class="metric-grid-title">{title}</div>
<div class="metric-grid-value" style="color: {val_color};">{value}</div>
{f'<div class="metric-grid-sub">{subtext}</div>' if subtext else ''}
</div>"""
    return _clean_html(html)


def render_status_badge(passed: bool, severity: IssueSeverity) -> str:
    """Return an accessible, semantic HTML status badge."""
    if passed:
        return '<span class="status-pill status-pass">PASSED</span>'
    if severity == IssueSeverity.CRITICAL:
        return '<span class="status-pill status-critical">CRITICAL</span>'
    if severity == IssueSeverity.WARNING:
        return '<span class="status-pill status-warning">WARNING</span>'
    return '<span class="status-pill status-info">INFO</span>'


def render_verdict_banner(
    score: float,
    grade: str,
    critical_count: int,
    warning_count: int,
    filename: str,
    theme: str = "light",
) -> str:
    """Render an executive verdict banner indicating LMS submission readiness."""
    is_dark = "dark" in theme.lower()
    if score >= 85 and critical_count == 0:
        bg = "rgba(21, 128, 61, 0.12)" if is_dark else "#F0FDF4"
        border = "rgba(34, 197, 94, 0.3)" if is_dark else "#BBF7D0"
        title_color = "#4ADE80" if is_dark else "#15803D"
        badge_text = "READY FOR LMS SUBMISSION"
        badge_bg = "rgba(21, 128, 61, 0.25)" if is_dark else "#DCFCE7"
        badge_color = "#4ADE80" if is_dark else "#15803D"
        icon_stroke = "#4ADE80" if is_dark else "#15803D"
        desc_color = "#94A3B8" if is_dark else "#475569"
        icon_svg = f'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="{icon_stroke}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>'
        desc = f"Document <b>{filename}</b> satisfies all mandatory layout geometry, heading sequence, and citation standards. Zero mark-deduction penalties flagged."
    elif critical_count > 0:
        bg = "rgba(185, 28, 28, 0.12)" if is_dark else "#FEF2F2"
        border = "rgba(239, 68, 68, 0.3)" if is_dark else "#FECACA"
        title_color = "#F87171" if is_dark else "#B91C1C"
        badge_text = "REVISIONS REQUIRED BEFORE SUBMISSION"
        badge_bg = "rgba(185, 28, 28, 0.25)" if is_dark else "#FEE2E2"
        badge_color = "#F87171" if is_dark else "#B91C1C"
        icon_stroke = "#F87171" if is_dark else "#B91C1C"
        desc_color = "#94A3B8" if is_dark else "#475569"
        icon_svg = f'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="{icon_stroke}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>'
        desc = f"Document <b>{filename}</b> has <b>{critical_count} critical violation(s)</b> that will result in automated grade deductions. Review the action items in the findings tab below."
    else:
        bg = "rgba(180, 83, 9, 0.12)" if is_dark else "#FFFBEB"
        border = "rgba(245, 158, 11, 0.3)" if is_dark else "#FDE68A"
        title_color = "#FBBF24" if is_dark else "#B45309"
        badge_text = "MINOR REVISIONS RECOMMENDED"
        badge_bg = "rgba(180, 83, 9, 0.25)" if is_dark else "#FEF3C7"
        badge_color = "#FBBF24" if is_dark else "#B45309"
        icon_stroke = "#FBBF24" if is_dark else "#B45309"
        desc_color = "#94A3B8" if is_dark else "#475569"
        icon_svg = f'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="{icon_stroke}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>'
        desc = f"Document <b>{filename}</b> meets core requirements but has <b>{warning_count} minor formatting inconsistencies</b>. Resolving these ensures maximum submission points."

    html = f"""<div style="background: {bg}; border: 1px solid {border}; border-radius: 12px; padding: 16px 20px; margin-bottom: 20px; display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 14px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);">
<div style="display: flex; align-items: flex-start; gap: 14px;">
<div style="margin-top: 2px; flex-shrink: 0;">{icon_svg}</div>
<div>
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px; flex-wrap: wrap;">
<span style="background: {badge_bg}; color: {badge_color}; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 4px; letter-spacing: 0.04em;">{badge_text}</span>
<span style="font-weight: 800; font-size: 15px; color: {title_color};">Grade Projection: {grade} ({round(score, 1)}%)</span>
</div>
<div style="font-size: 13px; color: {desc_color}; line-height: 1.45;">{desc}</div>
</div>
</div>
</div>"""
    return _clean_html(html)


def render_finding_card(
    rule_name: str,
    category: str,
    actual: str,
    expected: str,
    fix: str,
    severity: str,
    passed: bool,
    rule_id: str = "",
    description: str = "",
    theme: str = "light",
) -> str:
    """Render a structured, high-clarity finding diagnosis card."""
    is_dark = "dark" in theme.lower()
    sev_upper = str(severity).upper()

    card_bg = "#111827" if is_dark else "#FFFFFF"
    card_border = "#1F293D" if is_dark else "#E2E8F0"
    title_color = "#F8FAFC" if is_dark else "#0F172A"
    tag_bg = "#1A2234" if is_dark else "#F1F5F9"
    tag_color = "#94A3B8" if is_dark else "#475569"
    id_color = "#94A3B8" if is_dark else "#64748B"
    desc_color = "#94A3B8" if is_dark else "#64748B"
    metric_bg = "#1A2234" if is_dark else "#F8FAFC"
    metric_border = "#1F293D" if is_dark else "#E2E8F0"
    metric_label = "#64748B" if is_dark else "#64748B"
    metric_val = "#F8FAFC" if is_dark else "#0F172A"

    if passed:
        border_color = "#10B981"
        badge_bg = "rgba(21, 128, 61, 0.2)" if is_dark else "#DCFCE7"
        badge_text = "#4ADE80" if is_dark else "#15803D"
        status_label = "✅ PASSED"
    elif "CRIT" in sev_upper:
        border_color = "#EF4444"
        badge_bg = "rgba(185, 28, 28, 0.2)" if is_dark else "#FEE2E2"
        badge_text = "#F87171" if is_dark else "#B91C1C"
        status_label = "🚨 CRITICAL PENALTY"
    elif "WARN" in sev_upper:
        border_color = "#F59E0B"
        badge_bg = "rgba(180, 83, 9, 0.2)" if is_dark else "#FEF3C7"
        badge_text = "#FBBF24" if is_dark else "#B45309"
        status_label = "⚠️ WARNING"
    else:
        border_color = "#3B82F6"
        badge_bg = "rgba(3, 105, 161, 0.2)" if is_dark else "#E0F2FE"
        badge_text = "#38BDF8" if is_dark else "#0369A1"
        status_label = "💡 QUALITY TIP"

    rule_id_html = f"<span style='background: {tag_bg}; color: {id_color}; font-size: 11px; font-weight: 600; padding: 2px 6px; border-radius: 4px; font-family: monospace;'>{rule_id}</span> " if rule_id else ""
    desc_html = f"<div style='font-size: 12px; color: {desc_color}; margin-top: 2px; margin-bottom: 10px; line-height: 1.4;'>{description}</div>" if description else ""

    fix_box_bg = "rgba(99, 102, 241, 0.12)" if is_dark else "#EEF2FF"
    fix_box_border = "rgba(99, 102, 241, 0.3)" if is_dark else "#C7D2FE"
    fix_box_title = "#818CF8" if is_dark else "#4F46E5"
    fix_box_text = "#E0E7FF" if is_dark else "#1E1B4B"

    fix_html = (
        f'<div style="margin-top: 10px; background: {fix_box_bg}; border: 1px solid {fix_box_border}; border-radius: 6px; padding: 10px 14px; font-size: 12.5px; display: flex; align-items: flex-start; gap: 8px;">'
        f'<span style="color: {fix_box_title}; font-weight: 700; white-space: nowrap;">🛠️ Actionable Fix:</span>'
        f'<span style="color: {fix_box_text}; font-weight: 500; line-height: 1.45;">{fix}</span>'
        f'</div>'
    ) if (not passed and fix) else ""

    html = f"""<div style="background: {card_bg}; border: 1px solid {card_border}; border-left: 4px solid {border_color}; border-radius: 8px; padding: 14px 16px; margin-bottom: 10px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.15);">
<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-bottom: 6px;">
<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
{rule_id_html}
<span style="font-weight: 700; font-size: 14px; color: {title_color};">{rule_name}</span>
<span style="background: {tag_bg}; color: {tag_color}; font-size: 10.5px; font-weight: 600; padding: 2px 7px; border-radius: 4px; text-transform: uppercase;">{category}</span>
</div>
<span style="background: {badge_bg}; color: {badge_text}; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 4px; letter-spacing: 0.03em;">{status_label}</span>
</div>
{desc_html}
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 12px;">
<div style="background: {metric_bg}; border: 1px solid {metric_border}; padding: 8px 12px; border-radius: 6px;">
<span style="color: {metric_label}; font-size: 10px; text-transform: uppercase; font-weight: 700; display: block; margin-bottom: 2px;">Document Measurement</span>
<span style="color: {metric_val}; font-weight: 600; font-size: 12.5px;">{actual}</span>
</div>
<div style="background: {metric_bg}; border: 1px solid {metric_border}; padding: 8px 12px; border-radius: 6px;">
<span style="color: {metric_label}; font-size: 10px; text-transform: uppercase; font-weight: 700; display: block; margin-bottom: 2px;">Required Standard</span>
<span style="color: {metric_val}; font-weight: 600; font-size: 12.5px;">{expected}</span>
</div>
</div>
{fix_html}
</div>"""
    return _clean_html(html)


def render_sidebar_brand(
    app_name: str = "Dimension",
    tagline: str = "Academic Pre-Flight Auditing",
) -> str:
    """Render the sidebar brand header with academic shield/geometry icon."""
    html = f"""<div class="sidebar-brand">
<div class="sidebar-brand-icon">
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
<path d="M12 2L2 7l10 5 10-5-10-5z"></path>
<path d="M2 17l10 5 10-5"></path>
<path d="M2 12l10 5 10-5"></path>
</svg>
</div>
<div class="sidebar-brand-text">
<div class="sidebar-brand-name">{app_name}</div>
<div class="sidebar-brand-sub">{tagline}</div>
</div>
</div>"""
    return _clean_html(html)


def render_sidebar_status_card(
    ai_status: str,
    rubrics_count: int,
    db_status: str = "SQLite Active",
    theme: str = "light",
) -> str:
    """Render the full-width high-trust system telemetry card for sidebar."""
    is_dark = "dark" in theme.lower()
    ai_color = "#818CF8" if is_dark else "#4F46E5"
    html = f"""<div class="sidebar-status-card">
<div class="sidebar-status-header">SYSTEM STATUS</div>
<div class="sidebar-status-row">
<span class="sidebar-status-label">Database</span>
<span class="sidebar-status-val"><span class="status-indicator-dot"></span>{db_status}</span>
</div>
<div class="sidebar-status-row">
<span class="sidebar-status-label">AI Engine</span>
<span class="sidebar-status-val" style="color: {ai_color};">{ai_status}</span>
</div>
<div class="sidebar-status-row">
<span class="sidebar-status-label">Rubrics Loaded</span>
<span class="sidebar-status-val">{rubrics_count} Standards</span>
</div>
</div>"""
    return _clean_html(html)


# Backward compatibility aliases
CUSTOM_CSS = get_theme_css("light")


def render_score_badge(score: float, grade: str) -> str:
    """Backward compatible score banner."""
    return render_score_showcase(score, grade, 25, 20, 0, "light")




