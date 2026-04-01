---
id: e0wpls-2avd
status: closed
deps: []
links: []
created: 2026-04-01T03:06:12Z
type: epic
priority: 2
assignee: Cristos L-C
external-ref: SPEC-217
tags: [spec:SPEC-217, epic:EPIC-051]
---
# SPEC-217: Worktree Link Resolution on Merge

Implement .agents/bin/resolve-worktree-links.sh — rewrites detected worktree-specific links in-place. Accepts piped output from detect-worktree-links.sh or standalone file/dir args. Idempotent. UNRESOLVABLE exits 1.


## Notes

**2026-04-01T03:10:26Z**

SPEC-217 complete. resolve-worktree-links.sh at .agents/bin/. All ACs met.
