---
source-id: "matrix-threading-msc3440"
title: "Matrix Threading via MSC3440 — Status and Implementation"
type: web
url: "https://matrix.org/blog/2022/09/29/matrix-v-1-4-release/"
fetched: 2026-04-06T20:00:00Z
---

# Matrix Threading via MSC3440 — Status and Implementation

## Specification Status

Threading in Matrix landed in the **Matrix v1.4 specification** (released September 2022). It required six MSCs:

- **MSC3440**: Threading via `m.thread` relation (core proposal).
- **MSC3816**: Clarifications for threaded events.
- **MSC3856**: Threads list API.
- **MSC3715**: Aggregation of thread roots.
- **MSC3771**: Read receipts for threads.
- **MSC3773**: Notifications for threads.

## How Threading Works

Threads use event relationships. A reply in a thread sets the `m.thread` relation pointing to the thread root event. This is different from Zulip's model where every message belongs to a topic; in Matrix, threading is opt-in per-message.

## Implementation Status

- **Synapse**: Full thread support (since v1.x series).
- **Element Web/Desktop**: Thread support in stable.
- **Element X (mobile)**: Thread support available.
- **Conduit/conduwuit**: Support varies; the thread relation is part of the spec but some aggregation features may be incomplete.

## Bot Implications

For a bot creating threads programmatically:

1. Send a root message to a room.
2. Subsequent messages in the "thread" must include `m.relates_to` with `rel_type: "m.thread"` pointing to the root event ID.
3. The bot must track the root event ID for each session.
4. Thread listing uses the `/threads` API endpoint.

This is more work than Zulip's model (where topic is just a string field on every message) but is fully functional.

## Limitations

- Threading was added retroactively to a flat-room model. Some clients and homeservers may have incomplete support.
- Thread notifications are separate from room notifications, which can be confusing.
- No "threads-only rooms" yet (where every message must be in a thread). This is future work mentioned in the spec.
- The Spec Core Team noted threads needed more real-world validation before finalization.

## Comparison with Zulip

In Zulip, every message has a topic — threading is mandatory and structural. In Matrix, threads are optional relations — a room can have a mix of threaded and unthreaded messages. For a bot-driven workflow where every session should be a thread, Zulip's model is more natural. Matrix requires the bot to explicitly manage thread relations.
