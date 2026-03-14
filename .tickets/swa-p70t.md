---
id: swa-p70t
status: closed
deps: []
links: []
created: 2026-03-14T04:28:09Z
type: bug
priority: 0
assignee: Cristos L-C
external-ref: gh-47
tags: [bug, swain-status]
---
# Fix jq is_resolved errors in swain-status

GH #47/#45: collect_artifacts passes string to is_resolved which expects object. Fix two call sites: remove .status prefix before is_resolved, and use .value instead of .value.status


## Notes

**2026-03-14T04:29:19Z**

Already fixed in c3872da — closed GH #47 and #45
