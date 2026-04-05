---
title: "Materialized Artifact Parenting View"
artifact: EPIC-060
track: container
status: Complete
author: cristos
created: 2026-04-02
last-updated: 2026-04-03
parent-vision: VISION-001
parent-initiative: INITIATIVE-002
priority-weight: high
success-criteria:
  - Parent-child hierarchy can be browsed directly inside lifecycle-scoped artifact folders without changing frontmatter authority
  - `chart` is the only hierarchy interface the materializer consumes
  - Each artifact materializes exactly once as a direct child under its narrowest valid parent
  - Unparented artifacts appear in per-type `_unparented/` repair surfaces with explanatory README files
  - Reconciliation removes stale symlinks and repairs drift automatically after hierarchy changes
depends-on-artifacts:
  - ADR-022
addresses: []
evidence-pool: ""
---

# Materialized Artifact Parenting View

## Goal / Objective

Show the artifact hierarchy in the docs tree as a parent-first view. A reader opens one folder, sees its own files and child folders, and can keep walking down the tree.

## Desired Outcomes

Operators and agents can inspect one parent in one place. The view stays trustworthy because `chart` rebuilds it.

## Progress

<!-- Auto-populated from session digests. See progress.md for full log. -->

## Scope Boundaries

**In scope:**
- machine-readable hierarchy output from `chart`
- child-folder symlinks in lifecycle folders
- narrowest-parent placement and duplicate suppression
- `_unparented/` repair surfaces and README files
- automatic cleanup after hierarchy changes

**Out of scope:**
- linked-artifact or dependency views in the child tree
- replacing canonical artifact files or folder rules
- approval steps before reconciliation

## Child Specs

- SPEC-261: Specgraph Hierarchy Projection Output (Complete)
- SPEC-262: Lifecycle-Scoped Materialized Child Views (Complete)
- SPEC-263: Automatic Hierarchy Reconciliation (Complete)

## Key Dependencies

- ADR-022 sets `chart` as the canonical hierarchy interface
- DESIGN-013 defines the materialization contract
- DESIGN-014 defines placement and `_unparented/` rules

## Retrospective

**Terminal state:** Complete
**Period:** 2026-04-02 - 2026-04-03
**Related artifacts:** ADR-022, DESIGN-013, DESIGN-014, SPEC-261, SPEC-262, SPEC-263, SPEC-236, SPEC-264

### Summary

This EPIC shipped the parent-first hierarchy view inside artifact folders. `chart` now projects the hierarchy, builds child-folder symlinks, writes `_unparented` repair surfaces, and cleans stale links.

The work also exposed two process bugs. Artifact ID allocation missed untracked work in other worktrees. That created collisions. Session gating also let mutating work begin before startup. Both became follow-on bug specs.

### Reflection

The design held up once the narrowest-parent rule and the output-only symlink rule were clear. Treating the materialized tree as a disposable view kept the implementation simple. It also made re-parenting work with normal rebuilds.

The main surprise was how fast duplicate artifact IDs polluted the new hierarchy view. That was not a materializer bug. The new view exposed a repo integrity bug. Hard failure on real duplicate IDs and the renumbering tooling turned that into a guardrail.

Another good correction was to make graph discovery skip symlinked paths on purpose. That avoids a future regression. It also keeps collision checks tied to canonical files only.

### Learnings Captured

| Item | Type | Summary |
|------|------|---------|
| SPEC-236 | SPEC candidate | Artifact ID allocation must see untracked artifacts in other worktrees before assigning a new ID. |
| SPEC-264 | SPEC candidate | Session gating must offer startup before any mutating work begins. |

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-02 | — | Initial creation |
| Complete | 2026-04-02 | — | Child specs shipped. The hierarchy view now rebuilds from `chart` and materializes on disk |
