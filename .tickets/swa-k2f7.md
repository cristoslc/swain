---
id: swa-k2f7
status: closed
deps: [swa-zvey, swa-8vf4, swa-edb3]
links: []
created: 2026-03-13T23:28:32Z
type: task
priority: 1
assignee: cristos
parent: swa-1wrf
tags: [spec:SPEC-032]
---
# GREEN: Implement xref pipeline and cache integration

Implement run_xref(repo_root, nodes, edges) in xref.py that orchestrates body scanning, frontmatter collection, discrepancy computation, and bidirectional checks for all artifacts. Needs to read markdown body text from files. Integrate into graph.build_graph() to store results under 'xref' cache key. Backward-compatible: existing cache keys unchanged.


## Notes

**2026-03-14T04:28:22Z**

Completed: xref integrated into build_graph in graph.py — stores results under xref cache key

**2026-03-14T04:32:10Z**

Completed: implemented in xref.py (commit b7f504c), integrated in graph.py/cli.py (commits 8aaef5e, 2f29ff8), 47/47 tests passing
