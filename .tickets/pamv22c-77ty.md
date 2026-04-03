---
id: pamv22c-77ty
status: closed
deps: [pamv22c-4u55]
links: []
created: 2026-04-03T02:33:06Z
type: task
priority: 1
assignee: cristos
parent: pamv22c-auly
tags: [spec:SPEC-235, epic:EPIC-055]
---
# Implement drift cleanup and collision handling

Remove stale child links and stale _unparented entries, but fail loudly when a real file or directory blocks a required symlink path.


## Notes

**2026-04-03T02:44:17Z**

Implemented stale-symlink cleanup and preserved collision failure behavior in the materializer. Verified via focused cleanup/collision tests and combined suite (33 passed).
