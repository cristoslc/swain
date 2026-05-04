---
id: swa-ma7m
status: closed
deps: []
links: []
created: 2026-04-14T01:30:53Z
type: task
priority: 2
assignee: Cristos L-C
parent: swa-qc20
tags: [spec:SPEC-305]
---
# Extract peer-agent dir list to shared data file

Move the inline agent_dirs list from bin/swain to a shared data file (e.g. scripts/hooks/agent-runtime-dirs.txt). bin/swain, the post-checkout hook, and swain-doctor all read from it. Verify existing worktree behavior is unchanged.


## Notes

**2026-04-14T01:38:03Z**

Abandoned: ADR-042 supersedes ADR-040. No hook needed — tracked files appear in worktrees via git. Peer-agent dirs are tracked by default.
