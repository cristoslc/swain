---
id: swa-0g0n
status: closed
deps: []
links: []
created: 2026-03-14T06:05:38Z
type: feature
priority: 2
assignee: cristos
tags: [spec:SPEC-039]
---
# SPEC-039: swain-sync worktree-aware execution

Update swain-sync/SKILL.md to detect git worktree context and adapt Steps 1, 3, 6, and bookmark. See SPEC-039.


## Notes

**2026-03-14T06:06:31Z**

Completed: Updated swain-sync/SKILL.md v1.2.0→v1.3.0. Step 1 now detects worktree context (IN_WORKTREE, REPO_ROOT). Stash message includes branch name. Step 6 uses git push origin HEAD:main when IN_WORKTREE=yes, with PR fallback on branch protection rejection and worktree pruning after landing. Session bookmark uses REPO_ROOT instead of . for discovery. All 8 ACs addressed.
