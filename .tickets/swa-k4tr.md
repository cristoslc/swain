---
id: swa-k4tr
status: closed
deps: [swa-8mpk]
links: []
created: 2026-03-13T21:33:00Z
type: task
priority: 1
assignee: cristos
parent: swa-9tg7
tags: [spec:SPEC-030]
---
# RED: Frontmatter parser tests

Write tests for extract_frontmatter() against fixture files: all field types (scalar, list, full-format addresses), question vs description priority, missing fields, empty frontmatter.


## Notes

**2026-03-13T21:37:58Z**

26 parser tests pass: scalar fields, list fields, empty lists, quoted values, addresses format, source-issue format, body extraction, description priority (question>description>body), title prefix stripping, truncation.
