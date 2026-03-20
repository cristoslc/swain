---
id: s1h-k6ok
status: closed
deps: [s1h-z0l5]
links: []
created: 2026-03-20T15:11:03Z
type: task
priority: 2
assignee: cristos
parent: s1h-wrgp
tags: [spec:SPEC-103]
---
# Add BROKEN_LINK detection to specwatch

Extend specwatch.sh scan to check all markdown link targets in docs/ artifacts against the filesystem. New finding type BROKEN_LINK with file:line and target path. Exit code 1 when any found.


## Notes

**2026-03-20T15:16:03Z**

BROKEN_LINK finding type added to specwatch. Emitted alongside STALE for markdown-link subset. Summary includes broken link count. 8 broken links detected in current docs tree.
