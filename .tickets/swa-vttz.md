---
id: swa-vttz
status: closed
deps: [swa-ol3y]
links: []
created: 2026-03-20T21:21:27Z
type: task
priority: 1
assignee: cristos
parent: swa-3cbh
tags: [spec:SPEC-114]
---
# Create one-time branch migration script

Shell script that: (1) renames main to trunk locally and on remote, (2) creates release branch from trunk HEAD, (3) sets release as default branch on GitHub via gh api, (4) pushes both branches. Must be idempotent and reversible. Include a dry-run mode.


## Notes

**2026-03-20T21:46:58Z**

Completed: scripts/migrate-to-trunk-release.sh created. Idempotent, --dry-run, prerequisite checks. Commit fc8f246, merged.
