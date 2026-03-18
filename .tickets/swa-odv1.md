---
id: swa-odv1
status: closed
deps: []
links: []
created: 2026-03-18T03:37:10Z
type: task
priority: 1
assignee: cristos
parent: swa-u7jl
tags: [spike:SPIKE-027, spec:SPEC-067]
---
# Thread 2: test Claude Code with read-only ~/.claude/

Start Claude Code with ~/.claude/ mounted read-only (chmod 555 or docker :ro). Observe: does it launch? Does it error immediately or only on writes? Which operations fail: project memory, settings, bookmarks, telemetry?


## Notes

**2026-03-18T03:50:58Z**

CLAUDE_CONFIG_DIR env var confirmed — redirects ALL writes including .claude.json. ~/.claude/ read-only mount is viable if CLAUDE_CONFIG_DIR points to writable dir. Full read-only HOME causes indefinite hang (no user-facing error). Session state (history, logs, file-edit history) silently not written with read-only mount — not a crash.
