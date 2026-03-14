---
id: swa-pk70
status: closed
deps: []
links: []
created: 2026-03-13T23:27:35Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-n4vm
tags: [spec:SPEC-031]
---
# RED: scope/impact command tests

Write failing tests for scope(id) and impact(id). scope: walk parent chain to VISION, collect siblings (same parent), lateral links (linked-artifacts, addresses, validates), incoming laterals, supporting vision with architecture-overview.md detection. impact: all referencing edges (including pain-point prefix matching), affected chains via parent walk, total count.


## Notes

**2026-03-14T04:08:19Z**

Completed: implemented in 6eb4eea (specgraph Python rewrite). All 118 tests pass.
