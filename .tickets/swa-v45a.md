---
id: swa-v45a
status: open
deps: [swa-b86s]
links: []
created: 2026-03-13T23:27:02Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-n4vm
tags: [spec:SPEC-031]
---
# GREEN: Implement blocks/blocked-by/tree/edges

Implement as pure functions in a new queries.py module. Each takes nodes dict + edges list, returns string. blocks: filter edges where from==id and type==depends-on. blocked-by: filter where to==id. tree: BFS transitive closure. edges: TSV output, optional id filter. Sort output to match bash.

