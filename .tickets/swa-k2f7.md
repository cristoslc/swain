---
id: swa-k2f7
status: open
deps: [swa-zvey, swa-8vf4, swa-edb3]
links: []
created: 2026-03-13T23:28:32Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-1wrf
tags: [spec:SPEC-032]
---
# GREEN: Implement xref pipeline and cache integration

Implement run_xref(repo_root, nodes, edges) in xref.py that orchestrates body scanning, frontmatter collection, discrepancy computation, and bidirectional checks for all artifacts. Needs to read markdown body text from files. Integrate into graph.build_graph() to store results under 'xref' cache key. Backward-compatible: existing cache keys unchanged.

