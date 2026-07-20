from __future__ import annotations

from dataclasses import dataclass
import re

from app.services.rules import Rule


CONJUNCTION_RULE = Rule(
    id="edit_logical_conjunction",
    match="<semantic:logical_conjunction>",
    category="logical_conjunction",
    action="replace",
    risk="low",
    reason="替换或删除过度显性的逻辑连接词，减少 AI 式逻辑骨架",
    replacement="",
    auto_apply=True,
    priority=110,
)

REPLACEMENTS = {
    "然而": "但",
    "可是": "但",
    "但是": "但",
    "不过": "但",
    "因此": "所以",
    "因而": "所以",
    "与": "和",
}

DELETIONS = [
    "从而",
    "以致",
    "而且",
    "况且",
    "何况",
    "加之",
    "以及",
    "并",
    "及",
]

CONDITIONAL_PAIRS = [
    ("只要", "就"),
    ("如果", "那么"),
    ("一旦", "便"),
]

TOKEN_PATTERN = re.compile(
    "|".join(
        re.escape(word)
        for word in sorted([*REPLACEMENTS.keys(), *DELETIONS], key=len, reverse=True)
    )
)


@dataclass(frozen=True)
class ConjunctionHit:
    rule: Rule
    start: int
    end: int
    text: str
    replacement: str


def _find_condition_pair_hits(text: str) -> list[ConjunctionHit]:
    hits: list[ConjunctionHit] = []

    for first, second in CONDITIONAL_PAIRS:
        start = 0
        while True:
            first_index = text.find(first, start)
            if first_index < 0:
                break

            second_index = text.find(second, first_index + len(first))
            if second_index >= 0 and second_index - first_index <= 40:
                hits.append(
                    ConjunctionHit(
                        rule=CONJUNCTION_RULE,
                        start=first_index,
                        end=first_index + len(first),
                        text=first,
                        replacement="",
                    )
                )
                hits.append(
                    ConjunctionHit(
                        rule=CONJUNCTION_RULE,
                        start=second_index,
                        end=second_index + len(second),
                        text=second,
                        replacement="",
                    )
                )
                start = second_index + len(second)
                continue

            start = first_index + len(first)

    return hits


def detect_logical_conjunctions(text: str) -> list[ConjunctionHit]:
    hits = [
        ConjunctionHit(
            rule=CONJUNCTION_RULE,
            start=item.start(),
            end=item.end(),
            text=item.group(0),
            replacement=REPLACEMENTS.get(item.group(0), ""),
        )
        for item in TOKEN_PATTERN.finditer(text)
    ]
    hits.extend(_find_condition_pair_hits(text))
    return sorted(hits, key=lambda item: item.start)
