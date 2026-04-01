---
id: e0wpls-t45t
status: closed
deps: [e0wpls-7zwf]
links: []
created: 2026-04-01T02:57:57Z
type: task
priority: 2
assignee: cristos
parent: e0wpls-gqvt
tags: [spec:SPEC-216]
---
# GREEN: implement markdown link scanner

Implement markdown scanner: regex [text](target), walk ../ to resolve from repo root, flag if resolution escapes repo root. Emit file:line: target [ESCAPES_REPO]. Make T3 tests pass.


## Notes

**2026-04-01T03:05:33Z**

Tests written and passing (integrated into full test run).
