---
id: swa-ibqy
status: closed
deps: []
links: []
created: 2026-03-14T06:14:11Z
type: epic
priority: 1
assignee: cristos
external-ref: SPEC-039
tags: [spec:SPEC-039]
---
# SPEC-039 implementation plan

Implement worktree-aware execution in swain-sync SKILL.md. Prose-only change: detect IN_WORKTREE flag, fix bookmark find to use REPO_ROOT, scope stash message, rebase onto origin/main when no upstream, push HEAD:main in worktree, open PR on branch protection, prune worktree after land.


## Notes

**2026-03-14T06:15:22Z**

Completed: All 5 ACs implemented in swain-sync SKILL.md v1.3.0. Worktree detection, stash scoping, rebase-onto-main, push HEAD:main, PR fallback, worktree prune, and REPO_ROOT bookmark fix all landed in commit dacbf2c.

**2026-03-14T06:15:47Z**

Completed: all AC criteria implemented in dacbf2c8; spec ready for Complete transition
