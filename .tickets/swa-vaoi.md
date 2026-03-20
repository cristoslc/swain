---
id: swa-vaoi
status: closed
deps: [swa-gkrm]
links: []
created: 2026-03-20T15:09:17Z
type: task
priority: 2
assignee: cristos
parent: swa-gxjs
---
# Add mmdc fallback logic

If mmdc not on PATH, fall back to inline Mermaid block. Chart still works, just no side-by-side.


## Notes

**2026-03-20T15:13:09Z**

Implemented: _render_quadrant_png returns None if mmdc missing, render_roadmap_markdown falls back to inline Mermaid
