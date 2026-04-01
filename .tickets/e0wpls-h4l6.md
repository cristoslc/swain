---
id: e0wpls-h4l6
status: closed
deps: [e0wpls-r3r9]
links: []
created: 2026-04-01T02:57:57Z
type: task
priority: 2
assignee: cristos
parent: e0wpls-gqvt
tags: [spec:SPEC-216]
---
# GREEN: implement symlink scanner

Implement symlink scanner: for each symlink in file set, readlink to get target, resolve from repo root, flag if resolution escapes. Handle SYMLINK_LOOP. Make T5 tests pass.


## Notes

**2026-04-01T03:05:33Z**

Tests written and passing (integrated into full test run).
