---
source-id: roo-code-cli
type: web
url: https://deepwiki.com/RooCodeInc/Roo-Code/15-cli-application
title: "CLI Application | RooCodeInc/Roo-Code | DeepWiki"
fetched: 2026-04-07T13:54:13Z
supplemental-urls:
  - https://github.com/RooCodeInc/Roo-Code/issues/3835
---

# Roo Code CLI (`@roo-code/cli`) — Headless Mode

**Roo Code** (formerly Roo-Cline) is a Cline fork (~22K stars, 1.2M installs)
that diverged to add custom Modes, diff-based editing, and multi-agent workflows.
Unlike Cline, which ships a standalone CLI, Roo Code's CLI (`@roo-code/cli`) is a
Node.js app that shims the VS Code API to run the core extension logic headlessly —
no VS Code process required.

---

## Dual-mode overview

| Mode | Trigger | Description |
|---|---|---|
| **TUI (interactive)** | `roo-code` / `roo` (TTY, non-print mode) | Rich terminal UI using Ink (React-based) |
| **Headless** | Stdin stream mode (NDJSON) | Programmatic control via structured JSON messages |

---

## Headless mode

Roo Code's CLI headless mode uses a structured **stdin stream protocol** rather than
command-line flags. The parent process writes NDJSON commands to stdin:

```json
{"type":"start","task":"Fix all TypeScript errors in src/","sessionId":"abc-123"}
{"type":"message","content":"Focus on strict null check errors first"}
{"type":"cancel"}
{"type":"ping"}
{"type":"shutdown"}
```

**Command types:**
- `start` — begin a new task (with optional `sessionId` for resume)
- `message` — send a follow-up message to the running task
- `cancel` — cancel the current task
- `ping` — keepalive check
- `shutdown` — graceful shutdown

This is distinct from all other tools in this trove — Roo Code has a **protocol**
rather than CLI flags. It is designed for embedding in orchestration systems
rather than shell scripts.

**Environment signal:**
```bash
ROO_CLI_RUNTIME=1  # set automatically; signals headless to core logic
```

---

## Output format

Roo Code's CLI uses a `JsonEventEmitter` for output. Two formats:

| Format | Behavior |
|---|---|
| `stream-json` (NDJSON) | Real-time streaming of tool use, text deltas, and state changes |
| `json` | Single accumulated JSON object emitted at task completion |

Output is emitted to stdout as NDJSON. Delta streaming reduces payload size —
tool outputs and command results are streamed as deltas, not full snapshots.

---

## Session continuity

Sessions are UUID-identified and persistent. The CLI can:
- Create a task with a specific `sessionId` for later resumption.
- Resume an existing session from workspace history by passing the same `sessionId` in a `start` command.

---

## Safety limits

| Flag | Effect |
|---|---|
| `--require-approval` | Force manual confirmation for every tool and command call |
| `--consecutive-mistake-limit <n>` | Stop if agent loops on errors N times (prevents runaway) |

---

## Architecture note

The CLI runs the **same core extension logic** as the VS Code extension, using a
`@roo-code/vscode-shim` package that provides mock VS Code API implementations.
This means all Roo Code features — custom Modes, diff-based editing, MCP tools —
are available in headless operation.

---

## Modes (Roo Code's key differentiator from Cline)

Roo Code adds **custom Modes** on top of Cline's Plan/Act pattern:
- **Code Mode** — standard coding tasks
- **Architect Mode** — system design and planning
- **Ask Mode** — codebase exploration without file edits
- **Custom modes** — user-defined personas with their own system prompts and tool permissions

Modes are usable in CLI/headless operation and persist per-task.

---

## MCP integration

Roo Code inherits Cline's MCP implementation and its own Mode Gallery marketplace.
All MCP tools configured for the extension are available in CLI mode.

---

## Skills dimension summary

| Dimension | Roo Code CLI |
|---|---|
| Skills/plugin name | "Modes" (custom personas with scoped permissions) |
| Extension mechanism | MCP (same as Cline; Roo Code Mode Gallery) |
| Headless protocol | Stdin NDJSON stream (not flags) — unique in this set |
| Output format | `stream-json` (NDJSON) or `json` |
| Session resume | UUID-based; persisted to workspace |
| Safety limits | `--require-approval`, `--consecutive-mistake-limit` |
| SKILL.md compat | Not documented (forked from Cline pre-Skills) |
| Key differentiator from Cline | Custom Modes with scoped tool permissions; NDJSON protocol |
