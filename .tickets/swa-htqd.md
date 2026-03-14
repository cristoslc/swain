---
id: swa-htqd
status: closed
deps: []
links: []
created: 2026-03-13T23:28:14Z
type: task
priority: 1
assignee: cristos
parent: swa-1wrf
tags: [spec:SPEC-032]
---
# RED: Bidirectional edge enforcement tests

Write failing tests for reciprocal edge detection. Given A depends-on B, B should have A in linked-artifacts. Test: edge present (no gap), edge missing (gap flagged), multiple depends-on edges, self-referential edges. Function: check_reciprocal_edges(nodes, edges) -> list[dict] with from, edge_type, expected_field.


## Notes

**2026-03-14T04:46:19Z**

Completed: RED phase done — tests written and all 47 pass as of commit 5a4386c
