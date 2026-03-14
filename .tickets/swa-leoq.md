---
id: swa-leoq
status: open
deps: [swa-xcbn]
links: []
created: 2026-03-13T23:28:02Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-1wrf
tags: [spec:SPEC-032]
---
# GREEN: Implement frontmatter ID collector

Implement collect_frontmatter_ids(raw_fields) -> set[str] in xref.py. Iterate relationship fields, extract TYPE-NNN base IDs. For addresses, extract base ID (strip .PP-NN suffix). Skip source-issue and evidence-pool fields.

