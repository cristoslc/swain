---
id: swa-0mm5
status: open
deps: [swa-ki28]
links: []
created: 2026-04-14T01:40:39Z
type: task
priority: 2
assignee: Cristos L-C
parent: swa-qc20
tags: [spec:SPEC-305]
---
# Doctor migration check: .agents/ → .swain/

New doctor check that detects a stale .agents/ directory and old .agents/ gitignore block. On detection, offer to: (1) move runtime files (.agents/bin/, .agents/session.json, .agents/hook-state/, .agents/chart-cache/, .agents/search-snapshots/, .agents/specwatch-ignore) to .swain/ equivalents, (2) update the gitignore block (.agents/ → .swain/session/), (3) track .swain/ and .swain-init. This replaces the old bin-auto-repair and gitignore-skill-folders checks. Runs during normal doctor pass and also at the end of swain-init.

