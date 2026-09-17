# Security and Review Notes

This repository is a public, sanitized snapshot for design and code review. It is not connected to the production relay and intentionally contains no production credentials, identifiers, report history, or enabled GitHub Actions workflow.

## Permission model

### ChatGPT

Intended production access is limited to the dedicated relay repository and the Issue operations required by the scheduled task:

- search/read Issues
- create Issues

ChatGPT does not need Slack credentials, repository administration, organization administration, or access to GitHub Actions secrets.

### GitHub Actions

The production workflow is intended to run with the following `GITHUB_TOKEN` permissions:

```yaml
permissions:
  contents: read
  issues: write
```

No personal access token is required.

### Slack bot

The bot is intended to use the minimum Slack scope required to post messages, currently `chat:write`, and to be manually added only to the target channel(s).

It does not require workspace administration, user management, file management, direct-message access, or broad channel-history access.

## Secret boundary

Production values for the following settings are stored only in GitHub Actions Secrets:

- `SLACK_BOT_TOKEN`
- `SLACK_CHANNEL_ID`

This public repository contains the secret names only. No production secret values, Slack workspace IDs, or channel IDs are included.

## Execution safety of this repository

The workflow sample is stored at:

`examples/slack-relay.yml.example`

It is intentionally not stored under `.github/workflows/`, so GitHub Actions cannot execute it from this public review repository.

## Current relay controls shown in this snapshot

- Issue-open event as the automatic relay trigger
- explicit `GITHUB_TOKEN` permission declaration
- approved Issue-title prefix validation
- Pull Request rejection
- empty-body rejection
- maximum Issue-body size validation
- Slack API `ok` response validation
- retry handling for rate limiting and transient network errors
- long-message splitting with follow-up chunks in a Slack thread
- Slack link/media unfurl disabled
- Issue close only after the sender process succeeds
- manual retry entry point via `workflow_dispatch`
- concurrency grouping by Issue number

## Review scope

Reviewers should focus especially on:

1. Whether a GitHub Issue is an acceptable lightweight queue and audit record.
2. Whether ChatGPT, GitHub Actions, and Slack permissions follow least privilege.
3. Whether Issue-title validation should use a stricter schema or regular expression instead of prefix matching.
4. Whether relay identity should be restricted by Issue author, trusted label, dedicated GitHub App identity, or another control.
5. Whether deterministic `report_id` metadata is needed for stronger idempotency.
6. Behavior when a multi-part Slack delivery succeeds only partially.
7. Whether retry behavior can result in duplicate Slack messages.
8. Whether repository writers could modify a production workflow to misuse Actions secrets.
9. Whether production secrets should move to a protected GitHub Environment.
10. Whether third-party Actions should be pinned to immutable commit SHAs.
11. Failure observability for scheduler failure, GitHub Actions failure, and Slack delivery failure.
12. Whether `closed = delivered` is a sufficiently strong delivery-state model.

## Deliberately excluded

This snapshot does not contain:

- production Slack tokens
- production Slack channel or workspace IDs
- enabled GitHub Actions workflows
- production Issue/report history
- internal findings or incident details
- internal owners, deadlines, or roadmap data
- private repository identifiers beyond the intentionally published review-repository reference
