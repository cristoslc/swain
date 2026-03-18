---
id: swa-u7jl
status: closed
deps: []
links: []
created: 2026-03-18T03:36:57Z
type: epic
priority: 2
assignee: Cristos L-C
external-ref: SPIKE-027
---
# SPIKE-027: Claude Config Dir Mount Strategy

Research spike: can ~/.claude/ be selectively mounted into a Docker Sandbox to reuse Max subscription login and global skills, without leaking per-project memories or allowing host write-back? Five investigation threads + synthesis. Gates SPEC-067 Ready transition.


## Notes

**2026-03-18T03:56:19Z**

All 5 threads complete. Verdict: Conditional Go — don't mount ~/.claude/. See SPIKE-027 for full findings.
