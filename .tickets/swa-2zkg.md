---
id: swa-2zkg
status: open
deps: []
links: []
created: 2026-04-14T01:38:46Z
type: task
priority: 2
assignee: Cristos L-C
parent: swa-qc20
tags: [spec:SPEC-305]
---
# Remove create_session_worktree() symlinking blocks

Delete the skill dir, .swain-init, and peer-agent dir symlink blocks from bin/swain create_session_worktree(). Per ADR-042, all dirs are tracked and appear in worktrees via git. Test: worktree creation still succeeds. Worktree has access to tracked files.

