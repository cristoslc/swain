---
source-id: "telegram-bot-sdk-detailed"
title: "Telegram — python-telegram-bot SDK, Rate Limits, and Hosted Transport Details"
type: web
url: "https://docs.python-telegram-bot.org/en/stable/index.html"
fetched: 2026-04-06T22:00:00Z
---

# Telegram — python-telegram-bot SDK, Rate Limits, and Hosted Transport Details

## Overview

This source supplements the earlier Telegram evaluation with detailed SDK information, precise rate limit numbers, and security analysis. Telegram remains a zero-ops hosted transport where the bot posts to supergroups with forum topics enabled.

## Python SDK: python-telegram-bot

python-telegram-bot (PTB) is the dominant Python library for Telegram bots. Currently at v22.7. Mature, actively maintained, async-first since v20.0.

- **Async-native.** Built on `asyncio`. Handlers are async functions.
- **Forum topic support.** Full CRUD on forum topics via `create_forum_topic`, `edit_forum_topic`, `close_forum_topic`, `delete_forum_topic`. Messages sent to specific topics via `message_thread_id` parameter.
- **Built-in rate limiter.** `AIORateLimiter` class implements automatic rate limiting with exponential backoff. This handles the 20 msg/min/group constraint automatically.
- **Webhook and polling modes.** Webhooks (push) for production, long polling (pull) for development.
- **Inline keyboards.** Buttons on messages for structured operator commands.
- **Rich message types.** Text (Markdown/HTML), photos, documents, audio, video, stickers.
- **Conversation handlers.** State machine for multi-step interactions.

## Rate Limits (Precise)

| Scope | Limit | Notes |
|---|---|---|
| Per chat (private) | ~1 msg/second | Short bursts tolerated. |
| Per group/supergroup | 20 msg/minute | Hard limit. 429 error if exceeded. |
| Global (all chats) | ~30 msg/second | Standard bots. |
| Paid broadcast | Up to 1,000 msg/second | Requires 100K Stars balance + 100K MAU. Not relevant for swain. |
| File download | 20 MB max | Per file. |
| File upload | 50 MB max | Per file. |

The 20 msg/min/group limit is the binding constraint for swain. A bot posting every tool call and text output in a session would need to batch. At one summary message per ~3 seconds, the bot stays within limits. The `AIORateLimiter` in PTB handles this transparently.

## E2E Encryption and Security

- **Cloud-stored messages.** All group/supergroup messages are stored on Telegram's servers in plaintext (encrypted at rest, but Telegram holds the keys).
- **No E2E for groups.** Telegram's Secret Chats (E2E encrypted) are only available for 1:1 conversations, not groups or supergroups. Since swain uses supergroups, E2E encryption is not available.
- **Bot messages are never E2E.** Even in secret chats, bots cannot participate. All bot communication is server-side.
- **Privacy mode.** Bots with privacy mode enabled only receive messages that mention them or are replies to their messages. With privacy mode disabled, bots see all group messages. For swain, privacy mode should be disabled so the bot sees operator commands.
- **Account security.** Telegram accounts use phone number authentication with optional 2FA. Account compromise exposes all group messages.
- **Practical assessment.** For development session data (code output, architecture decisions, build logs), Telegram's security is adequate. It is comparable to Slack's security model. Not suitable for handling secrets, credentials, or highly classified material.

## Free Tier Viability

Telegram is completely free:

- No message limit.
- No group size limit (up to 200,000 members).
- No bot count limit.
- No storage limit for messages.
- No feature gating behind paid tiers.
- File upload limit (50 MB) is the only practical constraint.

For a solo operator with N bots across M projects, Telegram costs nothing. There is no paid tier required for any swain use case.

## Provisioning Automability

Bot creation requires one manual step: talking to @BotFather to create the bot and get the API token. After that:

- Supergroups can be created via API (`createSupergroup` in Telegram's MTProto API, not the Bot API — this is a limitation).
- Forum mode can be enabled via `toggleForum` (also MTProto only).
- Forum topics can be created via Bot API (`createForumTopic`).
- The bot can be added to groups by the operator via the Telegram UI.

**Limitation:** The Bot API cannot create groups or enable forum mode. These require either the MTProto API (more complex, requires a user account, not a bot) or manual setup by the operator. A `/swain-stage` command would need to instruct the operator to create the supergroup and enable forum mode, then the bot can handle topic creation from there.

## Migration Path

Telegram has no self-hosted version. Messages are stored on Telegram's cloud infrastructure. Telegram provides a data export tool (Telegram Desktop can export chat history as JSON/HTML), but there is no import tool for any other platform. Migration away from Telegram requires custom tooling to transform exported data into the target platform's format.

Unlike Zulip, where Cloud and self-hosted are the same software, moving from Telegram to self-hosted requires changing the entire chat adapter layer.
