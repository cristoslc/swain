---
id: swa-sujx
status: open
deps: [swa-9wuc]
links: []
created: 2026-03-20T15:09:56Z
type: task
priority: 2
assignee: Cristos L-C
parent: swa-f0pa
tags: [spec:SPEC-103]
---
# Add BROKEN_LINK detection to specwatch

Extend specwatch.sh scan to check all markdown link targets ](path) in docs/ artifacts against the filesystem. New finding type BROKEN_LINK with file:line and target path. Exit code 1 when any found.

