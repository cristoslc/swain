---
id: swa-ozi4
status: closed
deps: []
links: []
created: 2026-03-14T06:07:39Z
type: epic
priority: 2
assignee: cristos
external-ref: SPIKE-007
---
# SPIKE-007 investigation plan

Research container image and runtime requirements for Claude Code. Per SPIKE-009: use Docker as Tier 2. Goal: minimal Dockerfile that runs claude interactively with TTY, <1GB image size.


## Notes

**2026-03-14T06:14:41Z**

Completed: All three sub-tasks closed. swa-whsu (base image/deps), swa-ldxr (TTY behavior), swa-ssfv (Dockerfile produced) — all documented in SPIKE-007 Findings §1-7. Verdict: Go. Minimal Dockerfile in §4.
