---
id: swa-8vf4
status: closed
deps: [swa-ika9, swa-dp20, swa-leoq]
links: []
created: 2026-03-13T23:28:14Z
type: task
priority: 1
assignee: cristos
parent: swa-1wrf
tags: [spec:SPEC-032]
---
# GREEN: Implement discrepancy computation

Implement compute_discrepancies(body_ids, frontmatter_ids) -> (body_not_in_fm, fm_not_in_body) in xref.py. Simple set difference operations returning sorted lists.


## Notes

**2026-03-14T04:32:10Z**

Completed: implemented in xref.py (commit b7f504c), integrated in graph.py/cli.py (commits 8aaef5e, 2f29ff8), 47/47 tests passing
