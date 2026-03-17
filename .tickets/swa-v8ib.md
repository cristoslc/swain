---
id: swa-v8ib
status: closed
deps: []
links: []
created: 2026-03-17T18:11:24Z
type: task
priority: 1
assignee: cristos
parent: swa-vc4x
tags: [spec:SPEC-061]
---
# RED: Write tests for lightweight context-file scan (critical categories)

Test that only categories D/F/G/H are checked during doctor. Test AGENTS.md and CLAUDE.md scanning.


## Notes

**2026-03-17T18:14:36Z**

RED complete: 30 tests written, all fail with ModuleNotFoundError (doctor_security_check module does not exist yet). Tests cover: critical category filtering (D/F/G/H only), exclusion of A/B/C/E/I/J, diagnostic output format (CRIT/WARN), silent pass, AGENTS.md/CLAUDE.md/SKILL.md scanning, tracked .env detection, main() CLI.
