---
id: swa-azjr
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
# Add animationStyle setting support

Read stage.motd.animationStyle; support clockwise (default), none, unknown→clockwise fallback


## Notes

**2026-03-14T06:38:36Z**

Completed: added ANIMATION_STYLE constant reading stage.motd.animationStyle (default: clockwise), _STYLE_MAP mapping values to frame sets, unknown values fall back to braille clockwise
