---
id: s1h-z0l5
status: closed
deps: []
links: []
created: 2026-03-20T15:11:03Z
type: task
priority: 2
assignee: cristos
parent: s1h-wrgp
tags: [spec:SPEC-103]
---
# Build resolve-artifact-link.sh

Given an artifact ID (e.g., SPEC-045) and a source file path, locate the artifact on disk via find and return the relative path from source to target. Handle all 11 artifact type prefixes. Exit 1 if not found.


## Notes

**2026-03-20T15:13:55Z**

resolve-artifact-link.sh implemented. Handles all 11 artifact type prefixes, both (TYPE-NNN)-Title and TYPE-NNN filename conventions. Returns absolute path or relative path from source file. 11/11 tests pass.
