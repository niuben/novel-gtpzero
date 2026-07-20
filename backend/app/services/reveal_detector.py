from __future__ import annotations

from dataclasses import dataclass
import re

from app.services.rules import Rule


REVEAL_RULE = Rule(
    id="delete_reveal_word",
    match="<semantic:reveal_word>",
    category="reveal_word",
    action="delete",
    risk="low",
    reason="删除揭示词，避免提前点破转折或真相",
    auto_apply=True,
    priority=120,
)

REVEAL_WORDS = [
    "后来的事证明",
    "他突然意识到",
    "她突然意识到",
    "他猛然意识到",
    "她猛然意识到",
    "他忽然意识到",
    "她忽然意识到",
    "他猛然发现",
    "她猛然发现",
    "他恍然大悟",
    "她恍然大悟",
    "他终于明白了",
    "她终于明白了",
    "他终于明白",
    "她终于明白",
    "他终于懂了",
    "她终于懂了",
    "那一刻他终于",
    "那一刻她终于",
    "没想到的事发生了",
    "原来如此",
    "原来是这样",
    "也就是说",
    "没想到",
    "想不到",
    "谁知道",
    "殊不知",
    "出人意料",
    "难怪",
    "原来",
    "竟然",
    "居然",
]

REVEAL_PATTERN = re.compile("|".join(re.escape(word) for word in sorted(REVEAL_WORDS, key=len, reverse=True)))


@dataclass(frozen=True)
class RevealHit:
    rule: Rule
    start: int
    end: int
    text: str


def detect_reveal_words(text: str) -> list[RevealHit]:
    return [
        RevealHit(rule=REVEAL_RULE, start=item.start(), end=item.end(), text=item.group(0))
        for item in REVEAL_PATTERN.finditer(text)
    ]
