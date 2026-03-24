---
title: "PURPOSE Migration and VISION-001 Supersession"
artifact: SPEC-164
track: implementable
status: Active
author: cristos
created: 2026-03-24
last-updated: 2026-03-24
priority-weight: high
type: ""
parent-epic: ""
parent-initiative: ""
linked-artifacts:
  - VISION-001
  - VISION-002
  - VISION-003
  - VISION-004
  - VISION-005
depends-on-artifacts: []
addresses: []
evidence-pool: "architecture-intent-evidence-loop@47664e8"
source-issue: ""
swain-do: required
---

# PURPOSE Migration and VISION-001 Supersession

## Problem Statement

VISION-001 ("Swain") has been functioning as two things simultaneously: a **purpose statement** (what swain is and why it exists) and a **vision** (a future state to work toward). Industry frameworks (SVPG, SAFe, Sinek) distinguish these as separate levels — purpose/mission is the identity that rarely changes; vision is the aspirational direction that evolves. Swain's artifact system has no level above VISION, so VISION-001 absorbed both roles.

This creates three problems:

1. **68 artifacts are parented to a statement of identity, not a strategic goal.** VISION-001's children weren't working toward a future state — they were building out what swain already is. This makes "progress toward VISION-001" meaningless as a metric.

2. **The root purpose has no home outside the artifact governance system.** VISION-001 participates in lifecycle phases, specgraph indexing, and dependency graphs. But the project's identity shouldn't be Proposed, Activated, or Superseded in the normal sense — changing it means "this is a different project now."

3. **VISION-001's framing ("decision support") is narrower than what swain has become.** Research (trove: architecture-intent-evidence-loop@47664e8) identified that swain's actual operating principle is the Intent -> Execution -> Evidence -> Reconciliation loop. "Decision support" is one application of the loop; the loop is the general case.

## Desired Outcomes

The operator and agents have a clear, authoritative statement of swain's identity and worldview that:
- Lives outside the artifact governance system (no lifecycle phases, no specgraph indexing)
- Is readable by both humans and agents
- Provides the vocabulary (intent, execution, evidence, reconciliation) that all downstream visions, initiatives, and work items can reference
- Supersedes VISION-001 cleanly, preserving historical accuracy of existing artifact parentage

## External Behavior

### Inputs
- Current VISION-001 content
- Loop framing from trove architecture-intent-evidence-loop@47664e8
- Existing VISION-002 through VISION-005 content (for alignment)

### Outputs
1. `PURPOSE.md` at project root — swain's identity, worldview, and foundational principles
2. AGENTS.md updated to reference PURPOSE.md (so agents load it)
3. VISION-001 transitioned to Superseded with `superseded-by: PURPOSE.md`
4. Existing VISION-001 children re-parented or annotated
5. Updated specgraph/relationship model acknowledging PURPOSE.md as the root anchor

### Constraints
- PURPOSE.md is NOT a swain-design artifact — no frontmatter, no lifecycle table, no artifact ID
- PURPOSE.md changes are project-identity-level events — the file should include a revision history section (manual, not lifecycle-managed)
- Existing children of VISION-001 retain their historical parentage; new work parents to the appropriate peer vision (002-005) or a new vision
- The VISION artifact type is unchanged — it continues to mean "aspirational future state"

## Acceptance Criteria

**AC-1: PURPOSE.md exists and contains the loop framing**
Given the project root
When I read PURPOSE.md
Then it contains: swain's identity statement, the Intent -> Execution -> Evidence -> Reconciliation loop definition, target audience (operator + agents), foundational principles, and a revision history section

**AC-2: PURPOSE.md is human-first, agent-accessible**
Given PURPOSE.md
When read by a human with no project context
Then they understand what swain is and why it exists without reading any other file
And when read by an agent
Then it provides the vocabulary and worldview needed to evaluate any downstream work

**AC-3: AGENTS.md references PURPOSE.md**
Given a fresh agent session
When AGENTS.md is loaded
Then the agent has access to PURPOSE.md content (via include or explicit reference)

**AC-4: VISION-001 is superseded**
Given VISION-001
When the migration is complete
Then VISION-001 status is Superseded
And VISION-001 contains a `superseded-by` reference to PURPOSE.md
And VISION-001 is moved to `docs/vision/Superseded/`
And the lifecycle table records the transition

**AC-5: Existing children have a valid parent path**
Given all artifacts that currently reference VISION-001 in `parent-vision`
When the migration is complete
Then each artifact either:
  (a) has been re-parented to VISION-002, 003, 004, or 005 with a rationale, OR
  (b) has been re-parented to a newly created vision, OR
  (c) retains `parent-vision: VISION-001` with an annotation that this is historical (for completed/abandoned artifacts)

**AC-6: No orphaned active work**
Given all Active or In Progress artifacts
When the migration is complete
Then every active artifact has a parent-vision path to a non-superseded vision

**AC-7: specgraph handles PURPOSE.md**
Given specgraph runs after migration
When it encounters artifacts with `parent-vision: VISION-001`
Then it does not error (VISION-001 still exists, just in Superseded state)
And the tree output shows the supersession clearly

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

### In scope
- Writing PURPOSE.md content
- VISION-001 supersession mechanics
- Re-parenting active children of VISION-001
- AGENTS.md update
- specwatch-ignore entries for the supersession

### Out of scope
- Creating new visions (e.g., Observable Reality) — follow-on work
- ADR formalizing the loop as architectural principle — follow-on work
- Changes to the VISION artifact type definition — not needed
- Changes to specgraph code — VISION-001 in Superseded state is already handled
- Re-parenting completed/abandoned artifacts — they keep historical parentage

### Re-parenting strategy

The 68 children of VISION-001 break down as follows (from the inventory):

**Completed/Abandoned/Superseded artifacts (~35):** Keep `parent-vision: VISION-001`. These were created and finished under that framing. Rewriting history adds no value.

**Active artifacts that clearly map to an existing peer vision:**
- Security-related (EPIC-017, EPIC-023, INITIATIVE-004) → VISION-002 (Safe Autonomy) or VISION-005 (Trustworthy Agent Governance)
- Session/cognitive (EPIC-039, EPIC-042, INITIATIVE-019) → already under VISION-004
- Platform enforcement (INITIATIVE-020) → already under VISION-005

**Active artifacts that are about swain's core capabilities** (artifact system, status, sync, retros, drift detection, etc.): These need a home. Options:
1. Create a new VISION for the artifact/governance system specifically
2. Parent them to an existing vision if the fit is clear
3. Leave them unanchored temporarily and parent as new visions emerge

The operator decides the strategy for bucket 3 during implementation. This spec provides the mechanics; the operator provides the judgment.

## Implementation Approach

### Phase 1: Write PURPOSE.md
Draft the content based on the trove synthesis. Get operator review and approval before proceeding.

### Phase 2: Update AGENTS.md
Add a reference or include for PURPOSE.md. Verify agent sessions load the content.

### Phase 3: Supersede VISION-001
Standard supersession workflow: update status, move to Superseded/, update lifecycle table, add specwatch-ignore entries.

### Phase 4: Re-parent active children
For each active child of VISION-001:
1. Assess which peer vision (002-005) it serves
2. If clear fit: update `parent-vision` frontmatter
3. If unclear: flag for operator decision
4. Commit re-parenting changes with provenance in commit message

### Phase 5: Validate
Run specgraph to verify no broken references. Run specwatch to verify no stale links. Confirm all active artifacts have a non-superseded vision ancestor.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-24 | -- | Initial creation from brainstorming session |
