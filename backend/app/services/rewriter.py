import re

from app.models.schemas import Change, LineResult, Tip
from app.services.detector import Match, detect_matches
from app.services.parser import ParsedLine
from app.services.validator import validate_rewrite


def normalize_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^[，,、：:；;\s]+", "", text)
    text = re.sub(r"[，,]\s*[，,]", "，", text)
    text = re.sub(r"\s+", " ", text)
    text = text.replace("，。", "。")
    return text.strip()


def _apply_match(text: str, match: Match) -> tuple[str, Change | None]:
    rule = match.rule

    if rule.action == "delete":
        rewritten = text[: match.start] + text[match.end :]
        return rewritten, Change(
            rule_id=rule.id,
            type="delete",
            before=match.text,
            after=None,
            reason=rule.reason,
        )

    if rule.action == "replace" and (rule.replacement is not None or match.replacement is not None):
        replacement = match.replacement if match.replacement is not None else rule.replacement
        if replacement is None:
            return text, None
        if rule.pattern_type == "regex" and match.replacement is None:
            replacement = re.sub(rule.match, rule.replacement, match.text, count=1)
        rewritten = text[: match.start] + replacement + text[match.end :]
        return rewritten, Change(
            rule_id=rule.id,
            type="replace",
            before=match.text,
            after=replacement,
            reason=rule.reason,
        )

    return text, None


def _without_overlaps(matches: list[Match]) -> list[Match]:
    selected: list[Match] = []
    occupied: list[range] = []

    for match in sorted(matches, key=lambda item: (-item.rule.priority, item.start, -(item.end - item.start))):
        current = range(match.start, match.end)
        if any(match.start < item.stop and match.end > item.start for item in occupied):
            continue
        selected.append(match)
        occupied.append(current)

    return selected


def rewrite_line(line: ParsedLine, enabled_rule_ids: set[str] | None = None) -> LineResult:
    matches = detect_matches(line.text, enabled_rule_ids)
    auto_matches = _without_overlaps([item for item in matches if item.rule.auto_apply and item.rule.risk == "low"])
    tips = [
        Tip(rule_id=item.rule.id, match=item.text, message=item.rule.reason, risk=item.rule.risk)
        for item in matches
        if not item.rule.auto_apply or item.rule.action == "suggest"
    ]

    # Apply from right to left so earlier offsets remain valid.
    rewritten = line.text
    changes: list[Change] = []
    for match in sorted(auto_matches, key=lambda item: item.start, reverse=True):
        rewritten, change = _apply_match(rewritten, match)
        if change:
            changes.append(change)

    rewritten = normalize_text(rewritten)
    if rewritten != line.text and not validate_rewrite(line.text, rewritten):
        rewritten = line.text
        changes = []

    return LineResult(
        line_id=line.line_id,
        index=line.index,
        original_text=line.text,
        suggested_text=rewritten,
        final_text=line.text,
        changed=rewritten != line.text,
        changes=list(reversed(changes)),
        tips=tips,
    )
