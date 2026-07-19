from app.models.schemas import ProcessResponse
from app.services.parser import parse_article
from app.services.rewriter import rewrite_line


def process_article(text: str) -> ProcessResponse:
    parsed_lines = parse_article(text)
    lines = [rewrite_line(line) for line in parsed_lines]
    return ProcessResponse(lines=lines, final_text="\n".join(line.final_text for line in lines))
