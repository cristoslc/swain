---
id: swa-vc4x
status: closed
deps: []
links: []
created: 2026-03-17T18:11:24Z
type: epic
priority: 1
assignee: Cristos L-C
external-ref: SPEC-061
---
# Implement SPEC-061: swain-doctor Security Integration

Lightweight security check during swain-doctor session start. Runs context-file scanner (critical categories only) on AGENTS.md/CLAUDE.md, checks for tracked .env files, integrates scanner availability diagnostics. Must complete in <3 seconds.


## Notes

**2026-03-17T18:21:13Z**

Complete: merged from worktree-agent-acd2ab08. 30 tests.
