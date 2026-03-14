---
id: swa-dp20
status: open
deps: [swa-c9lc]
links: []
created: 2026-03-13T23:28:02Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-1wrf
tags: [spec:SPEC-032]
---
# GREEN: Implement body scanner

Implement scan_body() in a new xref.py module. Use re.findall(r'[A-Z]+-\d+', body) to find candidates, then filter against known_ids set and exclude self_id. Return set of artifact IDs found in body but not in frontmatter relationships.

