---
title: "Implementing the Chat Bridge"
artifact: TRAIN-001
track: standing
status: Active
author: cristos
created: 2026-04-24
last-updated: 2026-04-24
audience: Developers adding features or fixing bugs in the swain-helm Zulip chat bridge.
train-type: how-to
superseded-by:
linked-artifacts:
  - VISION-006
  - ADR-046
  - ADR-047
  - EPIC-084
  - RUNBOOK-004
artifact-refs:
  - artifact: SPEC-291
    rel: [documents]
    commit: 2bb0c0ea
    verified: 2026-04-24
  - artifact: SPEC-329
    rel: [documents]
    commit: 2bb0c0ea
    verified: 2026-04-24
parent-epic: EPIC-084
parent-initiative:
---

# Implementing the Chat Bridge

## Prerequisites

- Python 3.12+ development environment with `uv` installed.
- The swain-helm repo cloned and dependencies installed (`uv sync`).
- A Zulip organization with a bot account for testing.
- Familiarity with NDJSON line-delimited protocols.
- Read [ADR-046](docs/adr/Active/(ADR-046)-Per-Bridge-Plugin-Processes/(ADR-046)-Per-Bridge-Plugin-Processes.md) (per-bridge subprocess architecture) before starting.

## Learning Objectives

After completing this document, the reader will be able to:
- Trace a message from Zulip to the runtime and back.
- Add a new event type or command to the protocol.
- Implement a new slash command in the chat adapter.
- Fix the Zulip reconnection bug if it regresses.
- Rebuild and relaunch the Docker container with updated code.

## Architecture Overview

The chat bridge has three layers that communicate via NDJSON over stdio pipes:

```
Zulip Cloud ←→ zulip_chat.py (subprocess) ←→ watchdog kernel ←→ opencode_server.py (subprocess) ←→ opencode serve
```

1. **zulip_chat.py** — A subprocess plugin that polls Zulip and relays events. Two async coroutines run inside it:
   - `_poll_zulip` — reads operator messages from Zulip, parses them into Commands, writes them to stdout.
   - `_relay_events` — reads Events from stdin, formats them for Zulip, posts them via the Zulip API.
2. **Watchdog kernel** — The `watchdog.py` process that manages plugin subprocesses (PluginProcess). It reads Commands from plugin stdout and routes them to the correct ProjectBridge. It reads Events from ProjectBridge and writes them back to plugin stdin.
3. **opencode_server.py** — A subprocess adapter that connects to the opencode serve HTTP API. It translates Commands into HTTP requests and SSE events back into protocol Events.

Each bridge gets its own zulip_chat.py subprocess. The watchdog spawns and manages them.

## Step 1: Trace a message end-to-end

An operator types "status?" in Zulip. Here is the path:

1. Zulip delivers the message event to `_poll_zulip` via `call_on_each_event`.
2. `_on_message` checks sender (skip bot's own messages), calls `parse_zulip_message`.
3. `parse_zulip_message` (in `adapters/zulip_chat.py`) returns a `Command` of type `send_prompt`.
4. `_emit` writes the Command as NDJSON to stdout.
5. The watchdog kernel reads it via `PluginProcess._read_stdout`, decodes it, and routes to the matching `ProjectBridge`.
6. ProjectBridge handles the command, talks to the runtime adapter.
7. The runtime adapter's response comes back as an `Event`.
8. The watchdog writes the Event as NDJSON to the chat plugin's stdin.
9. `_relay_events` reads the Event, calls `format_event_for_zulip`, posts to Zulip.

## Step 2: Add a new event type

To add a new event type (e.g., `approval_needed`):

1. **Define the protocol type** in `src/swain_helm/protocol.py`:
   - Add the type string to the `Event` class factory method (e.g., `Event.approval_needed`).
   - Ensure `encode_message` and `decode_message` handle the new type.

2. **Add format logic** in `src/swain_helm/adapters/zulip_chat.py`:
   - Add a case in `format_event_for_zulip` that produces the Zulip message content.

3. **Add relay logic** in `src/swain_helm/plugins/zulip_chat.py`:
   - Add a case in `_relay_events` (under the correct section: trunk-origin, promoted, or regular session).
   - Call `typing.start` or `typing.stop` as appropriate.

4. **Write tests**:
   - Unit test: protocol roundtrip (`encode_message` / `decode_message`).
   - Integration test: `_relay_events` posts the formatted message correctly.
   - Integration test: `_poll_zulip` parses the corresponding slash command if two-way.

## Step 3: Add a new slash command

To add a new slash command (e.g., `/approve`):

1. **Add parsing logic** in `src/swain_helm/adapters/zulip_chat.py`:
   - Add a case in `parse_zulip_message` that matches the slash command pattern.
   - Return a `Command` of the appropriate type with parsed payload fields.

2. **Add protocol type** in `src/swain_helm/protocol.py`:
   - Add the Command factory method (e.g., `Command.approve`).

3. **Add routing** in the runtime adapter (`src/swain_helm/adapters/opencode_server.py`):
   - Implement the handler method (e.g., `_approve_permission`).
   - Add routing in `send_command` or the equivalent dispatch method.

4. **Write tests**:
   - Unit test: `parse_zulip_message` produces the correct Command.
   - Integration test: `_poll_zulip` emits the Command when the slash command is received.
   - Integration test: the adapter routes the Command correctly.

## Step 4: Fix Zulip reconnection (the queue expiration bug)

If `_poll_zulip` stops receiving messages after a period of silence, the Zulip event queue has expired. The SDK raises an exception instead of reconnecting. The fix is the reconnection loop in `_poll_zulip`:

1. `_poll_zulip` wraps `call_on_each_event` in a `for` loop with `max_reconnect_attempts`.
2. On success (normal return), it reconnects after `reconnect_delay`.
3. On `CancelledError`, it re-raises (clean shutdown).
4. On any other exception, it logs the error and sleeps with exponential backoff: `min(reconnect_delay * 2^attempt, 60.0)`.
5. After `max_reconnect_attempts` failures, it raises the last exception.

To test this:
- Unit test: mock `call_on_each_event` to raise an auth error, verify reconnect.
- Unit test: mock it to fail `max_reconnect_attempts` times, verify the exception propagates.

## Step 5: TypingIndicator

The `TypingIndicator` class sends Zulip stream/topic typing notifications. Key points:

- `start(stream, topic)` — creates a `_pulse` task that sends `set_typing_status` with `op: start` every 10 seconds.
- `stop(stream, topic)` — cancels the pulse task and sends `op: stop`.
- Safety: auto-stops after `MAX_DURATION` (300s) to prevent "typing forever" if `turn_ended` never arrives.
- `_send_typing` resolves `stream_id` from stream name and calls `client.set_typing_status()`.
- Errors in `_send_typing` are logged at debug level and swallowed (typing indicators are non-critical).

The no-op stub version was a regression. If typing stops working, check that `TypingIndicator.__init__` takes `(client, loop)` and that `_pulse` and `_send_typing` are present.

## Step 6: Rebuild and relaunch Docker

After any code change, rebuild and relaunch the container to test:

```bash
# Stop and remove the existing container
docker stop swain-helm-watchdog && docker rm swain-helm-watchdog

# Rebuild (from repo root)
PROJECT_PATH="$(pwd)" \
PROJECT_NAME=swain \
ZULIP_BOT_EMAIL="swain-helm-bot@cristoslc.zulipchat.com" \
ZULIP_BOT_API_KEY="<your-api-key>" \
ZULIP_SITE="https://cristoslc.zulipchat.com" \
ZULIP_OPERATOR_EMAIL="operator@example.com" \
docker compose build --no-cache

# Relaunch
PROJECT_PATH="$(pwd)" \
PROJECT_NAME=swain \
ZULIP_BOT_EMAIL="swain-helm-bot@cristoslc.zulipchat.com" \
ZULIP_BOT_API_KEY="<your-api-key>" \
ZULIP_SITE="https://cristoslc.zulipchat.com" \
ZULIP_OPERATOR_EMAIL="operator@example.com" \
docker compose up -d

# Verify
docker ps --filter name=swain-helm-watchdog
docker logs swain-helm-watchdog --tail 20
```

Credential resolution inside Docker uses env vars (no `op` CLI). The docker-compose.yml maps `ZULIP_BOT_API_KEY` to `SWAIN_HELM_CHAT_BOT_API_KEY`.

## Step 7: Run the tests

```bash
# Unit + integration tests (fast)
uv run pytest tests/unit/ tests/integration/ -x -q

# External smoke tests (requires running container)
uv run pytest tests/external/ -x -q
```

Integration tests use mock Zulip clients. The `_poll_zulip` calls need `TypingIndicator(MagicMock(), asyncio.get_running_loop())` and `max_reconnect_attempts=1, reconnect_delay=0.01` for fast execution. The `_relay_events` calls need `TypingIndicator(MagicMock(), asyncio.get_running_loop())` as the last argument.

## Key Takeaways

- The bridge is three NDJSON-piped layers: zulip_chat.py, watchdog kernel, opencode_server.py.
- `_poll_zulip` has a reconnection loop with exponential backoff — the SDK does not auto-reconnect on queue expiration.
- `TypingIndicator` is a real implementation that pulses Zulip typing status every 10 seconds. The no-op stub was a regression.
- Each bridge gets its own subprocess. The watchdog manages lifecycles.
- Always rebuild Docker after code changes. The container cannot see host filesystem changes.

## Next Steps

- [RUNBOOK-004](docs/runbook/Active/(RUNBOOK-004)-swain-helm-Operations/(RUNBOOK-004)-swain-helm-Operations.md) — operating the bridge day-to-day.
- [ADR-046](docs/adr/Active/(ADR-046)-Per-Bridge-Plugin-Processes/(ADR-046)-Per-Bridge-Plugin-Processes.md) — per-bridge subprocess architecture rationale.
- [SPEC-329](docs/spec/Active/(SPEC-329)-Permission-Surfacing/(SPEC-329)-Permission-Surfacing.md) — permission approval flow via `/approve` and `/deny`.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-24 | 2bb0c0ea | Initial creation |