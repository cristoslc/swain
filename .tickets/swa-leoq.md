---
id: swa-leoq
status: closed
deps: [swa-xcbn]
links: []
created: 2026-03-13T23:28:02Z
type: task
priority: 1
assignee: cristos
parent: swa-1wrf
tags: [spec:SPEC-032]
---
# GREEN: Implement frontmatter ID collector

Implement collect_frontmatter_ids(raw_fields) -> set[str] in xref.py. Iterate relationship fields, extract TYPE-NNN base IDs. For addresses, extract base ID (strip .PP-NN suffix). Skip source-issue and evidence-pool fields.


## Notes

**2026-03-14T04:32:10Z**

Completed: implemented in xref.py (commit b7f504c), integrated in graph.py/cli.py (commits 8aaef5e, 2f29ff8), 47/47 tests passing
