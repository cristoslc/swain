---
id: swa-p71m
status: closed
deps: [swa-yi6y]
links: []
created: 2026-03-13T21:33:01Z
type: task
priority: 1
assignee: cristos
parent: swa-9tg7
tags: [spec:SPEC-030]
---
# RED: Graph builder tests

Write tests for build_graph() that given parsed frontmatter from multiple files, produces correct nodes dict and typed edge list. Cover all edge types: depends-on, parent-epic, parent-vision, linked-artifacts, validates, addresses, superseded-by, evidence-pool, source-issue.


## Notes

**2026-03-13T21:38:55Z**

18 graph builder tests pass: edge types (depends-on, linked-artifacts, validates, addresses, source-issue, superseded-by, parent-vision, parent-epic), non-artifact skipping, empty ref skipping, cache I/O, staleness detection, repo hash.
