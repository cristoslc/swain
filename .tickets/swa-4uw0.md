---
id: swa-4uw0
status: closed
deps: []
links: []
created: 2026-03-14T04:17:32Z
type: bug
priority: 1
assignee: cristos
tags: [spec:SPEC-037]
---
# Fix specgraph ready standing-track leak

do_ready uses inline status regex instead of type-aware is_resolved, causing Active ADRs/PERSONAs/JOURNEYs/VISIONs to appear as actionable work


## Notes

**2026-03-14T04:17:39Z**

Fixed: added is_resolved helper to do_ready() jq filter, matching the pattern already used by do_next() and do_overview(). Verified Active ADRs/PERSONAs/JOURNEYs/VISIONs no longer appear in ready output.
