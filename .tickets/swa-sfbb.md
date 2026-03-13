---
id: swa-sfbb
status: closed
deps: []
links: []
created: 2026-03-13T23:05:37Z
type: task
priority: 2
assignee: cristos
parent: swa-01mh
tags: [spec:SPEC-034]
---
# Update specgraph scope to detect epic-level architecture overviews

Walk parent chain: check Epic directory first, then Vision directory. Show both if both exist. Update bash specgraph.sh do_scope and add to Python SPEC-031 scope.


## Notes

**2026-03-13T23:07:37Z**

Updated bash specgraph.sh do_scope to walk parent chain (Epic first, then Vision) for architecture-overview.md detection. Shows both if both exist. Verified against live repo — no errors.
