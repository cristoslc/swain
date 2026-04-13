---
source-id: "tinode-lightweight-chat-server"
title: "Tinode — Lightweight Self-Hosted Chat Server with Native Clients and Bot Support"
type: web
url: "https://github.com/tinode/chat"
fetched: 2026-04-07T06:00:00Z
---

# Tinode — Lightweight Self-Hosted Chat Server with Native Clients and Bot Support

## What It Is

Tinode is a self-hosted instant messaging platform written in Go. It positions itself as a modern replacement for XMPP/Jabber with a simpler protocol and built-in support for bots, plugins, and multiple client types.

## Architecture and Deployment

- **Server:** Single Go binary (`tinode-server`). Can run standalone or in a sharded cluster.
- **Database:** Supports MySQL, PostgreSQL, or MongoDB as the backend store. RethinkDB support exists but is deprecated.
- **Docker:** Official Docker images available. A typical deployment is one container for the server plus one for the database.
- **Not truly single-process.** Unlike conduwuit or Campfire, Tinode needs an external database. This adds one more service to manage.

## Client Ecosystem

- **Android:** Tindroid (Java). Native app.
- **iOS:** Tinodios (Swift). Native app.
- **Web:** React.js single-page application.
- **CLI:** Python scriptable command-line client. Good for bot development and testing.
- **gRPC and JSON/WebSocket API:** Two protocol options for programmatic access.

## Bot and Plugin Support

- Built-in chatbot framework with a sample bot ("Tino").
- Plugin architecture for extending functionality (moderation, custom logic).
- The gRPC API gives bots full access to messaging primitives: send messages, create groups, manage members.
- The Python CLI client can be scripted into a bot.

## Channels and Groups

- **One-on-one messaging** and **group messaging** supported.
- **Channels** with unlimited read-only subscribers for broadcast patterns.
- Groups can be created programmatically via the API.
- **No native threading.** Messages within a group are a flat stream. There is no topic, thread, or sub-conversation concept built into the protocol. A bot would need to implement threading at the application layer (e.g., prefixed messages, metadata tags).

## Threading Assessment

This is Tinode's main weakness for the swain use case. Without native threading, session separation within a project room requires workarounds:

1. **One group per session.** Creates many groups. No visual hierarchy.
2. **Message prefixes.** Bot prefixes messages with session IDs. No client-side filtering.
3. **Custom metadata.** Messages support custom headers, but clients do not render them as threads.

None of these are as clean as Zulip's mandatory topics or even Matrix's MSC3440 thread relations.

## Resource Requirements

Not formally documented, but the Go binary is lightweight. With a PostgreSQL backend, expect 200-500 MB RAM for a small deployment. Less than Zulip or Mattermost, more than conduwuit.

## Mobile Apps

Native Android and iOS apps exist and are maintained. They provide a standard chat interface. Push notifications are supported. The mobile experience is better than PWA-only options (Campfire) but the apps are less polished than Telegram or Element X.

## Suitability for Swain

Tinode is a genuine lightweight alternative to Mattermost and Rocket.Chat. It has native mobile apps, a scriptable bot interface, and a simpler architecture. But the lack of native threading is a significant gap. For a "one room per project, one thread per session" model, Tinode would require either many groups (one per session) or application-layer threading hacks.

If threading is negotiable and the priority is "lighter than Mattermost with real mobile apps and a bot API," Tinode is worth considering. If threading is mandatory, it falls short.
