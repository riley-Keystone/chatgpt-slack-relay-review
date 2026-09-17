# ChatGPT Scheduled Task → GitHub Issue → Slack Relay

> Public, sanitized, review-only snapshot. This repository is not connected to the production relay and contains no credentials, production identifiers, production report history, or enabled workflow.

## Architecture

```text
ChatGPT Scheduled Task
        ↓
GitHub Issue
        ↓
GitHub Actions validation / relay
        ↓
Slack App
        ↓
Configured Slack channels
```

Responsibility split:

- **ChatGPT** — scheduled monitoring, analysis, report generation, and decision to create a relay Issue.
- **GitHub** — queue/audit layer, input validation, Slack API invocation, retry entry point, and delivery-state tracking.
- **Slack** — final message presentation only.

The main security boundary is intentional: ChatGPT does not hold the Slack bot token. Production Slack credentials are available only to the GitHub Actions relay layer.

## Permission boundaries

- ChatGPT GitHub access: intended to be limited to Issue search/read/create in one explicitly authorized relay repository. No repository admin, Secrets access, branch management, merge, or organization admin is required.
- GitHub Actions `GITHUB_TOKEN`: `contents: read` and `issues: write` only.
- Slack bot: intended minimum scope is `chat:write`, with the bot manually added only to required target channel(s).
- Production configuration: `SLACK_BOT_TOKEN` and `SLACK_CHANNEL_IDS` are stored only as GitHub Actions Secrets. `SLACK_CHANNEL_IDS` is a comma-separated list of channel IDs. This repository shows secret names only, never values.

## Review snapshot contents

The public files mirror the relay logic closely enough for design/security review while removing production data and execution capability:

- `SECURITY.md` — permission model, secret boundary, threat/review checklist
- `examples/slack-relay.yml.example` — sanitized, non-executable workflow example
- `scripts/send_to_slack.py` — multi-channel Slack sender, response validation, retry handling, message splitting/thread continuation
- `scripts/validate_issue.py` — Issue validation and approved-title filtering, including P0 alert titles
- `tests/test_relay.py` — representative unit tests

### Why there is no active workflow here

The workflow sample is intentionally stored as:

```text
examples/slack-relay.yml.example
```

and not under:

```text
.github/workflows/
```

Therefore GitHub Actions cannot execute the sample from this public review repository.

## Relay behavior represented by this snapshot

```text
Issue opened
    ↓
Load Issue JSON
    ↓
Validate title / state / body
    ↓
Read SLACK_CHANNEL_IDS
    ↓
Send the same report to each configured Slack channel
    ↓
If all configured channel deliveries succeed: close Issue and add delivery comment
If any delivery fails: workflow fails and Issue remains open
```

Long reports are split into smaller messages. For each channel, the first message becomes the root Slack message and remaining chunks are sent as thread replies.

The sender verifies Slack's JSON response and requires `ok=true`. HTTP 429 responses respect `Retry-After`; transient network failures are retried within a bounded attempt count.

## Local verification

```bash
python3 -m py_compile scripts/send_to_slack.py scripts/validate_issue.py
python3 -m unittest discover -s tests -v
```

## Review scope

Please review especially:

- Whether a GitHub Issue is an acceptable lightweight queue and audit record
- Whether ChatGPT, GitHub Actions, and Slack permissions are sufficiently minimal
- Whether Issue-trigger identity should be restricted by author/App identity or trusted label
- Whether prefix-based title validation should be replaced by a strict schema / regex
- Idempotency and duplicate-delivery behavior, especially after partial Slack thread or partial multi-channel delivery
- Manual retry semantics for open vs. already-completed Issues
- Slack API failure handling and delivery-state semantics
- Risk that repository writers could alter a production workflow consuming Secrets
- Pinning third-party Actions to immutable commit SHAs
- Moving production Secrets to a protected GitHub Environment
- Scheduler / Actions / Slack failure observability

## Known review points

This snapshot intentionally preserves several current design choices so they can be reviewed rather than silently hardened here:

1. Title validation currently uses `startswith()` against an allowlist rather than strict full-title matching.
2. The relay currently relies primarily on Issue state and pre-create duplicate search rather than a deterministic `report_id`.
3. A retry after partial multi-message or multi-channel Slack delivery could potentially duplicate already-delivered content.
4. The current workflow validates the Issue before checking whether it is already closed.
5. Both scheduled full-report and P0 alert title prefixes are currently accepted, but strict title/date validation is not yet enforced.
6. `actions/checkout@v4` is version-tag pinned, not immutable commit-SHA pinned.

## Deliberately excluded

- production Slack tokens
- production Slack workspace/channel IDs
- enabled GitHub Actions workflows
- production report history
- internal findings, owners, deadlines, and roadmap data
- production repository Secrets or environment values
