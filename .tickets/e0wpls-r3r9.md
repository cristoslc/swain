---
id: e0wpls-r3r9
status: closed
deps: [e0wpls-t45t]
links: []
created: 2026-04-01T02:57:57Z
type: task
priority: 2
assignee: cristos
parent: e0wpls-gqvt
tags: [spec:SPEC-216]
---
# RED: symlink scanner — SYMLINK_ESCAPE detection

Write failing tests: (1) symlink with relative target resolving outside repo root flagged as SYMLINK_ESCAPE, (2) symlink within repo not flagged, (3) symlink loop emits SYMLINK_LOOP warning and skips.


## Notes

**2026-04-01T03:05:33Z**

Tests written and passing (integrated into full test run).
