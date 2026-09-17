#!/usr/bin/env python3
"""Validate that a GitHub issue is an intentional Slack relay message."""

import json
import sys


ALLOWED_PREFIXES = (
    "Chain & Wallet Compatibility | ",
    "Chain & Wallet Compatibility Report | ",
    "Chain Compatibility Alert | ",
    "ChatGPT → GitHub → Slack E2E Test",
)
MAX_BODY_CHARS = 120_000


def validate(issue: dict) -> None:
    if issue.get("pull_request"):
        raise ValueError("Pull requests cannot be relayed")

    title = (issue.get("title") or "").strip()
    body = (issue.get("body") or "").strip()
    state = issue.get("state")

    if not title.startswith(ALLOWED_PREFIXES):
        raise ValueError("Issue title is not an approved relay type")
    if state not in {"open", "closed"}:
        raise ValueError("Issue state is invalid")
    if not body:
        raise ValueError("Issue body is empty")
    if len(body) > MAX_BODY_CHARS:
        raise ValueError("Issue body is too large")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: validate_issue.py ISSUE_JSON")
    with open(sys.argv[1], encoding="utf-8") as file:
        issue = json.load(file)
    validate(issue)
    print(f"Validated relay issue #{issue.get('number', 'unknown')}")


if __name__ == "__main__":
    main()
