---
id: swa-bepi
status: closed
deps: []
links: []
created: 2026-03-17T17:11:02Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-z7pq
tags: [spec:SPEC-059]
---
# RED: Write tests for scanner binary detection (gitleaks, osv-scanner, trivy)

Test that detection correctly identifies presence/absence of each Go binary scanner. Test OS-specific install command generation (brew on Darwin, apt on Linux).


## Notes

**2026-03-17T18:10:41Z**

Complete: implementation merged from worktree-agent-ac564be9. 30 tests passing.
