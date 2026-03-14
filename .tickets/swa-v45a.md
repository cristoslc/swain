---
id: swa-v45a
status: closed
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


## Notes

**2026-03-14T05:19:49Z**

Completed: blocks/blocked-by/tree/edges implemented in queries.py — sorted output, all tests passing, commit d8839d4
