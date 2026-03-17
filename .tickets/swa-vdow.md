---
id: swa-vdow
status: closed
deps: []
links: []
created: 2026-03-17T18:11:23Z
type: task
priority: 1
assignee: cristos
parent: swa-hlaj
tags: [spec:SPEC-060]
---
# RED: Write tests for scanner orchestration and graceful degradation

Test that orchestrator runs available scanners, skips missing ones with warnings, and produces unified output.


## Notes

**2026-03-17T18:15:21Z**

RED complete: 43 tests written in tests/test_security_check.py covering orchestration, graceful degradation, scanner invocation, scanner crash handling, repo hygiene. All tests fail with ModuleNotFoundError as expected.
