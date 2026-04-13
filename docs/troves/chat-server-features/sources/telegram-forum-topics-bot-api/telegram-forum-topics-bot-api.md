---
source-id: "telegram-forum-topics-bot-api"
title: "Telegram Forum Topics and Bot API — Zero-Ops Chat Transport"
type: web
url: "https://core.telegram.org/api/forum"
fetched: 2026-04-07T06:00:00Z
---

# Telegram Forum Topics and Bot API — Zero-Ops Chat Transport

## Overview

Telegram is a hosted messaging platform with native apps on every major platform. Instead of self-hosting a chat server, you use Telegram's infrastructure and write a bot that connects via their Bot API. The ops burden shifts entirely to Telegram. You run zero servers for the chat layer.

## Forum Topics as Rooms and Threads

Since Bot API 6.3, Telegram supergroups can enable "forum mode," which adds **topics** — named sub-threads within a group. Each topic acts like a separate conversation channel within the group.

- **Topics as sessions.** A bot can create topics programmatically via `createForumTopic`. Each topic has a name, optional icon, and its own message stream. This maps to swain's "one thread per session" need.
- **Groups as projects.** One Telegram supergroup per project, with forum mode enabled. Each group contains topics for sessions. This maps to "one room per project."
- **Bot API methods.** Full CRUD on topics: `createForumTopic`, `editForumTopic`, `closeForumTopic`, `reopenForumTopic`, `deleteForumTopic`. Bots send messages to specific topics via the `message_thread_id` parameter on `sendMessage` and all other send methods.
- **General topic.** Every forum group has a non-deletable "General" topic (ID=1) that can serve as a default channel.
- **Pinned topics.** Topics can be pinned for visibility. There is a configurable limit on pinned topics per group.

## Bot API Capabilities

- **Webhooks or long polling.** The bot receives updates via webhook (push) or `getUpdates` (pull). Webhooks are the recommended production approach.
- **Message routing.** Incoming messages include `message_thread_id` so the bot knows which topic they came from.
- **Rich messages.** Bots can send text, markdown, photos, documents, inline keyboards (buttons), and more.
- **Inline keyboards.** Buttons on messages allow the operator to approve, reject, or trigger actions without typing. This is good for structured steering commands.
- **Rate limits.** Bots can send about 30 messages per second to different chats, 20 messages per minute to the same group. Sufficient for development workflows.

## Recent Improvements (2025-2026)

- Bot API 7.5 (March 2025): `has_topics_enabled` field on User class, allowing bots to detect forum mode in private chats.
- Bots can now create topics in private chats, not just group chats.
- Topic management permissions (`manage_topics` right) can be granted to bots.

## Mobile UX

Telegram's native apps on iOS and Android display forum topics as a list within the group. Tapping a topic opens its message stream. The UX is polished and familiar to hundreds of millions of users. No PWA needed — native apps with push notifications.

## Trade-Offs vs. Self-Hosting

### Advantages

1. **Zero ops burden.** No server to run, no Docker, no backups, no upgrades, no SSL certs. Telegram handles everything.
2. **Best mobile apps.** Native iOS and Android apps that already exist on most developers' phones.
3. **Push notifications built in.** No configuration needed.
4. **Rich bot API.** Full CRUD on topics, inline keyboards, markdown formatting, file attachments.
5. **Free.** No cost for bots or forum groups.
6. **Reliability.** Telegram has 99.9%+ uptime. A solo operator cannot match this with self-hosted infrastructure.

### Disadvantages

1. **Vendor dependency.** Your chat transport depends on Telegram's continued operation and policies. They could change API terms, rate limits, or features.
2. **Data sovereignty.** Messages live on Telegram's servers. Not on your machine.
3. **No self-hosted fallback.** If Telegram goes down or blocks your bot, there is no local fallback.
4. **Topic threading is flat.** Topics within a group are one level deep. No nested threads within a topic (unlike Zulip's topic+message threading).
5. **Limited customization.** You cannot customize the UI, add custom metadata to messages, or extend the protocol.
6. **Rate limits exist.** 20 messages per minute to the same group. For a bot that posts rapid-fire updates during a session, this may require batching.

## Suitability for Swain

Telegram with forum topics is a strong candidate for the "zero ops" tier. The mapping is clean:

- Telegram supergroup = project room.
- Forum topic = session thread.
- Bot API = programmatic control.
- Native app = mobile access.

The main risks are vendor lock-in and the 20 msg/min/group rate limit. If the bot batches updates (e.g., one summary message per minute instead of per-event), the rate limit is fine. The vendor risk is real but acceptable for a tool that values operator convenience over infrastructure control.
