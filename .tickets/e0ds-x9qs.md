---
id: e0ds-x9qs
status: closed
deps: []
links: []
created: 2026-03-20T04:03:10Z
type: task
priority: 2
assignee: cristos
parent: e0ds-5n6l
---
# Add specwatch-ignore step to phase-transitions.md for → Superseded

Add a new step between step 5 (commit) and step 8 (post-op scan) that appends glob patterns for the superseded and superseding artifacts to .agents/specwatch-ignore. Runs only for → Superseded transitions.


## Notes

**2026-03-20T04:03:27Z**

Added step 5a to phase-transitions.md for → Superseded transitions. Appends glob patterns for superseded + superseding artifacts to .agents/specwatch-ignore.
