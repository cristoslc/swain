---
id: aa-bkm1
status: closed
deps: []
links: []
created: 2026-03-17T17:12:46Z
type: task
priority: 1
assignee: cristos
tags: [spec:SPEC-058]
---
# RED — Tests for categories H-J (MCP config manipulation, HTML comment injection, external fetch+exec)

Write pytest tests for context file scanner categories H (MCP config manipulation), I (HTML comment injection), J (external fetch+exec). SPEC-058.


## Notes

**2026-03-17T17:16:05Z**

RED complete: 40 tests fail (H=9, I=7, J=10 detection + CLI=5 + FileDiscovery=10), 8 pass (benign/negative). All expected to fail.
