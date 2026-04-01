---
id: e0wpls-qsym
status: closed
deps: [e0wpls-ztlt]
links: []
created: 2026-04-01T02:57:57Z
type: task
priority: 2
assignee: cristos
parent: e0wpls-gqvt
tags: [spec:SPEC-216]
---
# GREEN: implement script scanner

Implement script scanner: grep *.sh files for patterns matching /tmp/worktree-, .claude/worktrees/, and the repo root absolute path baked in. Emit file:line: path [HARDCODED_WORKTREE_PATH]. Make T7 tests pass.


## Notes

**2026-04-01T03:05:33Z**

Tests written and passing (integrated into full test run).
