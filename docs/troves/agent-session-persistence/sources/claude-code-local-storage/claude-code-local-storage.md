---
source-id: "claude-code-local-storage"
title: "How Claude Code Manages Local Storage for AI Agents"
type: web
url: "https://milvus.io/blog/why-claude-code-feels-so-stable-a-developers-deep-dive-into-its-local-storage-design.md"
fetched: 2026-03-28T08:00:00Z
hash: "--"
---

# How Claude Code Manages Local Storage for AI Agents

## Directory Structure

All session data lives under `~/.claude/`:

```
~/.claude/
├── sessions/              # Session metadata indexed by PID
│   └── {pid}.json         # {pid, sessionId, cwd, startedAt, kind, entrypoint}
├── history.jsonl           # Global conversation index (append-only)
├── projects/               # Per-project conversation storage
│   └── {path-slug}/       # Path-encoded (e.g., -Users-me-proj)
│       └── {sessionId}.jsonl  # Full conversation per session
├── file-history/           # Per-session file edit tracking
│   └── {sessionId}/       # Snapshots at message boundaries
├── shell-snapshots/        # Shell function state snapshots
│   └── snapshot-zsh-{ts}-{suffix}.sh
├── tasks/                  # Task/todo state per session
│   └── {sessionId}/
│       ├── .lock
│       └── .highwatermark
├── backups/                # Config backup snapshots
├── ide/                    # IDE workspace mapping
│   └── {pid}.lock         # {pid, workspaceFolders, ideName}
├── session-env/            # Session-specific environment (placeholder)
│   └── {sessionId}/
├── debug/                  # Structured logging
│   └── {sessionId}.txt
└── settings.json           # User configuration
```

## Session Identification

Each session gets a UUID (`sessionId`) mapped to the working directory:

1. OS assigns PID on process start
2. Claude Code generates 36-char UUID sessionId
3. `sessions/{pid}.json` records: `{pid, sessionId, cwd, startedAt, entrypoint}`
4. `history.jsonl` appends: `{sessionId, project, timestamp, message}`
5. `projects/{encoded-path}/{sessionId}.jsonl` stores full conversation

## JSONL Format

Messages are written to disk as soon as they're generated — one line per message, append-only. If the program crashes, only the last unfinished message may be lost. Everything written before that stays intact.

## Project Path Encoding

Project paths are encoded by replacing every non-alphanumeric character with `-`. For example: `/Users/me/proj` becomes `-Users-me-proj`.

## Crash Recovery Path

```
Orphaned PID in sessions/{pid}.json (process no longer running)
  → sessionId + cwd (project path)
  → projects/{encoded-path}/{sessionId}.jsonl (full conversation)
  → file-history/{sessionId}/ (file snapshots at message boundaries)
```

## Automatic Cleanup

Default setting cleans up local conversation history after 30 days. Configurable via `cleanupPeriodDays` in settings.json.

## Session Resume

Claude Code supports `/resume` to reload a previous session's conversation context. The session picker shows recent sessions for the current project.

## What Survives a Crash

- Full conversation history (append-only JSONL — crash-safe)
- Session metadata (PID, sessionId, cwd, startedAt)
- File edit snapshots (at message boundaries)
- Shell environment snapshots
- Task execution cursor

## What's Lost

- In-flight operations (commands executing but not yet written)
- File changes between snapshot boundaries
- Runtime state (process-local variables, temp files)
