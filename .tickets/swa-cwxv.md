---
id: swa-cwxv
status: open
deps: []
links: []
created: 2026-04-14T01:39:22Z
type: task
priority: 2
assignee: Cristos L-C
parent: swa-qc20
tags: [spec:SPEC-305]
---
# Remove swain-doctor symlink repair (check 12 + SPEC-290)

Delete check 12 and the SPEC-290 repair pass from swain-doctor. With all dirs tracked per ADR-042, symlink repair is dead code. Test: swain-doctor runs without error. No symlink repair is attempted.

