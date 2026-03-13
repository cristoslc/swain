---
id: swa-rosx
status: closed
deps: []
links: []
created: 2026-03-13T02:06:21Z
type: epic
priority: 1
assignee: cristos
external-ref: SPIKE-009
---
# Research: Isolation Mechanism Selection

Investigate Docker containers, microVMs, Dev Containers, Orbstack, and Nix/sandbox for isolating Claude Code. Must work on macOS and Linux with <5s startup and real-time filesystem sharing. SPIKE-007 and SPIKE-008 are blocked on this.


## Notes

**2026-03-13T02:28:11Z**

Research complete. All 7 tasks closed. SPIKE-009 findings and recommendation written. Go recommendation: three-tier isolation architecture with shared launcher. Lightweight sandboxing (default) → Docker containers (opt-in) → Docker Sandboxes (strongest). SPIKE-007 and SPIKE-008 are unblocked.
