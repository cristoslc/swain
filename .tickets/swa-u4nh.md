---
id: swa-u4nh
status: closed
deps: [swa-kkzp]
links: []
created: 2026-03-13T23:05:37Z
type: task
priority: 2
assignee: cristos
parent: swa-01mh
tags: [spec:SPEC-034]
---
# GREEN: implement diagram check

Implement has_diagram() function. Wire into specwatch scan as ARCH_NO_DIAGRAM warning. Check all architecture-overview.md files in docs/.


## Notes

**2026-03-13T23:07:37Z**

Implemented arch_check.py with has_diagram() and find_architecture_overviews(). 15 unit tests pass.
