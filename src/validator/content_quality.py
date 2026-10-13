"""Content quality, clarity, and academic writing validator."""

import re
from typing import Dict, List, Set, Tuple
from src.config import GEMINI_API_KEY, GEMINI_MODEL, OPENAI_API_KEY, OPENAI_MODEL
from src.extractor.base import ExtractedDocument
from src.rules.schema import ContentQualityRules
from src.validator.base import IssueSeverity, ValidationCategory, ValidationIssue

def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences handling common abbreviations and punctuation."""
    # Replace common abbreviations to avoid false splits
    cleaned = re.sub(r"\b(e\.g\.|i\.e\.|et al\.|Dr\.|Prof\.|vs\.)", lambda m: m.group(0).replace(".", "@"), text)
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    return [s.replace("@", ".").strip() for s in sentences if s.strip()]

def review_quality_with_llm(sample_text: str) -> List[Dict[str, str]]:
    """Query LLM for qualitative writing suggestions on sample text."""
    prompt = (
        "Review this sample academic text for writing clarity, conciseness, passive voice, and tone. "
        "List up to 2 specific constructive recommendations in 1-2 sentences each.\n\n"
        f"Text excerpt:\n{sample_text[:1200]}"
    )

    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            resp = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250,
            )
            ans = resp.choices[0].message.content or ""
            return [{"aspect": "LLM Academic Tone Review", "feedback": ans}]
        except Exception:
            pass

    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(GEMINI_MODEL)
            resp = model.generate_content(prompt)
            return [{"aspect": "LLM Academic Tone Review", "feedback": resp.text or ""}]
        except Exception:
            pass

    return []

def validate_content_quality(
    doc: ExtractedDocument,
    rules: ContentQualityRules,
) -> List[ValidationIssue]:
    """Validate sentence length, vague words, lexical density, and optional LLM review."""
    issues: List[ValidationIssue] = []
    text = doc.full_text
    words = text.split()

    # 1. Vague Terminology Detection
    detected_vague: Dict[str, int] = {}
    text_lower = text.lower()

    for phrase in rules.forbidden_vague_words:
        phrase_clean = phrase.lower().strip()
        matches = len(re.findall(r"\b" + re.escape(phrase_clean) + r"\b", text_lower))
        if matches > 0:
            detected_vague[phrase] = matches

    vague_passed = len(detected_vague) == 0
    issues.append(
        ValidationIssue(
            rule_id="qual_vague_words",
            rule_name="Academic Vocabulary & Clarity",
            category=ValidationCategory.CONTENT_QUALITY,
            severity=IssueSeverity.WARNING if not vague_passed else IssueSeverity.INFO,
            passed=vague_passed,
            description="Checks for conversational, vague, or subjective expressions that undermine academic tone.",
            expected="No colloquial expressions ('things', 'stuff', 'obviously', etc.)",
            actual="Clean academic diction" if vague_passed else f"Detected: {', '.join([f'{k} (x{v})' for k, v in list(detected_vague.items())[:4]])}",
            suggested_fix="Replace colloquial terms with formal academic alternatives (e.g., 'factors', 'elements', 'evidently').",
        )
    )

    # 2. Run-On Sentences Detection
    sentences = split_into_sentences(text)
    max_len = rules.max_sentence_length_words
    run_on_count = 0
    longest_sentence_words = 0

    for s in sentences:
        s_words = len(s.split())
        if s_words > longest_sentence_words:
            longest_sentence_words = s_words
        if s_words > max_len:
            run_on_count += 1

    run_on_ratio = (run_on_count / len(sentences)) if sentences else 0.0
    run_on_passed = run_on_ratio < 0.15

    issues.append(
        ValidationIssue(
            rule_id="qual_run_on_sentences",
            rule_name="Sentence Length & Flow",
            category=ValidationCategory.CONTENT_QUALITY,
            severity=IssueSeverity.INFO if run_on_passed else IssueSeverity.WARNING,
            passed=run_on_passed,
            description=f"Identifies sentences exceeding {max_len} words that may hinder reader comprehension.",
            expected=f"Sentences ≤ {max_len} words (≤ 15% run-on tolerance)",
            actual=f"{run_on_count} long sentences ({round(run_on_ratio * 100, 1)}% of text)" if not run_on_passed else f"Well balanced ({run_on_count} sentences > {max_len} words)",
            suggested_fix=f"Break compound sentences longer than {max_len} words into distinct, concise clauses.",
        )
    )

    # 3. Lexical Diversity (Type-Token Ratio)
    if len(words) > 100:
        clean_words = [re.sub(r"[^\w]", "", w.lower()) for w in words if len(w) > 2]
        unique_words = set(clean_words)
        ttr = len(unique_words) / len(clean_words) if clean_words else 1.0
        ttr_passed = ttr >= rules.min_lexical_diversity

        issues.append(
            ValidationIssue(
                rule_id="qual_lexical_diversity",
                rule_name="Vocabulary Variety (TTR)",
                category=ValidationCategory.CONTENT_QUALITY,
                severity=IssueSeverity.INFO,
                passed=ttr_passed,
                description="Measures vocabulary repetition using the Type-Token Ratio (unique words / total words).",
                expected=f"TTR ≥ {rules.min_lexical_diversity}",
                actual=f"TTR: {round(ttr, 2)} ({len(unique_words)} unique words)",
                suggested_fix="Expand technical vocabulary variety and avoid excessive repetition of identical phrasing.",
            )
        )

    # 4. Optional LLM Qualitative Review
    if rules.enable_llm_quality_review:
        llm_feedback = review_quality_with_llm(text)
        for fb in llm_feedback:
            issues.append(
                ValidationIssue(
                    rule_id="qual_llm_review",
                    rule_name="AI Qualitative Review",
                    category=ValidationCategory.CONTENT_QUALITY,
                    severity=IssueSeverity.INFO,
                    passed=True,
                    description="Qualitative commentary on writing style, conciseness, and tone generated by LLM.",
                    expected="Academic clarity",
                    actual="AI Insights Available",
                    suggested_fix=fb["feedback"],
                )
            )

    return issues
