---
id: swa-z7pq
status: open
deps: []
links: []
created: 2026-03-17T17:10:29Z
type: epic
priority: 1
assignee: Cristos L-C
external-ref: SPEC-059
---
# Implement SPEC-059: Tooling Availability Strategy

Define and implement per-scanner binary detection (gitleaks, osv-scanner, trivy via brew/apt; semgrep via uv run). Integrate availability checks into swain-doctor diagnostics. swain-security-check degrades gracefully when scanners are absent.

