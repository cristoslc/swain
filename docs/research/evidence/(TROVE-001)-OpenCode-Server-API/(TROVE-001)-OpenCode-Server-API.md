---
title: "OpenCode Server API"
artifact: TROVE-001
type: evidence
created: 2026-04-06
source: API exploration + docs
---

# OpenCode Server API Trove

Evidence gathered from a running `opencode serve --port 4097` instance (v1.3.10) via direct HTTP calls, the OpenAPI spec at `/doc`, and CLI help output.

## Endpoints

The server exposes a REST+SSE API. OpenAPI version 3.1.1.

### Session endpoints (not in OpenAPI paths, but functional)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/session` | Create a new session. Returns `Session` object. |
| `GET` | `/session` | List all sessions. Returns array of `Session` objects. |
| `POST` | `/session/{id}/message` | Send a message. Body: `{"parts":[{"type":"text","text":"..."}]}`. Returns assistant response with parts. |
| `GET` | `/session/{id}/event` | SSE stream of session-scoped events. |

### Global endpoints (documented in OpenAPI)

| Method | Path | Summary |
|--------|------|---------|
| `GET` | `/global/health` | Health check. Returns `{"healthy":true,"version":"1.3.10"}`. |
| `GET` | `/global/event` | Global SSE event stream (all sessions, all projects). |
| `GET` | `/global/sync-event` | Global sync event stream (deduplicated, aggregated). |
| `GET` | `/global/config` | Get global configuration. |
| `PATCH` | `/global/config` | Update global configuration. |
| `POST` | `/global/dispose` | Shut down all instances and release resources. |
| `POST` | `/global/upgrade` | Upgrade opencode to a specified or latest version. |

### Auth endpoints

| Method | Path | Summary |
|--------|------|---------|
| `PUT` | `/auth/{providerID}` | Set auth credentials for a provider. |
| `DELETE` | `/auth/{providerID}` | Remove auth credentials for a provider. |

### Logging endpoint

| Method | Path | Summary |
|--------|------|---------|
| `POST` | `/log` | Write a log entry. Body: `{"service":"...","level":"info","message":"...","extra":{}}`. |

## Session Lifecycle

### Creating a session

```bash
curl -X POST http://127.0.0.1:4097/session \
  -H 'Content-Type: application/json' -d '{}'
```

Response:

```json
{
  "id": "ses_29a6309c2ffeNDhL8DD1qcOYVt",
  "slug": "gentle-orchid",
  "version": "1.3.10",
  "projectID": "6dff88243ace23e8fef1727de924be27b0fc7858",
  "directory": "/path/to/project",
  "title": "New session - 2026-04-07T01:44:38.717Z",
  "time": { "created": 1775526278717, "updated": 1775526278717 }
}
```

Key fields: `id` (prefixed `ses_`), `slug` (human-readable), `projectID`, `directory`, `title`, `time`.

### Session persistence

Sessions persist across messages. Listing sessions (`GET /session`) returns all sessions with updated titles (the server auto-generates titles from conversation content). Follow-up messages to the same session ID carry the full conversation history on the server side.

### Session schema (from OpenAPI)

Required fields: `id`, `slug`, `projectID`, `directory`, `title`, `version`, `time`.

Optional fields: `workspaceID` (prefixed `wrk_`), `parentID` (for forked sessions), `summary` (additions/deletions/files/diffs), `share` (URL), `permission`, `revert`.

### SessionStatus

A union type with three variants:

- `{"type":"idle"}` -- session is idle and ready for input.
- `{"type":"busy"}` -- session is processing a message.
- `{"type":"retry","attempt":N,"message":"...","next":T}` -- session is retrying after an error.

## Message Format

### Sending a message (UserMessage)

```bash
curl -X POST http://127.0.0.1:4097/session/{id}/message \
  -H 'Content-Type: application/json' \
  -d '{"parts":[{"type":"text","text":"Say hello in 3 words"}]}'
```

The request body contains `parts` -- an array of part objects. The simplest is `{"type":"text","text":"..."}`.

UserMessage schema required fields: `id`, `sessionID`, `role` ("user"), `time`, `agent`, `model`.

Optional fields: `format` (output format), `summary`, `system` (system prompt override), `tools` (tool enable/disable map), `variant`.

### Response (AssistantMessage)

The response wraps an `info` object (the AssistantMessage) and a `parts` array.

```json
{
  "info": {
    "id": "msg_...",
    "sessionID": "ses_...",
    "role": "assistant",
    "parentID": "msg_...",
    "modelID": "gemma4:31b-cloud",
    "providerID": "ollama-cloud",
    "mode": "build",
    "agent": "build",
    "path": { "cwd": "/path", "root": "/path" },
    "cost": 0,
    "tokens": { "total": 59360, "input": 59350, "output": 10, "reasoning": 0, "cache": {"read":0,"write":0} },
    "time": { "created": 1775526286975, "completed": 1775526296946 },
    "finish": "stop"
  },
  "parts": [
    { "type": "step-start", "snapshot": "...", "id": "prt_...", "sessionID": "ses_...", "messageID": "msg_..." },
    { "type": "text", "text": "Hello there, friend.", "time": {"start":...,"end":...}, "id": "prt_...", "sessionID": "ses_...", "messageID": "msg_..." },
    { "type": "step-finish", "reason": "stop", "snapshot": "...", "tokens": {...}, "cost": 0, "id": "prt_...", "sessionID": "ses_...", "messageID": "msg_..." }
  ]
}
```

### Part types (from OpenAPI union)

- `TextPart` -- text content (`text` field).
- `ToolPart` -- tool call and result.
- `FilePart` -- file content or diff.
- `ReasoningPart` -- reasoning trace.
- `SubtaskPart` -- delegated subtask.
- `StepStartPart` -- marks step beginning (includes `snapshot` git SHA).
- `StepFinishPart` -- marks step end (includes `reason`, `tokens`, `cost`).
- `SnapshotPart` -- git snapshot reference.
- `PatchPart` -- code patch.
- `AgentPart` -- agent delegation.
- `RetryPart` -- retry marker.
- `CompactionPart` -- context compaction marker.

TextPart required fields: `id`, `sessionID`, `messageID`, `type` ("text"), `text`.

## SSE Events

### Event stream endpoints

- `GET /session/{id}/event` -- session-scoped events (real-time, per session).
- `GET /global/event` -- global events (wrapped in `GlobalEvent` with `directory` and `payload`).
- `GET /global/sync-event` -- sync events (deduplicated, aggregated by `sessionID`).

### Event types (from OpenAPI schema)

**Session lifecycle:**

- `session.created` -- new session. Payload: `{sessionID, info: Session}`.
- `session.updated` -- session metadata changed.
- `session.deleted` -- session removed.
- `session.status` -- status change. Payload: `{sessionID, status: SessionStatus}`.
- `session.idle` -- session finished processing. Payload: `{sessionID}`.
- `session.error` -- session error. Payload: `{sessionID, error}`.
- `session.compacted` -- context compacted.
- `session.diff` -- file diff produced.

**Message streaming:**

- `message.updated` -- full message object updated. Payload: `{sessionID, info: Message}`.
- `message.removed` -- message removed.
- `message.part.updated` -- part added or updated. Payload: `{sessionID, part: Part, time}`.
- `message.part.removed` -- part removed.
- `message.part.delta` -- incremental text delta. Payload: `{sessionID, messageID, partID, field, delta}`.

**Permissions and questions:**

- `permission.asked` -- tool needs permission. Payload includes `PermissionRequest`.
- `permission.replied` -- permission granted/denied.
- `question.asked` -- question for the user. Payload: `QuestionRequest` with `id`, `sessionID`, `questions[]`.
- `question.replied` -- answer provided.
- `question.rejected` -- question rejected.

**Infrastructure:**

- `server.connected` -- initial connection event.
- `server.instance.disposed` -- instance shut down.
- `global.disposed` -- all instances disposed.
- `installation.updated` -- version updated.
- `installation.update-available` -- new version available.

**TUI commands (for attached clients):**

- `tui.prompt.append` -- append text to prompt.
- `tui.command.execute` -- execute a TUI command (session.list, session.new, session.interrupt, prompt.submit, etc.).
- `tui.toast.show` -- show toast notification with variant (info/success/warning/error).
- `tui.session.select` -- navigate to a session.

**File and workspace:**

- `file.edited` -- file edited by the agent.
- `file.watcher.updated` -- file watcher detected changes.
- `workspace.ready` / `workspace.failed` -- workspace state.
- `worktree.ready` / `worktree.failed` -- git worktree state.
- `vcs.branch.updated` -- branch changed.

**Other:**

- `pty.created` / `pty.updated` / `pty.exited` / `pty.deleted` -- pseudo-terminal lifecycle.
- `lsp.client.diagnostics` / `lsp.updated` -- LSP events.
- `mcp.tools.changed` / `mcp.browser.open.failed` -- MCP events.
- `todo.updated` -- todo list changed.
- `command.executed` -- command executed.

### Key event for adapter: `message.part.delta`

This is the streaming event for real-time text output:

```json
{
  "type": "message.part.delta",
  "properties": {
    "sessionID": "ses_...",
    "messageID": "msg_...",
    "partID": "prt_...",
    "field": "text",
    "delta": "chunk of text"
  }
}
```

Accumulate `delta` values for the same `partID` to reconstruct the full text. When `session.idle` fires, the response is complete.

### Key event for adapter: `session.idle`

Signals that the session has finished processing and is ready for the next message:

```json
{
  "type": "session.idle",
  "properties": { "sessionID": "ses_..." }
}
```

## Auth

- Server password set via `OPENCODE_SERVER_PASSWORD` environment variable (optional).
- When set, clients must provide the password. The `opencode attach` command accepts `-p/--password` flag.
- Per-provider auth credentials managed via `PUT /auth/{providerID}` and `DELETE /auth/{providerID}`.
- Auth schema (`Auth`) is a union of `ApiAuth`, `OAuth`, and `WellKnownAuth`.
- Default model configured in `~/.config/opencode/opencode.json`.
- Current test model: `ollama-cloud/gemma4:31b-cloud` (Gemma 4 via Ollama Cloud).

## Operator Attachment

The operator can connect a full TUI to a running headless server:

```bash
opencode attach http://127.0.0.1:4097
```

Options:

- `-p/--password` -- basic auth password (defaults to `OPENCODE_SERVER_PASSWORD`).
- `-c/--continue` -- continue the last session.
- `-s/--session` -- continue a specific session by ID.
- `--fork` -- fork the session when continuing (use with `--continue` or `--session`).
- `--dir` -- directory to run in.
- `--print-logs` -- print logs to stderr.
- `--log-level` -- log level (DEBUG, INFO, WARN, ERROR).
- `--pure` -- run without external plugins.

This means the bridge can print `opencode attach http://127.0.0.1:<port>` and the operator gets a full interactive session with scroll, tool approval, and command history.

## JS SDK

The `@opencode-ai/sdk` npm package wraps these HTTP endpoints. It provides typed client methods for session creation, message sending, and event subscription. Useful if the adapter were written in JS/TS, but the swain adapter will use direct HTTP calls from Python.

## Configuration Schema

The server exposes its full config via `GET /global/config` and accepts updates via `PATCH /global/config`. The `Config` schema includes provider settings, model selection, permission rules, layout preferences, and MCP server configuration.

## Adapter Integration Notes

1. **Startup**: spawn `opencode serve --port <N>` as a subprocess. Poll `GET /global/health` until `{"healthy":true}`.
2. **Session creation**: `POST /session` with empty body. Cache the `id` for reuse.
3. **Sending messages**: `POST /session/{id}/message` with `{"parts":[{"type":"text","text":"..."}]}`. The response includes the full assistant message and parts. For synchronous use, this is sufficient.
4. **Streaming**: connect to `GET /session/{id}/event` via SSE. Watch for `message.part.delta` events to stream text in real time, and `session.idle` to know when the response is complete.
5. **Session reuse**: the same session ID accepts multiple messages. The server maintains conversation history.
6. **Crash recovery**: if the `opencode serve` process exits, restart it on the same port. Existing session data persists on disk (SQLite in `~/.local/share/opencode/`).
7. **Shutdown**: `POST /global/dispose` for clean shutdown, or send SIGTERM to the process.
8. **Operator access**: print `opencode attach http://127.0.0.1:<port>` so the operator can connect at any time.
