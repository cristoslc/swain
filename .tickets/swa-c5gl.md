---
id: swa-c5gl
status: closed
deps: [swa-bepi, swa-pc1x]
links: []
created: 2026-03-17T17:11:02Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-z7pq
tags: [spec:SPEC-059]
---
# GREEN: Implement scanner availability checker

Shell/Python function that checks each scanner, returns availability status and install command per detected OS. Under 1 second, no network calls.


## Notes

**2026-03-17T18:10:41Z**

Complete: implementation merged from worktree-agent-ac564be9. 30 tests passing.
