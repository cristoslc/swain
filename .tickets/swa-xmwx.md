---
id: swa-xmwx
status: closed
deps: []
links: []
created: 2026-03-14T06:38:00Z
type: task
priority: 2
assignee: cristos
parent: swa-bzm2
tags: [spec:SPEC-040]
---
# Gate spinner tick on animationStyle != none

When none, skip _tick_spinner; show static symbol; satisfy AC2


## Notes

**2026-03-14T06:38:36Z**

Completed: _tick_spinner returns early when ANIMATION_STYLE=='none' or FRAMES empty; _render_agent uses static ● symbol when FRAMES empty (none mode)
