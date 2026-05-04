---
title: "OpenCode Server Adapter"
artifact: SPEC-292
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
parent-initiative: INITIATIVE-018
linked-artifacts:
  - DESIGN-025
  - ADR-038
  - SPEC-291
depends-on-artifacts:
  - DESIGN-025
  - SPEC-291
sourcecode-refs:
  - src/untethered/adapters/opencode_server.py
  - src/untethered/adapters/tmux_pane.py
  - src/untethered/bridges/project.py
---

# OpenCode Server Adapter

## Summary

Replace `TmuxPaneAdapter` with `OpenCodeServerAdapter` for control-topic sessions. The adapter manages an `opencode serve` process, creates sessions via HTTP, sends messages, and streams responses via SSE.

## Motivation

The current `TmuxPaneAdapter` launches an agent in a tmux pane and scrapes its output. This has drawbacks: no message boundaries, no crash persistence, and no way for the operator to attach a TUI. The `opencode serve` HTTP API solves all three. The adapter starts a headless server, sends prompts via REST, streams responses via SSE, and lets the operator connect with `opencode attach`.

## Acceptance Criteria

1. `OpenCodeServerAdapter` starts `opencode serve --port <N>` as a managed subprocess and waits for `GET /global/health` to return `{"healthy":true}` before accepting commands.
2. On the first `control_message`, the adapter creates a session via `POST /session` and caches the session ID for reuse.
3. Messages are sent via `POST /session/{id}/message` with body `{"parts":[{"type":"text","text":"..."}]}`.
4. The adapter connects to `GET /session/{id}/event` via SSE and emits `text_output` events by accumulating `message.part.delta` payloads. It treats `session.idle` as the response-complete signal.
5. The session persists across multiple `control_message` commands. The adapter reuses the cached session ID rather than creating a new session per message.
6. The bridge prints `opencode attach http://127.0.0.1:<port>` so the operator can connect a full TUI at any time.
7. If the `opencode serve` process crashes (exit detected on the subprocess), the adapter restarts it on the same port and resumes. Existing session data persists on disk, so the restarted server recovers prior sessions.
8. The adapter replaces `TmuxPaneAdapter` for `control_message` sessions. `TmuxPaneAdapter` remains available for `/work` sessions that need tmux isolation.

## Out of Scope

- Replacing `TmuxPaneAdapter` for `/work` sessions.
- Multi-model routing or provider switching at the adapter level.
- Permission-granting via the bridge (the adapter runs with auto-approve or the operator handles permissions via attach).
- SSE reconnection with event replay (Phase 1 reconnects from current state).
