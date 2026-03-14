---
id: swa-u601
status: closed
deps: []
links: []
created: 2026-03-14T06:02:39Z
type: bug
priority: 1
assignee: cristos
tags: [spec:SPEC-035]
---
# SPEC-035: fix ticket-query TICKETS_DIR unbound variable

Auto-detect .tickets/ when TICKETS_DIR is unset, using same walk-up logic as tk. Respect TICKETS_DIR if already set. Exit non-zero with clear stderr if .tickets/ not found. Spec: SPEC-035.


## Notes

**2026-03-14T06:03:04Z**

Completed: Added find_tickets_dir walk-up logic to ticket-query. All 4 ACs verified: direct invocation outputs JSON, missing .tickets/ gives clean error+exit-1, TICKETS_DIR env respected, specwatch no longer skips tk-sync (shows 'artifacts and tk items are in sync').
