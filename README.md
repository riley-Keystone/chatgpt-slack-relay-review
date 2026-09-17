# ChatGPT Scheduled Task → GitHub Issue → Slack Relay

> Public, sanitized, review-only snapshot. Not connected to production; contains no credentials or production data.

## Architecture

ChatGPT Scheduled Task → GitHub Issue → GitHub Actions → internal Slack App → designated private Slack channel.

## Permission boundaries

- ChatGPT GitHub access: create/search Issues in one explicitly authorized relay repository only. No repository admin, secrets access, code push, branch management, merge, or organization admin.
- GitHub Actions `GITHUB_TOKEN`: `contents: read` and `issues: write` only. No personal access token.
- Slack bot: `chat:write` only and manually invited to one designated private channel. No public posting, channel history, user data, files, or workspace admin.
- Production secrets: `SLACK_BOT_TOKEN` and `SLACK_CHANNEL_ID`, stored only as GitHub Actions secrets. No values appear here.

## Safety properties

The relay validates approved Issue-title prefixes, rejects empty/oversized content, splits long reports, retries transient Slack errors, and closes the Issue only after successful delivery. Failed Issues remain open for investigation.

The sample workflow is stored as `examples/slack-relay.yml.example`, so GitHub Actions cannot execute it in this public repository.

## Files

- `SECURITY.md` — permission matrix, threat model and review checklist
- `examples/slack-relay.yml.example` — disabled workflow example
- `scripts/send_to_slack.py` — Slack sender and message splitting
- `scripts/validate_issue.py` — relay input validation
- `tests/test_relay.py` — unit tests

## Local verification

```bash
python3 -m py_compile scripts/send_to_slack.py scripts/validate_issue.py
python3 -m unittest discover -s tests -v
```

## CTO review scope

- Whether a GitHub Issue is an acceptable lightweight queue
- Whether workflow permissions and Slack scopes are minimal
- Risk that repository writers could alter workflows consuming secrets
- Idempotency for partial Slack thread delivery
- Pinning third-party Actions to immutable commit SHAs
- Moving production secrets to a protected GitHub Environment

## Deliberately excluded

Production identifiers, Slack workspace/channel IDs, credentials, report history, internal owners/deadlines, findings, roadmap data, and enabled workflows.
