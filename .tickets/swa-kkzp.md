---
id: swa-kkzp
status: closed
deps: []
links: []
created: 2026-03-13T23:05:37Z
type: task
priority: 2
assignee: cristos
parent: swa-01mh
tags: [spec:SPEC-034]
---
# RED: architecture overview diagram check tests

Write tests for a function that checks whether an architecture-overview.md contains a diagram: mermaid block, image ref, or diagram heading. Test positive cases (mermaid, image, heading) and negative (prose only).


## Notes

**2026-03-13T23:07:37Z**

15 tests pass: mermaid blocks, markdown images, HTML images, diagram headings (Diagram, Architecture Diagram, System Diagram, C4), prose-only detection, code block exclusion, vision/epic level discovery, missing diagram flagging.
