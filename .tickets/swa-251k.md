---
id: swa-251k
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
# Thread 3: find CLAUDE_HOME or config-dir env var

Check Claude Code CLI help and docs for env vars that redirect config/state dir (CLAUDE_HOME, CLAUDE_CONFIG_DIR, XDG_CONFIG_HOME). Test: set candidate var to writable path, verify Claude Code writes state there. If none exist, test whether HOME override alone suffices.


## Notes

**2026-03-18T03:50:58Z**

CLAUDE_CONFIG_DIR confirmed in source: process.env.CLAUDE_CONFIG_DIR ?? path.join(homedir(), '.claude'). When set, keychain service name gets hash suffix — existing Mac keychain entry NOT found. CLAUDE_CODE_OAUTH_TOKEN and CLAUDE_CODE_OAUTH_REFRESH_TOKEN env vars confirmed in binary. API key via ANTHROPIC_API_KEY still works. HOME override alone does not redirect config.
