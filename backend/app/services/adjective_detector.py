from __future__ import annotations

from dataclasses import dataclass
import random

import jieba.posseg as pseg

from app.services.rules import Rule


ADJECTIVE_RULE = Rule(
    id="delete_attributive_adjective",
    match="<pos:adjective:attributive>",
    category="pos_adjective",
    action="delete",
    risk="low",
    reason="随机删除部分不必要的形容词定语，压缩修饰痕迹",
    auto_apply=True,
    priority=90,
)

DELETE_PROBABILITY = 0.5


@dataclass(frozen=True)
class AdjectiveHit:
    rule: Rule
    start: int
    end: int
    text: str


def _is_adjective(flag: str) -> bool:
    return flag.startswith("a") or flag == "z"


def detect_unnecessary_adjectives(text: str) -> list[AdjectiveHit]:
    candidates: list[AdjectiveHit] = []
    cursor = 0

    for word, flag in pseg.cut(text):
        if not word.strip():
            continue

        index = text.find(word, cursor)
        if index < 0:
            index = text.find(word)
        if index < 0:
            continue

        cursor = index + len(word)
        if not _is_adjective(flag):
            continue

        # First pass only removes attributive adjectives, not predicate adjectives.
        if not text.startswith("的", cursor):
            continue

        end = cursor + 1
        candidates.append(AdjectiveHit(rule=ADJECTIVE_RULE, start=index, end=end, text=text[index:end]))

    if len(candidates) <= 1:
        return candidates if candidates and random.random() < DELETE_PROBABILITY else []

    hits = [item for item in candidates if random.random() < DELETE_PROBABILITY]
    if len(hits) == len(candidates):
        hits.remove(random.choice(hits))

    return hits
