---
title: "Standalone Placement for Standing-Track Artifact Types"
artifact: ADR-026
track: standing
status: Active
author: Cristos L-C
created: 2026-04-03
last-updated: 2026-04-03
linked-artifacts:
  - SPEC-249
  - EPIC-058
  - ADR-027
depends-on-artifacts: []
evidence-pool: ""
---

# Standalone Placement for Standing-Track Artifact Types

## Context

The materializer gives each artifact a `placement_state`: `placed` (has parent), `root` (Vision), or `unparented` (all others). `unparented` creates repair-surface directories.

Standing-track types (RETRO, ADR, JOURNEY, PERSONA, RUNBOOK, DESIGN, TRAIN) sit alongside the hierarchy, not in it. They rarely have parents. But the materializer treated them like orphaned SPECs -- making repair surfaces that implied something was broken.

RETROs were the worst case. Their date-slug IDs (`RETRO-2026-03-22-...`) broke `_extract_type`, which expected `-\d+` at the end. Each retro got its own type directory -- 19 zombie directories that came back after every build.

## Decision

Add a `standalone` placement state for parentless standing-track artifacts. Standalone artifacts:

1. **Skip hierarchy materialization** -- no parent symlinks, no `_unparented` surfaces.
2. **Still get relationship symlinks** -- `_Related/` and `_Depends-On/` based on `linked-artifacts` and `depends-on` edges.
3. **Stay in the projection** -- visible in `chart.sh`, graph queries, lenses, and recommendations.

Standing-track types with a parent (e.g., a DESIGN under an EPIC) still get `placed`. `standalone` only applies when `direct_parent` is `None`.

Also fix `_extract_type` to match the uppercase prefix before the first dash-digit boundary (`^([A-Z]+)-`) instead of stripping trailing `-\d+`.

## Alternatives Considered

1. **Gitignore the zombie directories.** Treats the symptom. Directories still get built on every run; other tools still see them.

2. **Hardcode a RETRO-only exclusion.** Doesn't cover ADRs, Journeys, Personas, or Runbooks. Each new standing type would need its own special case.

3. **Filter standing types from the projection.** Too aggressive -- standing types have relationship edges used by graph queries and symlinks.

## Consequences

- No more zombie directories. Standing-track artifacts get relationship symlinks in their real location.

- `_extract_type` handles any ID with an uppercase prefix, including future non-numeric schemes.

- Code checking for `"unparented"` to find parentless artifacts will miss standing types. It must also check `"standalone"`.

- Standalone artifacts with no relationship edges produce no filesystem output. They are only visible through `chart.sh`.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-03 | 761829e | Implementation landed; ADR records decision retroactively |
