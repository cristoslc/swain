---
id: swa-lv26
status: open
deps: [swa-vttz]
links: []
created: 2026-03-20T21:21:28Z
type: task
priority: 2
assignee: Cristos L-C
parent: swa-3cbh
tags: [spec:SPEC-114]
---
# Update all branch references from main to trunk

Find and update all references to 'main' (as a branch name) across: swain-sync skill, swain-dispatch skill, swain-init skill, AGENTS.md, CI workflows (.github/), ADR body text, and any shell scripts that hardcode origin/main. Use grep to find all occurrences first, then update systematically.

