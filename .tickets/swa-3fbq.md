---
id: swa-3fbq
status: closed
deps: [swa-p71m]
links: []
created: 2026-03-13T21:33:01Z
type: task
priority: 1
assignee: cristos
parent: swa-9tg7
tags: [spec:SPEC-030]
---
# GREEN: Implement graph builder and cache I/O

Build nodes dict and edge list from parsed frontmatter in graph.py. Write JSON cache to /tmp/agents-specgraph-<hash>.json. Cache freshness check (any docs/*.md newer than cache). SHA-256 repo hash matching bash behavior.


## Notes

**2026-03-13T21:38:55Z**

graph.py and cache I/O implemented during scaffold; 18 unit tests + 6 integration tests pass.
