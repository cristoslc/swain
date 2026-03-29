---
source-id: "codex-cli-session-storage"
title: "Codex CLI Session Storage and Crash Recovery"
type: web
url: "https://developers.openai.com/codex/cli/features"
fetched: 2026-03-28T08:00:00Z
hash: "--"
---

# Codex CLI Session Storage and Crash Recovery

## Storage Location

Codex saves local session transcripts under `CODEX_HOME` (default: `~/.codex/`).

```
~/.codex/
├── history.jsonl           # Session transcript log
├── sessions/               # Per-session state (inferred)
└── config.json             # Global configuration
```

## Session Persistence

- `history.jsonl` is the primary session log
- History file size can be capped via `history.max_bytes` — when exceeded, oldest entries are dropped and the file is compacted
- Sessions can be resumed via `codex resume <name>`

## Known Issues (2026)

- **Session ID before persistence** ([#15870](https://github.com/openai/codex/issues/15870)): Codex can display a session ID before local persistence is committed. Transport errors (WebSocket failures, reconnect attempts) can leave a session ID visible with no local artifacts.
- **Name collision** ([#15943](https://github.com/openai/codex/issues/15943)): Fresh sessions can be auto-named before the thread is persisted. If an older saved thread has the same name, the newer unsaved entry shadows it.
- **Desktop/CLI mismatch** ([#14389](https://github.com/openai/codex/issues/14389)): Desktop app may not see local sessions from a shared `CODEX_HOME`.

## Crash Recovery

- Crash recovery substantially improved but not fully resolved as of v0.117.0
- WebSocket policy close issues and reconnect failure after idle still reported
- Session data written to disk before transport failure is recoverable

## Project Mapping

Not explicitly documented. Sessions appear to be global (not per-project) unless the user structures session names by project.

## What Survives a Crash

- Session transcripts in `history.jsonl` (up to last successful write)
- Named sessions that were fully persisted

## What's Lost

- Sessions where transport failed before persistence committed
- In-flight operations during WebSocket disconnection
