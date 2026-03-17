---
id: swa-hlaj
status: closed
deps: []
links: []
created: 2026-03-17T18:11:23Z
type: epic
priority: 1
assignee: Cristos L-C
external-ref: SPEC-060
---
# Implement SPEC-060: swain-security-check Skill

Build the swain-security-check skill — orchestration shell that invokes all scanners (gitleaks, osv-scanner/trivy, semgrep, context-file scanner), normalizes findings, and produces a unified severity-bucketed report in JSON and markdown.


## Notes

**2026-03-17T18:20:15Z**

All 5 child tasks closed. SPEC-060 fully implemented: security_check.py orchestrator, 43 tests, SKILL.md. 283/283 repo tests pass.
