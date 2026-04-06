---
title: "Artifact Model Correction — Three Tracks with Correct Types"
artifact: ADR-025
track: standing
status: Accepted
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
linked-artifacts:
  - ADR-003
  - EPIC-056
depends-on-artifacts: []
evidence-pool: "docs/ directory inventory (2026-04-04)"
---

# Artifact Model Correction — Three Tracks with Correct Types

## Context

ADR-003 established three lifecycle tracks (Implementable, Container, Standing) but misclassified artifact types. The current model has:

- **Container:** EPIC, SPIKE (incorrect — SPIKE is singular research)
- **Implementable:** SPEC only (missing SPIKE)
- **Standing:** VISION, JOURNEY, PERSONA, ADR, RUNBOOK, DESIGN (missing INITIATIVE, TRAIN, RETRO)

This causes downstream problems:
- Worktree naming logic treats SPIKE as multi-faceted (asks for purpose slug) when it's singular
- INITIATIVE has no track assignment despite grouping multiple EPICs
- Collision detection rules are wrong for affected types

The artifact model is foundational to swain's chart rendering, priority inheritance, worktree isolation, and skill routing. Misclassification propagates errors throughout the system.

## Evidence

**Directory inventory (2026-04-04):**
| Directory | Count | Track (proposed) |
|-----------|-------|-----------------|
| docs/spec/ | 247 | Implementable |
| docs/spike/ | 5 | Implementable |
| docs/epic/ | 59 | Container |
| docs/initiative/ | 14 | Container |
| docs/vision/ | 16 | Standing |
| docs/journey/ | 4 | Standing |
| docs/persona/ | 4 | Standing |
| docs/adr/ | 27 | Standing |
| docs/design/ | 17 | Standing |
| docs/runbook/ | 4 | Standing |
| docs/train/ | — | Standing (SPEC-091 defines) |
| docs/swain-retro/ | 19 | Standing (RETRO artifacts) |

**Frontmatter analysis:** 1,305 artifacts total across 12 types.

## Decision

**Correct the artifact type → track mapping:**

| Track | Types | Characteristics | Collision | Naming |
|-------|-------|-----------------|-----------|--------|
| **Implementable** | SPEC, SPIKE | Singular, atomic work units | Hard (one session per artifact) | Use artifact title |
| **Container** | EPIC, INITIATIVE | Groups multiple children (EPICs contain Specs, INITIATIVEs contain EPICs) | Soft (multi-faceted, purpose slug) | `${purpose-slug}-${timestamp}-${ID}-${title}` |
| **Standing** | VISION, JOURNEY, PERSONA, ADR, RUNBOOK, DESIGN, TRAIN | Persistent constraints, reference docs | Hard (one session per artifact; confirmed no concurrent sessions) | Use artifact title |
| **Byproduct** | RETRO | Session learnings, created post-hoc | N/A (named after parent artifact or session purpose) | N/A |

### Track Definitions

**Implementable (SPEC, SPIKE):**
- Singular, atomic work that completes in one or few sessions
- Has clear completion criteria
- Collapses to Complete terminal state
- **Naming:** `${ARTIFACT_ID}-${slugified-title}` (e.g., `spec-054-worktree-isolation`)
- **Collision:** Hard — block if worktree already exists for this artifact

**Container (EPIC, INITIATIVE):**
- Groups multiple child artifacts (EPICs contain Specs, INITIATIVEs contain EPICs)
- Multi-faceted — multiple concurrent sessions may work on different facets
- Completes when all children complete
- **Naming:** `${purpose-slug}-${timestamp}-${ARTIFACT_ID}-${slugified-title}` (e.g., `migration-20260404-epic-012-materialized-parenting`)
- **Collision:** Soft — warn if similar worktree exists, offer resume or create new

**Standing (VISION, JOURNEY, PERSONA, ADR, RUNBOOK, DESIGN, TRAIN):**
- Persistent reference/constraint artifacts
- Don't "complete" — become Retired or Superseded
- Rarely have concurrent sessions (one person updates at a time)
- **Naming:** `${ARTIFACT_ID}-${slugified-title}` (e.g., `vision-001-safe-autonomy`)
- **Collision:** Hard — block if worktree already exists

**Byproduct (RETRO):**
- Session learnings captured post-hoc
- Not a session goal — created after work completes
- Tied to parent artifact (SPEC, EPIC, SPIKE) or cross-cutting incident
- **Naming:** N/A — worktree named after parent artifact or session purpose
- **Collision:** N/A — inherits collision rules from parent artifact

### Key Changes from ADR-003

| Change | Rationale |
|--------|-----------|
| **SPIKE → Implementable** | SPIKE is singular research task, not a container (confirmed Q1) |
| **INITIATIVE → Container** | INITIATIVE groups multiple EPICs (ADR-009 multi-vision initiatives) |
| **TRAIN → Standing** | TRAIN is reference/training material (SPEC-091) |
| **RETRO → Byproduct** | RETRO is session byproduct, not primary goal (named after parent or session purpose) |
| **Clarify collision rules** | Implementable/Standing = hard, Container = soft (confirmed Q4) |
| **Container naming includes title** | `${purpose-slug}-${timestamp}-${ID}-${title}` format (confirmed Q5) |

## Alternatives Considered

**A. Keep ADR-003 as-is, add exceptions.** Document that SPIKE is "actually implementable" and INITIATIVE is "actually container" in downstream specs. Rejected: creates ongoing confusion, every tool needs special cases.

**B. Make SPIKE a Container.** Argue that SPIKEs can have multiple facets. Rejected: SPIKEs are time-boxed research with singular questions. If multi-faceted, should be multiple SPIKEs or an EPIC.

**C. Merge INITIATIVE into EPIC.** Flatten hierarchy to Vision → EPIC → Spec. Rejected: loses strategic grouping layer. INITIATIVEs coordinate across multiple EPICs (ADR-009 multi-vision initiatives).

## Consequences

**Positive:**
- Worktree naming logic works correctly (no asking for purpose slug on SPECs)
- Collision detection matches artifact semantics
- Chart rendering can correctly inherit priority (Container → Implementable cascade)
- Skill routing can branch on track (implementable = autonomous, container = coordination)

**Negative:**
- **Breaking change** — existing SPIKE/INITIATIVE artifacts need reclassification
- Tooling (chart.sh, specgraph, swain-status) needs track lookup updates
- Frontmatter validation needs updating
- Directory structure unchanged (types stay in their folders)

**Migration:**
- No directory renames needed (type folders unchanged)
- Frontmatter `track:` field needs updating for SPIKE/INITIATIVE artifacts
- chart.sh track lookup needs correction
- swain-design skill needs updated type→track mapping

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-04 | — | Drafted from worktree isolation redesign conversation |
| Accepted | 2026-04-04 | — | Operator interview completed; all questions confirmed |
