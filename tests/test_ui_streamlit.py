"""Frontend automated tests using Streamlit AppTest framework."""

from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")

def test_streamlit_frontend_initial_render():
    """Verify that app renders with default Dark Pro theme and no unhandled exceptions."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception, f"App encountered an exception during render: {at.exception}"

    # Verify Sidebar components
    assert len(at.sidebar.radio) >= 2
    theme_radio = at.sidebar.radio[0]
    assert "🌙 Dark Pro" in theme_radio.options
    assert "☀️ Clean Light" in theme_radio.options

    nav_radio = at.sidebar.radio[1]
    assert "🔍 Compliance Checker" in nav_radio.options
    assert "🛠️ Rubric Studio" in nav_radio.options
    assert "📊 Audit History" in nav_radio.options
    assert "⚙️ Settings" in nav_radio.options

def test_streamlit_frontend_theme_toggle():
    """Verify toggling between Dark and Light mode renders successfully."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()

    # Switch to Clean Light
    at.sidebar.radio[0].set_value("☀️ Clean Light").run()
    assert not at.exception, "Switching to Clean Light theme raised an exception"

    # Switch back to Dark Pro
    at.sidebar.radio[0].set_value("🌙 Dark Pro").run()
    assert not at.exception, "Switching back to Dark Pro theme raised an exception"

def test_streamlit_frontend_navigation_tabs():
    """Verify all navigation views render without crashing."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()

    # Rubric Studio view
    at.sidebar.radio[1].set_value("🛠️ Rubric Studio").run()
    assert not at.exception, "Rubric Studio view crashed"

    # Audit History view
    at.sidebar.radio[1].set_value("📊 Audit History").run()
    assert not at.exception, "Audit History view crashed"

    # Settings view
    at.sidebar.radio[1].set_value("⚙️ Settings").run()
    assert not at.exception, "Settings view crashed"

def test_streamlit_frontend_run_compliance_audit():
    """Simulate user selecting demo paper and triggering compliance audit."""
    at = AppTest.from_file(APP_PATH, default_timeout=45)
    at.run()

    # Select demo document: Sample Conforming Paper - PDF
    demo_selectbox = at.selectbox[1]
    demo_selectbox.set_value("Sample Conforming Paper (Passes APA) - PDF").run()
    assert not at.exception

    # Click 'Run Comprehensive Compliance Audit' button
    audit_button = at.button[0]
    audit_button.click().run()
    assert not at.exception, "Clicking compliance audit button caused an error"

    # Verify results state
    assert "last_report" in at.session_state
    report = at.session_state["last_report"]
    assert report.overall_score >= 80.0
    assert report.letter_grade in ["A", "A-", "B+", "B"]

    # Verify PDF certificate and JSON data generated in session
    assert "last_pdf_bytes" in at.session_state
    assert len(at.session_state["last_pdf_bytes"]) > 1000
    assert "last_json_str" in at.session_state
    assert '"overall_score":' in at.session_state["last_json_str"]
