---
id: swa-koml
status: closed
deps: [swa-2yqm]
links: []
created: 2026-03-13T21:33:01Z
type: task
priority: 1
assignee: cristos
parent: swa-9tg7
tags: [spec:SPEC-030]
---
# Integration: verify Python build matches bash build

Run both specgraph.sh build and specgraph.py build on the live repo. Diff cache JSON output after normalizing key order. All nodes and edges must match.


## Notes

**2026-03-13T21:39:41Z**

Full suite: 103 tests pass (26 parser, 53 resolution, 18 graph builder, 6 integration). Python build output matches bash exactly: same 72 nodes, same 132 edges, same metadata.
