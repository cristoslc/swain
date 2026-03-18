---
id: swa-872z
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
# Thread 1: locate claude login credential file

Inspect ~/.claude/ on host after claude login. Identify exact file(s) written by OAuth flow (credentials.json, .credentials, auth.json, etc.). Determine whether it is a bearer token, refresh token, or session cookie. This is the minimal mount target for Max sub reuse.


## Notes

**2026-03-18T03:50:58Z**

Credentials on macOS live in Keychain (service: Claude Code-credentials). ~/.claude/.credentials.json only exists on Linux/no-keychain. ~/.claude.json at HOME contains oauthAccount identity metadata (no tokens). Mounting keychain not viable in Docker. Viable: CLAUDE_CODE_OAUTH_TOKEN env var, or ANTHROPIC_API_KEY. Minimal file mount if needed: ~/.claude.json (identity metadata only).
