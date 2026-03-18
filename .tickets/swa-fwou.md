---
id: swa-fwou
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
# Thread 4: Docker Sandboxes :ro mount semantics

Test docker sandbox run with ~/.claude:ro. Does :ro block writes inside the VM (EROFS) or only prevent sync-back to host? Does docker sandbox accept file-level paths (e.g. ~/.claude/credentials.json:ro) or only directory-level? Check Docker Desktop 4.58+ changelog/docs.


## Notes

**2026-03-18T03:50:58Z**

Docker Desktop 4.65.0 installed. docker sandbox v0.12.0 available. :ro = hard VM-level EROFS (not soft no-sync). File-level mounts NOT supported — directory only. ~/.claude/:ro mount valid and provides strong isolation. Paths preserved same as host.
