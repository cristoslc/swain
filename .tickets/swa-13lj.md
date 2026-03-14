---
id: swa-13lj
status: closed
deps: []
links: []
created: 2026-03-14T06:07:11Z
type: feature
priority: 2
assignee: cristos
tags: [spec:SPEC-034]
---
# SPEC-034: fix Python scope + ARCH_NO_DIAGRAM check

Fix specgraph.py scope() to walk epic+vision parent chain (bash version already does this). Add ARCH_NO_DIAGRAM check to specwatch.sh. Definition files already have diagram guidance.


## Notes

**2026-03-14T06:09:43Z**

Completed: (1) specgraph.py scope() arch overview chain walk was already in HEAD. (2) Added scan_arch_diagrams() to specwatch.sh - finds architecture-overview.md files without mermaid/image/heading, emits ARCH_NO_DIAGRAM warnings. Wired into 'scan' command. 3 scope test failures are pre-existing (sibling detection bug, not related to this spec). specwatch scan passes cleanly.
