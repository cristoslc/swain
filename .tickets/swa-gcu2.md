---
id: swa-gcu2
status: closed
deps: []
links: []
created: 2026-03-14T04:28:09Z
type: task
priority: 2
assignee: Cristos L-C
external-ref: gh-46
tags: [specwatch]
---
# Suppress superseded-ADR warnings for closed artifacts in specwatch

GH #46: specwatch warns when closed artifacts reference superseded ADRs. Only warn for active-phase artifacts, skip closed/terminal ones.


## Notes

**2026-03-14T04:29:44Z**

Fixed in 38d7967 — closes GH #46
