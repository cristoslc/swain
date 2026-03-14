---
id: swa-cij6
status: closed
deps: [swa-u4k5]
links: []
created: 2026-03-13T23:27:17Z
type: task
priority: 1
assignee: cristos
parent: swa-n4vm
tags: [spec:SPEC-031]
---
# GREEN: Implement mermaid/status commands

Implement mermaid() and status() in queries.py. mermaid: emit graph TD, node labels with escaped quotes, edges with type labels. Filter by visibility (show_all flag). status: group nodes by type, sort by id within group, emit formatted table. Include hidden count.


## Notes

**2026-03-14T05:16:06Z**

Completed: mermaid_cmd/status_cmd implemented with tests.
