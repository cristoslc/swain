---
id: pamv22c-4u55
status: closed
deps: []
links: []
created: 2026-04-03T02:33:06Z
type: task
priority: 1
assignee: cristos
parent: pamv22c-auly
tags: [spec:SPEC-235, epic:EPIC-055]
---
# Hook reconciliation into mutating flows

Identify the workflows that rebuild graph state and wire the hierarchy materializer to run after chart rebuilds in those paths.


## Notes

**2026-04-03T02:44:17Z**

Hooked hierarchy materialization into chart build so canonical graph rebuilds now project direct-child views. Verified via chart wrapper test and combined suite (33 passed).
