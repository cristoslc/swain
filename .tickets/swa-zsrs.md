---
id: swa-zsrs
status: closed
deps: [swa-kfxm]
links: []
created: 2026-03-14T06:23:13Z
type: task
priority: 2
assignee: cristos
parent: swa-5aq2
tags: [spec:SPEC-038]
---
# Backfill track field into existing artifacts

Add track field to all existing docs/ artifacts (spec, epic, spike, vision, adr, persona, runbook, design, journey). Can use sed/script. Each type gets its assigned track value per ADR-003


## Notes

**2026-03-14T06:32:33Z**

Completed: backfilled track field into all 87 artifacts. 0 TRACK_MISSING warnings after rebuild. All artifact types correctly mapped: SPEC→implementable, EPIC/SPIKE→container, ADR/VISION/JOURNEY/PERSONA/RUNBOOK/DESIGN→standing.
