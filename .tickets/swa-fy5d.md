---
id: swa-fy5d
status: closed
deps: [swa-wjw9, swa-s4zy, swa-t3ig]
links: []
created: 2026-03-14T04:59:29Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-ul7c
tags: [spec:SPEC-033]
---
# Integration: verify xref section in swain-status output

Run swain-status --refresh and verify Cross-Reference Gaps section appears with real discrepancies from the live repo. Verify compact mode shows xref count. Verify clean state shows no section.


## Notes

**2026-03-14T05:25:44Z**

Completed: integration verified — xref section appears in full output with 67 entries, compact shows 'xref: 67 gaps', JSON cache has xref_gap_count=67. Fixed bug: missing_reciprocal jq expression used .target // . but entries are objects with .from key; changed to .from. Committed fix(swain-status): fix xref missing_reciprocal rendering — swa-fy5d.
