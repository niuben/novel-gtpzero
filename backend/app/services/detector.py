from dataclasses import dataclass
import re

import jieba

from app.services.rules import RULES, Rule, USER_DICT_WORDS


for word in USER_DICT_WORDS:
    jieba.add_word(word, freq=100000)


@dataclass(frozen=True)
class Match:
    rule: Rule
    start: int
    end: int
    text: str


def detect_matches(text: str) -> list[Match]:
    """Find configured rule matches using jieba dictionary segmentation.

    jieba gives us dictionary-aware phrase hits while the explicit offset lookup
    keeps rewrite spans deterministic.
    """
    tokens = set(jieba.cut(text, cut_all=False))
    matches: list[Match] = []

    for rule in RULES:
        if rule.pattern_type == "regex":
            for item in re.finditer(rule.match, text):
                matches.append(Match(rule=rule, start=item.start(), end=item.end(), text=item.group(0)))
            continue

        if rule.match not in tokens and rule.match not in text:
            continue

        start = 0
        while True:
            index = text.find(rule.match, start)
            if index < 0:
                break
            matches.append(Match(rule=rule, start=index, end=index + len(rule.match), text=rule.match))
            start = index + len(rule.match)

    return sorted(matches, key=lambda item: (-item.rule.priority, item.start))
