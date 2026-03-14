---
id: swa-rdlc
status: closed
deps: []
links: []
created: 2026-03-13T23:27:02Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-n4vm
tags: [spec:SPEC-031]
---
# RED: neighbors command tests

Write failing tests for neighbors(id). Must produce TSV: direction, edge_type, id, status, title. Both incoming and outgoing edges. Sort by direction+type+id.


## Notes

**2026-03-14T04:08:19Z**

Completed: implemented in 6eb4eea (specgraph Python rewrite). All 118 tests pass.
