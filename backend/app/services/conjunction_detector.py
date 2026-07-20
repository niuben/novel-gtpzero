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
    "故而": "所以",
    "与": "和",
    "和": "、"
}

SAFE_PREFIX_DELETIONS = [
    "不可否认的是",
    "值得注意的是",
    "需要指出的是",
    "但",
    "因为",
    "所以",
]

TOKEN_PATTERN = re.compile(
    "|".join(
        re.escape(word)
        for word in sorted([*REPLACEMENTS.keys(), *SAFE_PREFIX_DELETIONS], key=len, reverse=True)
    )
)


@dataclass(frozen=True)
class ConjunctionHit:
    rule: Rule
    start: int
    end: int
    text: str
    replacement: str


def _without_overlaps(hits: list[ConjunctionHit]) -> list[ConjunctionHit]:
    selected: list[ConjunctionHit] = []
    occupied: list[range] = []

    for hit in sorted(hits, key=lambda item: (item.start, -(item.end - item.start), not item.replacement)):
        if any(hit.start < item.stop and hit.end > item.start for item in occupied):
            continue
        selected.append(hit)
        occupied.append(range(hit.start, hit.end))

    return sorted(selected, key=lambda item: item.start)


def detect_logical_conjunctions(text: str) -> list[ConjunctionHit]:
    hits: list[ConjunctionHit] = []
    for item in TOKEN_PATTERN.finditer(text):
        word = item.group(0)
        if word in SAFE_PREFIX_DELETIONS and text[: item.start()].strip(" ，,。！？!?；;：:"):
            continue

        hits.append(
            ConjunctionHit(
                rule=CONJUNCTION_RULE,
                start=item.start(),
                end=item.end(),
                text=word,
                replacement=REPLACEMENTS.get(word, ""),
            )
        )

    return _without_overlaps(hits)
