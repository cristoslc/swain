---
source-id: "gemini-cli-session-management"
title: "Gemini CLI Session Management"
type: web
url: "https://geminicli.com/docs/cli/session-management/"
fetched: 2026-03-28T08:00:00Z
hash: "--"
---

# Gemini CLI Session Management

## Storage Location

Sessions are stored in `~/.gemini/tmp/<project_hash>/chats/`, where `project_hash` is a unique identifier based on the project's root directory. Sessions are project-specific — switching directories switches to that project's session history.

```
~/.gemini/
├── tmp/
│   └── <project_hash>/
│       └── chats/          # Per-project session files
├── settings.json           # Global configuration
└── GEMINI.md               # Global memory file
```

## Data Persisted Per Session

- Complete conversation history (prompts and model responses)
- Tool execution details (inputs and outputs)
- Token usage statistics (input, output, cached amounts)
- Assistant reasoning and thoughts when available

## Session Resume

**Command line:**
- `gemini --resume` — loads the most recent session
- `gemini --resume 1` — resumes by index number
- `gemini --resume [UUID]` — resumes by session ID

**Interactive:**
- `/resume` slash command opens the Session Browser
- Browse, preview, and search past sessions

## Session Management Commands

- `gemini --list-sessions` — list all sessions
- `gemini --delete-session [index/ID]` — delete a session

## Configuration

Retention configurable via `settings.json`:
- Default: retain sessions for 30 days
- `maxCount` limits total sessions retained
- `maxSessionTurns` limits conversation length

## Project Directory Mapping

Sessions are project-specific via `project_hash` derived from the project root directory. This means crashed sessions can be mapped back to a project.

## Crash Recovery

Current state (2026): When Gemini CLI crashes unexpectedly, sessions cannot be resumed. A feature request ([#11758](https://github.com/google-gemini/gemini-cli/issues/11758)) proposes automatic session saving and crash recovery — offering to resume from where the previous session left off when a crash is detected.

## What Survives a Crash

- Session files already written to disk in `~/.gemini/tmp/<project_hash>/chats/`
- Global memory (`GEMINI.md`)
- Configuration

## What's Lost

- In-flight conversation turns not yet flushed to disk
- Session state if crash recovery is not yet implemented
