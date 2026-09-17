#!/usr/bin/env python3
"""Send a validated GitHub issue to Slack, continuing long reports in a thread."""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Optional


SLACK_API_URL = "https://slack.com/api/chat.postMessage"
MAX_CHUNK_SIZE = int(os.environ.get("SLACK_CHUNK_SIZE", "3500"))
MAX_ATTEMPTS = 4


def split_text(text: str, limit: int = MAX_CHUNK_SIZE) -> list[str]:
    text = (text or "").strip()

    if not text:
        return [""]

    if limit < 100:
        raise ValueError("Chunk limit must be at least 100 characters")

    chunks: list[str] = []
    current = ""

    for paragraph in text.split("\n\n"):
        candidate = paragraph if not current else f"{current}\n\n{paragraph}"

        if len(candidate) <= limit:
            current = candidate
            continue

        if current:
            chunks.append(current)

        remaining = paragraph

        while len(remaining) > limit:
            piece = remaining[:limit]
            cut = max(piece.rfind("\n"), piece.rfind(" "))

            if cut < int(limit * 0.6):
                cut = limit

            chunks.append(remaining[:cut].rstrip())
            remaining = remaining[cut:].lstrip()

        current = remaining

    if current:
        chunks.append(current)

    return chunks or [""]


def slack_post(
    token: str,
    channel: str,
    text: str,
    thread_ts: Optional[str] = None,
) -> dict:
    payload = {
        "channel": channel,
        "text": text,
        "unfurl_links": False,
        "unfurl_media": False,
    }

    if thread_ts:
        payload["thread_ts"] = thread_ts

    for attempt in range(1, MAX_ATTEMPTS + 1):
        request = urllib.request.Request(
            SLACK_API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))

            if not result.get("ok"):
                raise RuntimeError(
                    f"Slack API error: {result.get('error', 'unknown_error')}"
                )

            return result

        except urllib.error.HTTPError as exc:
            retry_after = int(exc.headers.get("Retry-After", "0") or 0)

            if exc.code == 429 and attempt < MAX_ATTEMPTS:
                time.sleep(max(retry_after, attempt))
                continue

            body = exc.read().decode("utf-8", errors="replace")

            raise RuntimeError(
                f"Slack HTTP error {exc.code}: {body}"
            ) from exc

        except urllib.error.URLError as exc:
            if attempt < MAX_ATTEMPTS:
                time.sleep(attempt)
                continue

            raise RuntimeError(
                f"Slack network error: {exc}"
            ) from exc

    raise RuntimeError("Slack delivery exhausted retries")


def main() -> None:
    token = os.environ.get("SLACK_BOT_TOKEN")
    channel_ids_raw = os.environ.get("SLACK_CHANNEL_IDS")

    if not token:
        raise RuntimeError("SLACK_BOT_TOKEN is not configured")

    if not channel_ids_raw:
        raise RuntimeError("SLACK_CHANNEL_IDS is not configured")

    channels = [
        channel.strip()
        for channel in channel_ids_raw.split(",")
        if channel.strip()
    ]

    if not channels:
        raise RuntimeError(
            "SLACK_CHANNEL_IDS contains no valid channel IDs"
        )

    if len(sys.argv) != 2:
        raise RuntimeError(
            "Usage: send_to_slack.py ISSUE_JSON"
        )

    with open(sys.argv[1], encoding="utf-8") as file:
        issue = json.load(file)

    title = (
        issue.get("title")
        or "ChatGPT Scheduled Task"
    ).strip()

    chunks = split_text(issue.get("body") or "")

    first = f"*{title}*"

    if chunks[0]:
        first += f"\n\n{chunks[0]}"

    for channel in channels:
        result = slack_post(
            token,
            channel,
            first,
        )

        root_ts = result.get("ts")

        for chunk in chunks[1:]:
            slack_post(
                token,
                channel,
                chunk,
                thread_ts=root_ts,
            )

    print(
        f"Successfully sent issue #{issue.get('number')} "
        f"to {len(channels)} channel(s) "
        f"in {len(chunks)} part(s) each."
    )


if __name__ == "__main__":
    main()
