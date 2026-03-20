---
id: swa-ol3y
status: open
deps: []
links: []
created: 2026-03-20T21:21:27Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-3cbh
tags: [spec:SPEC-114]
---
# Replace rebase with merge in swain-sync worktree landing

In the swain-sync skill, replace the rebase-onto-origin/main step with git merge origin/trunk. Add retry loop (max 3 attempts) on non-fast-forward push rejection. Run tests on the merged result before push. This is the primary ADR-011 change. Update the skill file and the sync shell script.

