---
id: swa-kvf5
status: closed
deps: []
links: []
created: 2026-03-17T18:21:46Z
type: task
priority: 1
assignee: cristos
parent: swa-gm1z
tags: [spec:SPEC-064]
---
# RED: Write tests for diff-only security gate trigger

Test that gate runs for security-sensitive tasks (using threat_surface.py), skips non-security tasks, and invokes security_check in diff-only mode.


## Notes

**2026-03-17T18:24:50Z**

RED complete: 10 tests for should_run_gate, 6 tests for get_changed_files, 6 tests for run_gate trigger behavior. All fail with ModuleNotFoundError (security_gate.py not yet implemented).

**2026-03-17T18:29:10Z**

Complete: merged from worktree-agent-a03d69eb. 35 tests.
