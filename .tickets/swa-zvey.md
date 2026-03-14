---
id: swa-zvey
status: closed
deps: []
links: []
created: 2026-03-13T23:28:31Z
type: task
priority: 1
assignee: cristos
parent: swa-1wrf
tags: [spec:SPEC-032]
---
# RED: Full xref pipeline tests

Write failing tests for the end-to-end xref pipeline. Given a set of artifacts with bodies and frontmatter, compute per-artifact xref results: body_not_in_frontmatter, frontmatter_not_in_body, missing_reciprocal. Test that the output matches the cache schema from the spec.


## Notes

**2026-03-14T04:46:19Z**

Completed: RED phase done — tests written and all 47 pass as of commit 5a4386c
