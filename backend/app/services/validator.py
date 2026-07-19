import re


PROTECTED_WORDS = ["不能", "不会", "不得", "不应", "必须", "只能", "至少", "最多", "禁止"]


def validate_rewrite(original: str, rewritten: str) -> bool:
    if not rewritten.strip():
        return False

    for word in PROTECTED_WORDS:
        if word in original and word not in rewritten:
            return False

    numbers = re.findall(r"\d+(?:\.\d+)?%?", original)
    for number in numbers:
        if number not in rewritten:
            return False

    if len(original) > 0:
        change_ratio = abs(len(original) - len(rewritten)) / len(original)
        if change_ratio > 0.75:
            return False

    if len(original) >= 20 and len(rewritten.strip()) < 6:
        return False

    return True
