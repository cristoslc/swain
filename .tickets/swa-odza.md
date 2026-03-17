---
id: swa-odza
status: closed
deps: [swa-kvf5, swa-1qiw]
links: []
created: 2026-03-17T18:21:46Z
type: task
priority: 1
assignee: cristos
parent: swa-gm1z
tags: [spec:SPEC-064]
---
# GREEN: Implement security gate and finding-to-ticket flow

Python module that integrates threat_surface + security_check (diff mode) + tk issue creation. Script at skills/swain-security-check/scripts/security_gate.py.


## Notes

**2026-03-17T18:26:02Z**

GREEN complete: security_gate.py implemented with should_run_gate, get_changed_files, run_gate, file_finding_as_ticket. All 35 tests pass. Full suite (390 tests) passes with no regressions.

**2026-03-17T18:29:11Z**

Complete: merged from worktree-agent-a03d69eb. 35 tests.
