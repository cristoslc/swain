---
id: swa-30s7
status: closed
deps: []
links: []
created: 2026-03-17T18:11:24Z
type: task
priority: 1
assignee: cristos
parent: swa-cdhc
tags: [spec:SPEC-063]
---
# RED: Write tests for security briefing generation per category

Test that auth-sensitive tasks get OWASP A07 guidance, input-validation gets A03, agent-context gets swain-specific guidance, etc.


## Notes

**2026-03-17T18:13:59Z**

RED confirmed: 43 tests written for security briefing generation per category (auth/A07, input-validation/A03, crypto/A02, external-data/A08, agent-context/swain, dependency-change/A06, secrets/A07+specific, multi-category, format, signature). All fail with ModuleNotFoundError as security_briefing.py does not exist yet.

**2026-03-17T18:21:13Z**

Complete: merged from worktree-agent-a2263eeb. 42 tests.
