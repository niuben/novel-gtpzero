from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


RuleAction = Literal["delete", "replace", "suggest"]
RiskLevel = Literal["low", "medium", "high"]
PatternType = Literal["literal", "regex"]


@dataclass(frozen=True)
class Rule:
    id: str
    match: str
    category: str
    action: RuleAction
    risk: RiskLevel
    reason: str
    replacement: str | None = None
    auto_apply: bool = False
    priority: int = 0
    pattern_type: PatternType = "literal"


VALID_ACTIONS = {"delete", "replace", "suggest"}
VALID_RISKS = {"low", "medium", "high"}
VALID_PATTERN_TYPES = {"literal", "regex"}


def _auto_apply_for(action: str, risk: str) -> bool:
    return action in {"delete", "replace"} and risk == "low"


def _load_concise_rules_file(path: Path, data: dict) -> list[Rule]:
    category = path.stem
    action = data.get("action")
    reason = data.get("reason")
    items = data.get("items")

    if action not in VALID_ACTIONS:
        raise ValueError(f"Rule file {path} has invalid or missing action: {action}")
    if not reason:
        raise ValueError(f"Rule file {path} must define reason")

    risk = data.get("risk", "low" if action in {"delete", "replace"} else "medium")
    if risk not in VALID_RISKS:
        raise ValueError(f"Rule file {path} has invalid risk: {risk}")

    pattern_type = data.get("pattern_type", "literal")
    if pattern_type not in VALID_PATTERN_TYPES:
        raise ValueError(f"Rule file {path} has invalid pattern_type: {pattern_type}")

    auto_apply = _auto_apply_for(action, risk)
    rules: list[Rule] = []

    if action == "replace":
        if not isinstance(items, dict):
            raise ValueError(f"Replace rule file {path} must define items as an object")
        iterable = list(items.items())
    else:
        if not isinstance(items, list):
            raise ValueError(f"Rule file {path} must define items as an array")
        iterable = [(item, None) for item in items]

    for index, (match, replacement) in enumerate(iterable):
        if not isinstance(match, str) or not match:
            raise ValueError(f"Rule file {path} has invalid item at index {index}")
        if action == "replace" and not isinstance(replacement, str):
            raise ValueError(f"Replace item in {path} must define string replacement: {match}")

        rules.append(
            Rule(
                id=f"{action}_{category}_{index}",
                match=match,
                category=category,
                action=action,
                risk=risk,
                reason=reason,
                replacement=replacement,
                auto_apply=auto_apply,
                pattern_type=pattern_type,
            )
        )

    return rules


def load_rules() -> list[Rule]:
    base_dir = Path(__file__).parent
    rule_files = sorted(path for path in base_dir.glob("*.json") if path.is_file())
    rules = [
        rule
        for path in rule_files
        for rule in _load_concise_rules_file(path, json.loads(path.read_text(encoding="utf-8")))
    ]

    ids = [rule.id for rule in rules]
    duplicate_ids = sorted({rule_id for rule_id in ids if ids.count(rule_id) > 1})
    if duplicate_ids:
        raise ValueError(f"Duplicate rule ids: {', '.join(duplicate_ids)}")

    return rules


RULES = load_rules()
USER_DICT_WORDS = [rule.match for rule in RULES if rule.pattern_type == "literal"]
