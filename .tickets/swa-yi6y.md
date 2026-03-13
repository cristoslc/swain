---
id: swa-yi6y
status: closed
deps: [swa-k4tr]
links: []
created: 2026-03-13T21:33:01Z
type: task
priority: 1
assignee: cristos
parent: swa-9tg7
tags: [spec:SPEC-030]
---
# GREEN: Implement frontmatter parser

Regex-based YAML frontmatter extraction in parser.py. Handle scalar fields, list fields (depends-on-artifacts, linked-artifacts, etc.), full-format fields (addresses with JOURNEY-NNN.PP-NN). Description extraction: question > description > first body paragraph.


## Notes

**2026-03-13T21:37:58Z**

parser.py implemented during scaffold; 26 unit tests pass.
