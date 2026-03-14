---
id: swa-e2ll
status: closed
deps: [swa-3dkf]
links: []
created: 2026-03-14T04:59:12Z
type: task
priority: 1
assignee: cristos
parent: swa-ul7c
tags: [spec:SPEC-033]
---
# Add xref data to status JSON cache

In swain-status.sh collect_artifacts(), read the xref array from the specgraph JSON cache and include it in the status cache JSON under an 'xref' key. If xref key absent from cache, use empty array.


## Notes

**2026-03-14T05:10:19Z**

Completed: xref and xref_gap_count added to status JSON cache
