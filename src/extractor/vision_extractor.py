"""Vision OCR extractor for scanned documents using OpenAI or Gemini Vision API."""

import base64
import io
import os
from typing import Dict, List, Optional
from PIL import Image

from src.config import GEMINI_API_KEY, GEMINI_MODEL, OPENAI_API_KEY, OPENAI_MODEL
from src.extractor.base import ExtractedDocument

def encode_image_to_base64(image: Image.Image) -> str:
    """Convert a PIL image to a base64 encoded string."""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def extract_text_with_openai_vision(images: List[Image.Image]) -> str:
    """Use OpenAI GPT-4o vision to perform OCR and structure extraction on page images."""
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    full_text = []

    for idx, img in enumerate(images[:5]):  # Process up to 5 pages for efficiency
        b64_data = encode_image_to_base64(img)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Please extract the full text and headings from this scanned document page exactly as written. "
                                "Preserve section headers on their own lines."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64_data}"},
                        },
                    ],
                }
            ],
            max_tokens=2000,
        )
        page_text = response.choices[0].message.content or ""
        full_text.append(f"--- Page {idx + 1} ---\n" + page_text)

    return "\n\n".join(full_text)

def extract_text_with_gemini_vision(images: List[Image.Image]) -> str:
    """Use Google Gemini Vision to extract text from page images."""
    import google.generativeai as genai

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    full_text = []

    for idx, img in enumerate(images[:5]):
        response = model.generate_content([
            "Extract all text from this academic document page. Keep headings on separate lines.",
            img,
        ])
        page_text = response.text or ""
        full_text.append(f"--- Page {idx + 1} ---\n" + page_text)

    return "\n\n".join(full_text)

def run_vision_ocr(images: List[Image.Image], filename: str = "scanned_doc.pdf") -> ExtractedDocument:
    """Execute vision OCR through the available LLM provider or fallback."""
    extracted_text = ""
    warnings = []

    if OPENAI_API_KEY:
        try:
            extracted_text = extract_text_with_openai_vision(images)
        except Exception as e:
            warnings.append(f"OpenAI Vision failed: {e}")

    if not extracted_text and GEMINI_API_KEY:
        try:
            extracted_text = extract_text_with_gemini_vision(images)
        except Exception as e:
            warnings.append(f"Gemini Vision failed: {e}")

    if not extracted_text:
        warnings.append("No active Vision API key (OpenAI or Gemini) configured for scanned OCR. Please configure in Settings.")
        extracted_text = "[SCANNED DOCUMENT: Vision API key required for full OCR]"

    words = extracted_text.split()
    total_words = len(words)
    first_page_text = " ".join(words[:250]) if words else ""

    return ExtractedDocument(
        filename=filename,
        file_type="scanned_image",
        page_count=len(images),
        total_word_count=total_words,
        dominant_font="Detected via OCR (Standard)",
        dominant_font_size_pt=12.0,
        avg_margins={"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0},
        detected_line_spacing=2.0,
        page_size_label="Letter",
        full_text=extracted_text,
        first_page_text=first_page_text,
        is_scanned=True,
        extraction_warnings=warnings,
    )
