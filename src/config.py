"""Configuration and environment settings."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
RUBRICS_DIR = BASE_DIR / "rubrics"
SAMPLES_DIR = BASE_DIR / "samples"
DATABASE_PATH = BASE_DIR / os.getenv("DATABASE_PATH", "compliance_history.db")

# Load .env if present
load_dotenv(BASE_DIR / ".env")

# Primary LLM Configuration: Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest").strip()

# Secondary / Optional fallback: OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

# Default Tolerance Thresholds
DEFAULT_MARGIN_TOLERANCE_INCHES = float(os.getenv("DEFAULT_MARGIN_TOLERANCE_INCHES", "0.15"))
DEFAULT_FONT_SIZE_TOLERANCE_PT = float(os.getenv("DEFAULT_FONT_SIZE_TOLERANCE_PT", "0.75"))

def has_openai() -> bool:
    """Return True if an OpenAI API key is set."""
    return bool(OPENAI_API_KEY)

def has_gemini() -> bool:
    """Return True if a Gemini API key is set."""
    return bool(GEMINI_API_KEY)

def has_any_llm() -> bool:
    """Return True if at least one LLM API key is available."""
    return has_openai() or has_gemini()
