---
id: swa-dxmt
status: closed
deps: []
links: []
created: 2026-03-14T04:28:09Z
type: feature
priority: 3
assignee: cristos
external-ref: gh-13
tags: [motd, swain-stage]
---
# MOTD: show uncommitted file count

GH #13: Show staged/unstaged file counts in MOTD header. The clickable commit button is exploratory — focus on the file count first.


## Notes

**2026-03-14T06:01:37Z**

Completed: swain-status collect_git() now caches staged/modified/untracked counts via git status --porcelain. swain-motd get_dirty_state() reads these from cache when usable, avoiding git status calls on every MOTD refresh (esp. important during 0.2s fast-refresh while agent is working). Falls back to direct git query when cache is stale.
