from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedLine:
    line_id: str
    index: int
    text: str


def parse_article(text: str) -> list[ParsedLine]:
    """Split article into editable line units.

    MVP scope: split by new lines and empty lines, preserving visible order.
    """
    lines: list[ParsedLine] = []
    for raw_line in text.splitlines():
        cleaned = raw_line.strip()
        if not cleaned:
            continue
        lines.append(
            ParsedLine(
                line_id=f"line_{len(lines) + 1}",
                index=len(lines),
                text=cleaned,
            )
        )
    return lines
