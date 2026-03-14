---
id: swa-na4r
status: closed
deps: [swa-fkfl]
links: []
created: 2026-03-14T06:07:57Z
type: task
priority: 2
assignee: cristos
parent: swa-ymk2
tags: [spec:SPIKE-008]
---
# Design filesystem binding strategy for agent state dirs

Map host paths to container/sandbox paths for: project dir, .claude/, .agents/, .tickets/, ~/.claude/ global config. Which dirs must be writable vs. read-only? Exclude sensitive host files.


## Notes

**2026-03-14T06:13:26Z**

Completed: State dirs in project root need no separate mounts. Docker: project root + ~/.claude/ (rw), creds ro. Tier 1 sandbox-exec: per-file allowlist for signing keys + gh + gitconfig. See SPIKE-008 findings sections 2 and 6.
