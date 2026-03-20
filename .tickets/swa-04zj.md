---
id: swa-04zj
status: in_progress
deps: []
links: []
created: 2026-03-20T21:21:27Z
type: task
priority: 1
assignee: cristos
parent: swa-3cbh
tags: [spec:SPEC-114]
---
# Update swain-release for trunk→release squash-merge

Modify swain-release to: (1) tag trunk at HEAD, (2) squash-merge trunk into release, (3) tag release, (4) push both branches and tags. The release branch receives a single commit per release. Tags on trunk preserve lifecycle hash reachability (ADR-012).

