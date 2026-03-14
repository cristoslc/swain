---
id: swa-urt6
status: closed
deps: [swa-uvc4]
links: []
created: 2026-03-14T06:23:13Z
type: task
priority: 2
assignee: cristos
parent: swa-5aq2
tags: [spec:SPEC-038]
---
# Refactor specgraph.sh: dynamic track-based is_resolved

Update do_build to extract 'track' from each artifact's frontmatter. Replace RESOLVED_RE and hardcoded is_resolved jq helper with dynamic lookup against tracks index. Add fallback: infer from type name + warn when track missing


## Notes

**2026-03-14T06:27:21Z**

Completed: do_build now extracts 'track' from frontmatter (with type-based fallback + TRACK_MISSING warning). All is_resolved defs now use (.track // 'implementable') == 'standing' instead of hardcoded type regex. ready output identical to pre-refactor baseline (verified).
