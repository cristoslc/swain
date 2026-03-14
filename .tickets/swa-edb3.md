---
id: swa-edb3
status: closed
deps: [swa-htqd]
links: []
created: 2026-03-13T23:28:14Z
type: task
priority: 1
assignee: cristos
parent: swa-1wrf
tags: [spec:SPEC-032]
---
# GREEN: Implement bidirectional edge enforcement

Implement check_reciprocal_edges(nodes, edges) in xref.py. For each depends-on edge A->B, check if B's linked-artifacts contains A (need to read from parsed frontmatter). Return missing reciprocal entries with from, edge_type, expected_field.


## Notes

**2026-03-14T04:32:10Z**

Completed: implemented in xref.py (commit b7f504c), integrated in graph.py/cli.py (commits 8aaef5e, 2f29ff8), 47/47 tests passing
