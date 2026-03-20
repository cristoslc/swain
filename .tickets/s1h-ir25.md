---
id: s1h-ir25
status: closed
deps: [s1h-am0i]
links: []
created: 2026-03-20T15:11:03Z
type: task
priority: 2
assignee: cristos
parent: s1h-wrgp
tags: [spec:SPEC-103]
---
# Add auto-relink to phase-transition workflow

Update swain-design phase-transitions.md: after git mv, grep all docs/ files for links pointing to the moved artifact's old path, run relink.sh to update them, stage the changes in the same commit.


## Notes

**2026-03-20T15:22:14Z**

Phase-transitions.md step 2a updated with concrete relink.sh invocation using find-based discovery. Stages relinked files in same commit as git mv.
