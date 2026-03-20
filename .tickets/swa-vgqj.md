---
id: swa-vgqj
status: open
deps: [swa-mo61]
links: []
created: 2026-03-20T03:00:36Z
type: task
priority: 2
assignee: Cristos L-C
external-ref: SPEC-096
parent: swa-j7i1
tags: [spec:SPEC-096]
---
# SPEC-096: design-check.sh — Blob SHA Drift Detection

New script: reads sourcecode-refs, performs blob SHA comparison, reports CURRENT/STALE/MOVED/BROKEN. Exit codes 0/1/2. Includes --repin mode. Depends on SPEC-094 schema.

