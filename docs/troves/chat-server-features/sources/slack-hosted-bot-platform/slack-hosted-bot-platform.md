---
source-id: "slack-hosted-bot-platform"
title: "Slack — Hosted Bot Platform with Bolt SDK and Threading"
type: web
url: "https://docs.slack.dev/tools/bolt-python/"
fetched: 2026-04-06T22:00:00Z
---

# Slack — Hosted Bot Platform with Bolt SDK and Threading

## Overview

Slack is the dominant hosted team chat platform. It provides a mature bot API, first-party Python SDK (Bolt for Python), native threading, and excellent mobile apps. For swain, Slack is a zero-ops chat transport — no server to run. The bot connects via Slack's API, posts to channels and threads, and the operator reads and steers from the Slack mobile app.

## Python SDK: Bolt for Python

Bolt for Python is Slack's official framework for building Slack apps. It is mature, actively maintained, and well-documented.

- **Event-driven.** The app listens for events (messages, reactions, slash commands) and responds with handlers.
- **Threading support.** Replying to a thread uses `thread_ts` (the timestamp of the parent message). The bot can post to any thread by specifying `thread_ts` on `chat.postMessage`. This maps to session-per-thread.
- **Slash commands.** The operator can type `/approve` or `/steer left` and the bot receives structured commands.
- **Interactive components.** Buttons, menus, modals. The operator can tap a button to approve an action without typing.
- **Socket Mode.** The bot connects via WebSocket instead of requiring a public HTTP endpoint. No ngrok or public server needed for development.
- **Async support.** `AsyncApp` class for asyncio-based bots.

## Pricing (as of 2026)

| Plan | Cost | Message History | Apps/Integrations | Key Limits |
|---|---|---|---|---|
| **Free** | $0 | 90 days | 10 | 1:1 calls only. Data older than 1 year deleted. |
| **Pro** | $7.25/user/month (annual) or ~$8.75 (monthly) | Unlimited | Unlimited | Full feature set for small teams. |
| **Business+** | $12.50/user/month (annual) | Unlimited | Unlimited | SAML, compliance, data retention. |
| **Enterprise Grid** | Custom (~$15+/user/month) | Unlimited | Unlimited | Multi-workspace, enterprise security. |

## Free Tier Viability

The free plan's 90-day message history is limiting but not fatal. A solo developer's recent sessions are visible. Older sessions vanish from search. The 10-app integration limit means only 10 bots/integrations total — tight if multiple projects each have bots. Data older than 1 year is deleted entirely, not just hidden. For a development tool, this is a real constraint.

The Pro plan at $7.25/month (1 user) removes all limits. This is the practical minimum for sustained use.

## Rate Limits

Slack's rate limits are generous enough for bot-driven workflows:

- **chat.postMessage** is in the "Special" tier: 1 message per second per channel, with short burst tolerance.
- **Workspace-wide** posting limit exists but is not documented precisely.
- **HTTP 429** responses include `Retry-After` headers. Bolt SDK handles retries automatically.
- **Practical limit:** ~60 messages per minute per channel. Sufficient for streaming bot output with batching.

Compared to Telegram's 20/min/group, Slack is 3x more generous per channel.

## Threading

Slack threads are opt-in. The bot creates a parent message in a channel, then posts updates as thread replies using `thread_ts`. The operator replies in the same thread.

- **Session mapping.** One parent message per session. All bot output and operator commands go in the thread. Clean.
- **Channel as project.** One channel per project.
- **Thread discovery.** Threads appear in the sidebar and can be followed. Push notifications work for thread replies.
- **Limitation.** Very long threads (hundreds of messages) get slow to load on mobile.

## Workspace Isolation

Slack workspaces provide strong isolation. Each workspace has its own users, channels, apps, and permissions. For security-sensitive work, separate workspaces prevent cross-project data leakage. Enterprise Grid adds multi-workspace management.

## Provisioning Automability

Slack app creation requires a manual step (creating the app in the Slack App Directory or via manifest). But once the app exists:
- Channels can be created via API (`conversations.create`).
- The bot can be invited to channels via API.
- OAuth tokens are issued during app installation.

A `/swain-stage` command could: verify the app is installed, create the project channel, and configure the bot. The initial app creation and workspace setup are manual.

## Security

Messages are stored on Slack's infrastructure (AWS). Slack has SOC 2, ISO 27001, and FedRAMP certifications. For enterprise use, compliance features are available on Business+ and Enterprise Grid. For a solo developer tool, the free or Pro tier security is adequate — messages are encrypted in transit and at rest.

## Migration Path

Slack has no self-hosted option. If you outgrow Slack or need data sovereignty, you must migrate to a different platform entirely. Slack provides data export (JSON format), but there is no "self-hosted Slack." This is a one-way commitment to the Slack ecosystem, unlike Zulip where Cloud and self-hosted are the same software.
