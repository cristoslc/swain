---
id: swa-edb3
status: open
deps: [swa-htqd]
links: []
created: 2026-03-13T23:28:14Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-1wrf
tags: [spec:SPEC-032]
---
# GREEN: Implement bidirectional edge enforcement

Implement check_reciprocal_edges(nodes, edges) in xref.py. For each depends-on edge A->B, check if B's linked-artifacts contains A (need to read from parsed frontmatter). Return missing reciprocal entries with from, edge_type, expected_field.

