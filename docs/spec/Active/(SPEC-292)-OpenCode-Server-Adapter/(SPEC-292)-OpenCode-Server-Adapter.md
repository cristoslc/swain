---
title: "OpenCode Server Adapter"
artifact: SPEC-292
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-21
parent-initiative: INITIATIVE-018
linked-artifacts:
  - DESIGN-025
  - ADR-038
  - ADR-046
  - SPEC-291
depends-on-artifacts:
  - DESIGN-025
  - SPEC-291
sourcecode-refs:
  - src/swain_helm/adapters/opencode_server.py
  - src/swain_helm/bridges/project.py
  - src/swain_helm/watchdog.py
---

# OpenCode Server Adapter

## Summary

Replace `TmuxPaneAdapter` with `OpenCodeServerAdapter` for trunk sessions. The adapter connects to a watchdog-managed `opencode serve` process, creates sessions via HTTP, sends messages asynchronously via `prompt_async`, and streams responses via SSE. Falls back to synchronous `POST /session/{id}/message` when SSE is unavailable.

## Motivation

The original `TmuxPaneAdapter` scraped output from tmux panes. The `opencode serve` HTTP API provides structured sessions, message boundaries, crash persistence, and operator TUI attachment. The original synchronous approach (`POST /session/{id}/message`) blocked the event loop for up to 120 seconds per LLM response. The async+SSE approach sends messages immediately via `prompt_async` (returns 204) and receives streaming `message.part.delta` events through the global `GET /event` SSE endpoint, with `session.idle` signaling turn completion.

## Acceptance Criteria

1. `OpenCodeServerAdapter` connects to a watchdog-managed `opencode serve` process and waits for `GET /global/health` to return `{"healthy":true}` before accepting commands.
2. On first `send_prompt`, the adapter creates a session via `POST /session` and caches the session ID for reuse, emitting `session_spawned` and a connect message.
3. Messages are sent via `POST /session/{id}/prompt_async` (returns 204 No Content) for non-blocking delivery. Falls back to synchronous `POST /session/{id}/message` on non-204 responses.
4. The adapter connects to `GET /event` (global SSE) on setup and accumulates `message.part.delta` payloads into `text_output` events. It emits `turn_ended` on `session.idle`.
5. The session persists across multiple `send_prompt` commands. The adapter reuses the cached session ID rather than creating a new session per message.
6. The adapter emits `opencode attach http://127.0.0.1:<port>` in the `session_spawned` message so the operator can connect a full TUI at any time.
7. Permission requests via `permission.asked` SSE events are forwarded as `approval_needed` protocol events.
8. The SSE client reconnects on connection errors with exponential backoff (1s initial, 30s max).
9. Cancel support via `POST /session/{id}/abort`.

## Out of Scope

- Replacing `TmuxPaneAdapter` for `/work` sessions.
- Multi-model routing or provider switching at the adapter level.
- Permission-granting via the bridge (the adapter forwards `permission.asked` but approval comes from the operator).
- SSE reconnection with event replay (reconnects from current state).

## Implementation Notes

- The watchdog owns and manages a single `opencode serve` process (ADR-046), not the adapter.
- The adapter runs as a subprocess plugin (ADR-038) and communicates via NDJSON over stdio.
- SSE listener runs as a background `asyncio.Task` started by `adapter.setup()`.
- Text deltas are buffered per `partID` and emitted incrementally to support streaming display in the chat adapter.
- The `_flushed_up_to` dict tracks how much of each part's text has already been emitted, so only new deltas are forwarded.
