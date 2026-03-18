---
id: swa-8t7a
status: closed
deps: []
links: []
created: 2026-03-18T11:54:33Z
type: task
priority: 2
assignee: cristos
parent: swa-62fm
tags: [spec:SPEC-067]
---
# Create scripts/swain-box wrapper script

Create a thin POSIX shell script at scripts/swain-box that: (1) checks docker is on PATH, (2) checks docker sandbox subcommand available (Desktop 4.58+), (3) resolves arg or defaults to $PWD, (4) checks path exists, (5) runs: docker sandbox run claude <absolute-path>. AC-1 through AC-5.


## Notes

**2026-03-18T11:55:40Z**

scripts/swain-box created in worktree spec-067-swain-box. Covers AC-1 through AC-5. Uses cd+pwd for portable absolute path resolution.
