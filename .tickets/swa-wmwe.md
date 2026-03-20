---
id: swa-wmwe
status: open
deps: [swa-7abc]
links: []
created: 2026-03-20T15:09:56Z
type: task
priority: 2
assignee: Cristos L-C
parent: swa-f0pa
tags: [spec:SPEC-103]
---
# Add auto-relink to phase-transition workflow

Update swain-design phase-transitions.md: after git mv, grep all docs/ files for links pointing to the moved artifact's old path, run relink.sh to update them, stage the changes in the same commit.

