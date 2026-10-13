"""Pre-configured default rubrics for quick selection."""

import json
from pathlib import Path
from typing import Dict, List
from src.config import RUBRICS_DIR
from src.rules.schema import RubricRuleSet

def get_builtin_rubrics() -> Dict[str, RubricRuleSet]:
    """Load all JSON rubrics stored in the rubrics directory."""
    rubrics: Dict[str, RubricRuleSet] = {}

    if RUBRICS_DIR.exists():
        for json_path in RUBRICS_DIR.glob("*.json"):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    rule_set = RubricRuleSet(**data)
                    rubrics[rule_set.title] = rule_set
            except Exception as e:
                print(f"Warning: could not load rubric from {json_path}: {e}")

    # Fallback to defaults if folder is empty or not yet mounted
    if not rubrics:
        apa_default = RubricRuleSet(
            rubric_id="apa_college_std",
            title="College Standard APA 7th Edition",
            description="Standard college submission rules: APA 7th, 12pt Times New Roman, 1-inch margins.",
        )
        rubrics[apa_default.title] = apa_default

    return rubrics

def get_default_rubric_names() -> List[str]:
    """Return a list of available rubric titles."""
    return list(get_builtin_rubrics().keys())

def get_rubric_by_name(title: str) -> RubricRuleSet:
    """Retrieve a rubric by its title name."""
    rubrics = get_builtin_rubrics()
    if title in rubrics:
        return rubrics[title]
    return next(iter(rubrics.values()), RubricRuleSet())
