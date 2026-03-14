---
id: swa-dp20
status: closed
deps: [swa-c9lc]
links: []
created: 2026-03-13T23:28:02Z
type: task
priority: 1
assignee: cristos
parent: swa-1wrf
tags: [spec:SPEC-032]
---
# GREEN: Implement body scanner

Implement scan_body() in a new xref.py module. Use re.findall(r'[A-Z]+-\d+', body) to find candidates, then filter against known_ids set and exclude self_id. Return set of artifact IDs found in body but not in frontmatter relationships.


## Notes

**2026-03-14T04:32:10Z**

Completed: implemented in xref.py (commit b7f504c), integrated in graph.py/cli.py (commits 8aaef5e, 2f29ff8), 47/47 tests passing
