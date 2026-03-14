---
id: swa-ldxr
status: closed
deps: []
links: []
created: 2026-03-14T06:07:57Z
type: task
priority: 2
assignee: cristos
parent: swa-ozi4
tags: [spec:SPIKE-007]
---
# Investigate TTY and terminal resize behavior in containers

Does claude require -it TTY? Does it handle SIGWINCH/terminal resize in a container? Does it run non-interactively (for --print mode)?


## Notes

**2026-03-14T06:11:29Z**

Completed: -it TTY required for interactive mode. claude -p works headless. SIGWINCH propagates normally via docker exec -it. Known bug: SIGKILL from background child also kills Claude (shared process group, issue #16135).
