---
id: swa-okvu
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
# RED: overview command tests

Write failing tests for the overview command. Hierarchy tree: vision nodes at top, children by parent edge, grandchildren. Status icons ([x]/[ ]/[!]). Blocked-by indicators. Cross-cutting section (ADR, PERSONA, RUNBOOK, SPIKE without parent). Unparented section. Executive summary with ready/blocked/counts. Execution tracking section (tk ready integration). --all flag shows resolved nodes.


## Notes

**2026-03-14T04:08:19Z**

Completed: implemented in 6eb4eea (specgraph Python rewrite). All 118 tests pass.
