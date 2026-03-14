---
id: swa-px0k
status: closed
deps: []
links: []
created: 2026-03-14T06:14:20Z
type: task
priority: 2
assignee: Cristos L-C
parent: swa-ibqy
tags: [spec:SPEC-039]
---
# AC-4: Rebase onto origin/main when no upstream

When IN_WORKTREE=yes and @{u} absent: git fetch origin && git rebase origin/main


## Notes

**2026-03-14T06:15:18Z**

Completed: When IN_WORKTREE=yes and no upstream, fetches and rebases onto origin/main — committed in SKILL.md v1.3.0

**2026-03-14T06:15:46Z**

Completed: implemented in commit dacbf2c8 as part of EPIC-015 Active transition
