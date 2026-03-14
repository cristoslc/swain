---
id: swa-0tzj
status: closed
deps: []
links: []
created: 2026-03-14T06:14:32Z
type: task
priority: 2
assignee: cristos
parent: swa-b1oa
tags: [spec:SPEC-043]
---
# AC-5: Read-only ops skip worktree creation

Gate worktree creation on operation type: tk ready, status, show are read-only; plan creation and task claim trigger worktree check


## Notes

**2026-03-14T06:16:24Z**

Completed: worktree isolation preamble added to swain-do/SKILL.md covering AC-1 through AC-5

**2026-03-14T06:18:42Z**

Completed: Read-only ops (tk ready, tk show, status checks, task queries) skip worktree detection — explicitly documented in SKILL.md (v3.1.0)
