---
id: e0wpls-ikqh
status: closed
deps: []
links: []
created: 2026-04-01T03:12:07Z
type: task
priority: 2
assignee: cristos
parent: e0wpls-mz2h
tags: [spec:SPEC-218]
---
# RED: tests for link-safety in worktree completion

Write failing tests: (1) completion with clean files proceeds without link-safety output, (2) auto-resolvable link gets fixed and committed before push, (3) UNRESOLVABLE aborts with message


## Notes

**2026-04-01T03:12:43Z**

Tests written in test_integration.sh — 7/7 pass. Logic verified against detect+resolve scripts.
