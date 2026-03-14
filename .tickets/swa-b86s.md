---
id: swa-b86s
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
# RED: blocks/blocked-by/tree/edges tests

Write failing tests for the four simplest query commands. blocks(id): direct depends-on targets. blocked-by(id): inverse depends-on lookup. tree(id): transitive dependency closure. edges(id?): raw edge list with types, optionally filtered. Test against fixture graphs with known structure.


## Notes

**2026-03-14T04:08:19Z**

Completed: implemented in 6eb4eea (specgraph Python rewrite). All 118 tests pass.
