from app.models.schemas import ProcessResponse
from app.services.parser import parse_article
from app.services.rewriter import rewrite_line


def process_article(text: str, enabled_rule_ids: list[str] | None = None) -> ProcessResponse:
    parsed_lines = parse_article(text)
    enabled_rule_set = set(enabled_rule_ids) if enabled_rule_ids is not None else None
    lines = [rewrite_line(line, enabled_rule_set) for line in parsed_lines]
    return ProcessResponse(lines=lines, final_text="\n".join(line.final_text for line in lines))
