---
title: "Multi-Vision Initiatives"
artifact: ADR-009
track: standing
status: Active
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
linked-artifacts:
  - EPIC-015
  - EPIC-016
  - EPIC-020
  - EPIC-036
  - INITIATIVE-001
  - INITIATIVE-013
  - SPEC-050
  - VISION-001
  - VISION-002
  - VISION-003
depends-on-artifacts: []
trove: ""
---

# Multi-Vision Initiatives

## Context

The artifact hierarchy model enforces a strict tree: Vision → Initiative → Epic → Spec, with each Initiative having a single `parent-vision`. This worked when Initiatives mapped cleanly to one product direction.

INITIATIVE-013 (Concurrent Session Safety, née Swarm Safety) broke this assumption. Concurrent session isolation serves both VISION-001 (operator tool — two terminal tabs on the same branch) and VISION-002 (agent platform — dispatched agents working in parallel). Forcing single-vision parenting led to either:
- Duplicating the concern across two Initiatives (INITIATIVE-001 under VISION-001, INITIATIVE-013 under VISION-002) with overlapping epics
- Artificially choosing one Vision, leaving the other's needs unrepresented

A related question arose: should Initiatives nest under other Initiatives (sub-initiatives)? INITIATIVE-001 (Worktree-Safe Skill Execution) contained 3 child Epics that all serve INITIATIVE-013's goal. The nesting question was evaluated alongside multi-vision.

## Decision

1. **`parent-vision` becomes a list.** An Initiative may serve multiple Visions. The field changes from a single value to a YAML list:

   ```yaml
   parent-vision:
     - VISION-001
     - VISION-002
   ```

   Single-vision initiatives use a one-element list. Existing single-value `parent-vision` fields are valid and treated as a one-element list (backward compatible).

2. **Priority inheritance uses highest-weight-wins.** When an Initiative serves multiple Visions with different `priority-weight` values, the Initiative inherits the highest weight among its parents (unless explicitly overridden at the Initiative level).

3. **No initiative nesting.** Initiatives do not parent under other Initiatives. The `parent-initiative` field is not added to the Initiative schema. Instead, when an Initiative is absorbed into another, its child Epics are re-parented directly. Informal grouping uses a **Tracks** section in the Initiative document body — prose headings that organize Epics into thematic clusters without adding a hierarchy level.

4. **INITIATIVE-001 is superseded by INITIATIVE-013.** Its child Epics (EPIC-015, EPIC-016, EPIC-020) and Specs (SPEC-050) are re-parented under INITIATIVE-013. INITIATIVE-013 is renamed to "Concurrent Session Safety" and gains both Visions as parents.

## Alternatives Considered

**Sub-initiatives (initiative nesting):** Adding `parent-initiative` to the Initiative schema would let INITIATIVE-001 nest under INITIATIVE-013. This preserves the "worktree hardening is a direction" semantics but adds a hierarchy level (Vision → Initiative → Sub-Initiative → Epic → Spec), complicates chart rendering, and creates ambiguous priority cascading. The Tracks section achieves the same grouping benefit without schema cost.

**Infrastructure Vision (VISION-003):** Creating a third Vision for "swain as a reliable concurrent runtime" would give session isolation a clean single parent. But it fragments the product direction into three Visions when two suffice, and "reliable runtime" is an enabler, not a product direction.

**Keep separate Initiatives:** Maintain INITIATIVE-001 and INITIATIVE-013 as peers with a `depends-on` edge. This preserves the current schema but perpetuates the artificial split that prompted this decision. The overlapping epics and duplicated concern are the status quo problem.

## Consequences

**Positive:**
- Initiatives that genuinely serve multiple product directions are represented honestly, not forced into one parent
- The hierarchy stays two levels deep (no sub-initiatives), keeping chart rendering and priority cascading simple
- Tracks section provides flexible grouping without schema rigidity
- INITIATIVE-001/013 consolidation eliminates the duplicated concurrent-safety concern

**Accepted downsides:**
- `chart.sh` and any tooling that assumes single `parent-vision` needs updating to handle lists
- Multi-vision initiatives may be overused — operator discipline required to keep it for genuinely cross-cutting concerns, not convenience
- Flattening loses the explicit "worktree hardening is a strategic direction" framing (mitigated by Tracks)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | -- | Decision made during EPIC-036 creation; INITIATIVE-001/013 consolidation |
