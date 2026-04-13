---
source-id: "zulip-bot-api"
title: "Zulip Bot API and ChatOps Integration"
type: web
url: "https://zulip.com/api/writing-bots"
fetched: 2026-04-06T20:00:00Z
---

# Zulip Bot API and ChatOps Integration

## Bot Types

Zulip supports three types of bots:

1. **Interactive bots** — respond to @-mentions using the Python bot framework.
2. **Outgoing webhook bots** — send HTTP POST requests to external services when mentioned.
3. **Generic API bots** — use the REST API directly for full programmatic control.

## REST API Capabilities

The Zulip REST API covers all operations needed for a bot-driven workflow:

### Stream/Channel Management

- Create a channel.
- Get all channels.
- Get channel by ID.
- Update a channel.
- Archive a channel.
- Get topics in a channel.
- Subscribe/unsubscribe from channels.

### Message Operations

- Send a message (to stream+topic or as DM).
- Edit a message.
- Delete a message.
- Get messages (with narrow filters for stream, topic, sender).
- Fetch a single message.
- Upload files.
- Render markdown.
- Mark messages as read (per-topic or all).
- Get message edit history.
- Get read receipts.
- Add/remove emoji reactions.

### Topic Management

- Topics are part of every message (required field).
- Topics can be muted per-user.
- Topics can be deleted.
- Topic max length: 60 characters.

## SDKs and Libraries

- **Python**: `zulip` and `zulip_bots` packages (official).
- **JavaScript**: `zulip-js` (official).
- **REST API**: curl-friendly JSON API.
- 100+ native integrations for common services.

## Bot Framework

The Python bot framework provides:

```python
class MyBot:
    def usage(self):
        return "Bot description"

    def handle_message(self, message, bot_handler):
        bot_handler.send_message(dict(
            type='stream',
            to='channel-name',
            subject='topic-name',
            content='message body'
        ))
```

## ChatOps Pattern

Zulip's threading model (streams + topics) is ideal for ChatOps:

- Deploy notifications go to `deployments` stream, `production` topic.
- Alert notifications go to `alerts` stream, `critical` topic.
- Each topic functions as a persistent thread.
- Messages within a topic are ordered chronologically.
- Bots can route messages based on context to appropriate streams and topics.

## Key Advantage for Bot-Driven Workflows

Every message requires a topic, so the bot naturally creates organized threads. A bot posting `session-2026-04-06-001` as the topic within a `project-swain` stream creates an automatically organized session thread. No extra API calls needed — the organizational structure is inherent in the message format.
