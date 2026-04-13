---
source-id: "campfire-bot-kit-api"
title: "Campfire Bot Kit — API Capabilities and Limitations"
type: web
url: "https://github.com/basecamp/campfire-bot-kit"
fetched: 2026-04-06T22:00:00Z
---

# Campfire Bot Kit — API Capabilities and Limitations

## Overview

The campfire-bot-kit is the official reference for building bots on Campfire (37signals/ONCE). It documents the webhook-based bot API that shipped in Campfire 1.1.0 (February 2024). The API is minimal by design, consistent with Campfire's simplicity-first philosophy.

## What Bots Can Do

- **Receive webhooks.** When a user @-mentions or pings a bot, Campfire sends a POST request to the bot's webhook URL. The JSON payload includes the message body (HTML and plain text), the room ID, and the sender.
- **Respond with text or images.** Bots return content with the right MIME type and Campfire posts it to the originating room.
- **Post to rooms independently.** Each bot gets unique per-room URLs with an embedded auth token. A bot can POST to these URLs at any time, not just in response to a mention.
- **Receive room and message paths in payloads.** Added in 1.1.2, the webhook payload includes room and message path information.

## What Bots Cannot Do

- **Create rooms.** No API endpoint exists for room creation. Only human admins can create rooms (and as of 1.4.0, room creation can be restricted to admins only).
- **Archive or delete rooms.** No room lifecycle management via API.
- **List rooms.** No endpoint to enumerate available rooms.
- **Read message history.** Bots only see messages when mentioned. They cannot poll or paginate through past messages.
- **Manage room membership.** No API for adding or removing users from rooms.
- **Search messages.** No search API exists.

## Implications for Prefix-as-Thread Workaround

The bot API cannot create rooms on the fly. A bot that wants to spin up a "thread room" like `swain/SPEC-142-session-abc` would need a human admin to create it, or the application would need to be forked and extended with custom room-creation endpoints. This makes automated pseudo-threading via prefixed rooms impractical without modifying Campfire's source code.

## Community Discussion

GitHub Discussions on once-campfire show users requesting webhook API enhancements (Discussion #142) and asking basic questions about posting via webhooks (Discussion #123). No discussions propose or document a room-prefix threading pattern. No threading feature requests appear at all, suggesting the Campfire user base either does not need threads or has accepted their absence.

## Changelog Highlights

- **1.1.0** (2024-02-15): Bot API introduced.
- **1.1.2**: Room and message paths added to webhook payloads.
- **1.1.7** (2024-07-18): Suppress webhook notification if a bot messages itself.
- **1.1.8** (2025-09-08): Fix for improper bot authentication.
- **1.4.0** (2025-12-01): Restrict room creation to admins only.
