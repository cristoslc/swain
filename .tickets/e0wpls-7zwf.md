---
id: e0wpls-7zwf
status: closed
deps: [e0wpls-ti32]
links: []
created: 2026-04-01T02:57:57Z
type: task
priority: 2
assignee: cristos
parent: e0wpls-gqvt
tags: [spec:SPEC-216]
---
# RED: markdown link scanner — ESCAPES_REPO detection

Write failing tests: (1) link with too many ../ hops flagged as ESCAPES_REPO, (2) valid relative link in same repo not flagged, (3) exit code 1 when findings, 0 when clean.


## Notes

**2026-04-01T03:05:33Z**

Tests written and passing (integrated into full test run).
