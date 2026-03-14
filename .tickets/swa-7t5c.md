---
id: swa-7t5c
status: closed
deps: []
links: []
created: 2026-03-14T03:29:22Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-t3vy
tags: [spec:SPEC-036]
---
# Update swain-status.sh — add unblock_count to ready items

In skills/swain-status/scripts/swain-status.sh, find the jq expression that builds the 'ready' array entries in the JSON cache. Add 'unblock_count: (.unblocks | length)' to each entry alongside the existing 'unblocks: [...]' array. This gives the agent leverage data without recomputing it. Verify with: jq '.artifacts.ready[].unblock_count' ~/.claude/projects/.../memory/status-cache.json after a fresh run.


## Notes

**2026-03-14T03:37:41Z**

Completed: unblock_count field added to each ready item in JSON cache output (line 181 of swain-status.sh). One-line jq change, syntax verified.
