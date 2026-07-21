from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.services.detector import get_available_rules
from app.services.orchestrator import process_article


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run TextCheck rewrite rules from the command line.")
    parser.add_argument("--text", help="Text to process. If omitted, stdin is used unless --input is set.")
    parser.add_argument("--input", type=Path, help="Path to a UTF-8 text file to process.")
    parser.add_argument("--output", type=Path, help="Optional path to write output. Defaults to stdout.")
    parser.add_argument(
        "--rules",
        default="all",
        help="Rule selection: all, none, or comma-separated rule ids.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format. text prints suggested text; json prints full line results.",
    )
    parser.add_argument("--list-rules", action="store_true", help="List available rule ids and exit.")
    return parser.parse_args()


def _read_text(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    if args.input is not None:
        return args.input.read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit("No input provided. Use --text, --input, or pipe text through stdin.")


def _enabled_rule_ids(rule_selection: str) -> list[str] | None:
    available_rule_ids = {rule.id for rule in get_available_rules()}
    normalized = rule_selection.strip()
    if normalized == "all":
        return None
    if normalized == "none":
        return []

    selected = [item.strip() for item in normalized.split(",") if item.strip()]
    unknown = sorted(set(selected) - available_rule_ids)
    if unknown:
        raise SystemExit(f"Unknown rule id(s): {', '.join(unknown)}")
    return selected


def _list_rules() -> str:
    return "\n".join(f"{rule.id}\t{rule.reason}" for rule in get_available_rules())


def _suggested_text(response) -> str:
    return "\n".join(line.suggested_text for line in response.lines)


def main() -> None:
    args = _parse_args()
    if args.list_rules:
        output = _list_rules()
    else:
        text = _read_text(args)
        response = process_article(text, _enabled_rule_ids(args.rules))
        output = (
            json.dumps(response.model_dump(), ensure_ascii=False, indent=2)
            if args.format == "json"
            else _suggested_text(response)
        )

    if args.output is not None:
        args.output.write_text(output, encoding="utf-8")
        return
    print(output)


if __name__ == "__main__":
    main()
