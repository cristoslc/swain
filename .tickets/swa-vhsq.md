---
id: swa-vhsq
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
# Refactor specgraph.py: dynamic track-based resolution

Update Python specgraph resolved.py to read track from artifact frontmatter, look up resolution rule from tracks index. Replace _STANDING_TYPES hardcoded list. Add fallback for missing track field


## Notes

**2026-03-14T06:31:47Z**

Completed: updated resolved.py (track param + _infer_track fallback), graph.py (track in node dict), queries.py (_node_is_resolved passes track). 33 integration test failures verified as pre-existing, not introduced by SPEC-038.
