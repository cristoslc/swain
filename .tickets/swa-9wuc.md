---
id: swa-9wuc
status: open
deps: []
links: []
created: 2026-03-20T15:09:56Z
type: task
priority: 2
assignee: Cristos L-C
parent: swa-f0pa
tags: [spec:SPEC-103]
---
# Build resolve-artifact-link.sh

Given an artifact ID (e.g., SPEC-045) and a source file path, locate the artifact on disk via find and return the relative path from source to target. Handle all 11 artifact type prefixes. Exit 1 if not found.

