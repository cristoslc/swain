---
id: swa-t89z
status: closed
deps: [swa-rdlc]
links: []
created: 2026-03-13T23:27:02Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-n4vm
tags: [spec:SPEC-031]
---
# GREEN: Implement neighbors command

Implement neighbors() in queries.py. Iterate all edges, emit both directions where from==id or to==id. Include node metadata (status, title) when available. TSV output sorted by direction+type+id.


## Notes

**2026-03-14T05:19:50Z**

Completed: neighbors command implemented — 5-column TSV, sorted, missing nodes handled, spec compliance reviewed ✅, commit 9ca2b63
