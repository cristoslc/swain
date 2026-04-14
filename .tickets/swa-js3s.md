---
id: swa-js3s
status: closed
deps: [swa-ma7m]
links: []
created: 2026-04-14T01:31:03Z
type: task
priority: 2
assignee: Cristos L-C
parent: swa-qc20
tags: [spec:SPEC-305]
---
# Install tracked post-checkout hook

Add a tracked hook script that reads the swain-owned list (.swain/bin etc) and the peer-agent data file, then symlinks missing entries into the current worktree. swain-init sets core.hooksPath to the tracked directory. Chain into any existing hook path. Test: fresh git worktree add produces all symlinks. Re-runs are no-ops. Existing symlinks untouched.

