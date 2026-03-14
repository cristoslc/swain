---
id: swa-t89z
status: closed
deps: [swa-rdlc]
links: []
created: 2026-03-13T23:27:02Z
type: task
priority: 1
assignee: cristos
parent: swa-n4vm
tags: [spec:SPEC-031]
---
# GREEN: Implement neighbors command

Implement neighbors() in queries.py. Iterate all edges, emit both directions where from==id or to==id. Include node metadata (status, title) when available. TSV output sorted by direction+type+id.


## Notes

**2026-03-14T05:07:18Z**

Completed: neighbors() added to queries.py with tests.
