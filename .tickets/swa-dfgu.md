---
id: swa-dfgu
status: open
deps: [swa-pk70]
links: []
created: 2026-03-13T23:27:35Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-n4vm
tags: [spec:SPEC-031]
---
# GREEN: Implement scope/impact commands

Implement scope() and impact() in queries.py. scope: walk_parents BFS up parent-epic/parent-vision edges. siblings: same parent, different id. laterals: linked-artifacts, addresses, validates, superseded-by, evidence-pool edges. Check filesystem for architecture-overview.md. impact: find all edges where to==id or to starts with id+dot. Walk parent chains. Format with DIRECT/AFFECTED CHAINS/TOTAL.

