from dataclasses import dataclass
import re

import jieba
import jieba.posseg as pseg

from app.services.adjective_detector import ADJECTIVE_RULE, detect_unnecessary_adjectives
from app.services.conjunction_detector import CONJUNCTION_RULE, detect_logical_conjunctions
from app.services.reveal_detector import REVEAL_RULE, detect_reveal_words
from app.services.rules import RULES, Rule, USER_DICT_WORDS


ADVERB_RULE = Rule(
    id="delete_pos_adverb",
    match="<pos:adverb>",
    category="pos_adverb",
    action="delete",
    risk="low",
    reason="删除副词，降低表达中的修饰痕迹",
    auto_apply=True,
    priority=100,
)

DEMONSTRATIVES = {"这", "那", "哪", "一", "某", "几", "两", "每"}
NEGATION_ADVERBS = {
    "不",
    "没",
    "没有",
    "未",
    "别",
    "勿",
    "莫",
    "非",
    "并不",
    "并非",
    "从未",
    "绝不",
    "决不",
    "未必",
    "不必",
    "不用",
    "无需",
    "不能",
    "不会",
    "不要",
    "不可",
    "不得",
    "不曾",
    "尚未",
}
NEGATION_PREFIXES = ("不", "没", "未", "非", "无")
NEGATION_INTENSIFIERS = {"并", "绝", "决", "从", "尚", "还"}
DEGREE_ADVERBS = {
    "太",
    "大",
    "很",
    "挺",
    "真",
    "更",
    "较",
    "最",
    "比较",
    "相当",
    "非常",
    "十分",
    "特别",
    "极其",
    "格外",
    "完全",
    "全然",
    "稍微",
    "略微",
    "有点",
    "有些",
    "过于",
    "更加",
    "越发",
    "怎么",
    "这么",
    "那么",
}
PROGRAMMATIC_RULES = [ADVERB_RULE, ADJECTIVE_RULE, REVEAL_RULE, CONJUNCTION_RULE]


for word in USER_DICT_WORDS:
    jieba.add_word(word, freq=100000)


@dataclass(frozen=True)
class Match:
    rule: Rule
    start: int
    end: int
    text: str
    replacement: str | None = None


def _is_negation_word(word: str) -> bool:
    return word in NEGATION_ADVERBS or word.startswith(NEGATION_PREFIXES)


def _has_previous_negation(segments: list[pseg.pair], position: int) -> bool:
    previous_words = [segments[index].word for index in range(max(0, position - 2), position)]
    return any(_is_negation_word(word) for word in previous_words)


def _degree_prefix(word: str) -> str:
    for degree_word in sorted(DEGREE_ADVERBS, key=len, reverse=True):
        if word.startswith(degree_word):
            return degree_word
    return ""


def _negated_degree_span(word: str) -> tuple[int, int] | None:
    for negation in sorted(NEGATION_ADVERBS, key=len, reverse=True):
        if not word.startswith(negation):
            continue
        degree_word = _degree_prefix(word[len(negation) :])
        if degree_word:
            return len(negation), len(negation) + len(degree_word)
    return None


def _detect_adverbs(text: str) -> list[Match]:
    matches: list[Match] = []
    cursor = 0
    segments = list(pseg.cut(text))

    for position, (word, flag) in enumerate(segments):
        if not word.strip():
            continue

        index = text.find(word, cursor)
        if index < 0:
            index = text.find(word)
        if index < 0:
            continue

        cursor = index + len(word)
        previous_word = segments[position - 1].word if position > 0 else ""
        next_word = segments[position + 1].word if position + 1 < len(segments) else ""
        if previous_word in DEMONSTRATIVES and len(word) > 1:
            continue

        negated_degree_span = _negated_degree_span(word)
        if negated_degree_span:
            start_offset, end_offset = negated_degree_span
            matches.append(
                Match(
                    rule=ADVERB_RULE,
                    start=index + start_offset,
                    end=index + end_offset,
                    text=text[index + start_offset : index + end_offset],
                )
            )
            continue

        if _has_previous_negation(segments, position):
            degree_word = _degree_prefix(word)
            if degree_word:
                matches.append(
                    Match(
                        rule=ADVERB_RULE,
                        start=index,
                        end=index + len(degree_word),
                        text=text[index : index + len(degree_word)],
                    )
                )
            continue

        if flag in {"d", "ad"}:
            if _is_negation_word(word):
                continue
            if word in NEGATION_INTENSIFIERS and _is_negation_word(next_word):
                continue
            end = cursor + 1 if text.startswith("地", cursor) else cursor
            matches.append(Match(rule=ADVERB_RULE, start=index, end=end, text=text[index:end]))

    return matches


def _is_rule_enabled(rule_id: str, enabled_rule_ids: set[str] | None) -> bool:
    return enabled_rule_ids is None or rule_id in enabled_rule_ids


def get_available_rules() -> list[Rule]:
    return [*PROGRAMMATIC_RULES, *RULES]


def detect_matches(text: str, enabled_rule_ids: set[str] | None = None) -> list[Match]:
    """Find configured rule matches using jieba dictionary segmentation.

    jieba gives us dictionary-aware phrase hits while the explicit offset lookup
    keeps rewrite spans deterministic.
    """
    tokens = set(jieba.cut(text, cut_all=False))
    matches: list[Match] = []
    if _is_rule_enabled(ADVERB_RULE.id, enabled_rule_ids):
        matches.extend(_detect_adverbs(text))
    if _is_rule_enabled(ADJECTIVE_RULE.id, enabled_rule_ids):
        matches.extend(
            Match(rule=item.rule, start=item.start, end=item.end, text=item.text)
            for item in detect_unnecessary_adjectives(text)
        )
    if _is_rule_enabled(REVEAL_RULE.id, enabled_rule_ids):
        matches.extend(
            Match(rule=item.rule, start=item.start, end=item.end, text=item.text)
            for item in detect_reveal_words(text)
        )
    if _is_rule_enabled(CONJUNCTION_RULE.id, enabled_rule_ids):
        matches.extend(
            Match(
                rule=item.rule,
                start=item.start,
                end=item.end,
                text=item.text,
                replacement=item.replacement,
            )
            for item in detect_logical_conjunctions(text)
        )

    for rule in RULES:
        if not _is_rule_enabled(rule.id, enabled_rule_ids):
            continue
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
