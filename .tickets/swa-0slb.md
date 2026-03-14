---
id: swa-0slb
status: closed
deps: []
links: []
created: 2026-03-13T23:27:17Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-n4vm
tags: [spec:SPEC-031]
---
# RED: ready/next command tests

Write failing tests for ready and next commands. ready: unresolved artifacts with all deps satisfied (using is_resolved logic from resolved.py). next: ready items + what they'd unblock, blocked items + what they need. Test VISION-to-VISION deps are non-blocking. Test OSC 8 link output.


## Notes

**2026-03-14T04:08:19Z**

Completed: implemented in 6eb4eea (specgraph Python rewrite). All 118 tests pass.
