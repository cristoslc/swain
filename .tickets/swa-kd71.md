---
id: swa-kd71
status: open
deps: []
links: []
created: 2026-03-20T00:42:36Z
type: epic
priority: 2
assignee: Cristos L-C
external-ref: SPEC-091
---
# TRAIN Artifact Type Implementation Plan

Ingested from docs/superpowers/plans/2026-03-19-train-artifact-type.md. Goal: Add TRAIN-NNN as a new standing artifact type for product documentation, with enriched `linked-artifacts` for commit-pinned staleness tracking.. Architecture: TRAIN is a standing-track artifact (like Persona, Design, Runbook) with Diataxis-based typing (how-to, reference, quickstart). Enriched `linked-artifacts` entries support `rel` tags and commit pinning. A new `train-check.sh` script detects dependency drift. Phase transition hooks nudge TRAIN creation/updates on SPEC and EPIC completion..

