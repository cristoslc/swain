---
id: swa-9njh
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
# AC-5+6+7: Worktree push, PR fallback, and prune

Step 6: push HEAD:main when IN_WORKTREE=yes; on branch-protection rejection open PR; after land remove worktree and prune


## Notes

**2026-03-14T06:15:18Z**

Completed: Step 6 pushes HEAD:main when IN_WORKTREE=yes, falls back to gh pr create on branch-protection, then removes worktree and prunes — committed in SKILL.md v1.3.0

**2026-03-14T06:15:47Z**

Completed: implemented in commit dacbf2c8 as part of EPIC-015 Active transition
