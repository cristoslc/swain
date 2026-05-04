---
title: "Where are ADR alignment checks invoked in swain workflows?"
artifact: SPIKE-070
track: container
status: Complete
author: cristos
created: 2026-04-13
last-updated: 2026-04-13
question: "Which swain workflow steps invoke an ADR alignment check (adr-check.sh), what do those checks validate, and where are the gaps where ADR alignment should be checked but is not?"
gate: Pre-MVP
risks-addressed:
  - ADR compliance is checked inconsistently, allowing architectural drift
  - Changes to SPECs or tickets bypass ADR alignment when they should not
evidence-pool: ""
---

# Where are ADR alignment checks invoked in swain workflows?

## Summary

**Go.** adr-check.sh runs in 3 of 6 relevant workflow points (creation, transition, sync) and checks frontmatter linkage only — no content analysis. Key gaps: ticket operations (swain-do), non-transition edits (SPEC, EPIC, VISION), task completion, and retros all skip ADR alignment. The SPEC-307 drift check (ticket → SPEC, SPEC → parent) is complementary: it catches scope creep within the artifact hierarchy, while ADR checks catch architectural decision violations. Both are needed.

## Question

Which swain workflow steps invoke an ADR alignment check (`adr-check.sh`), what do those checks validate, and where are the gaps where ADR alignment should be checked but is not?

## Go / No-Go Criteria

- Every call site of `adr-check.sh` is identified with the invoking skill, step, and trigger condition.
- The validation rules inside `adr-check.sh` are cataloged (what it checks, what it skips).
- Gaps are identified where ADR alignment is relevant but not currently checked.

## Pivot Recommendation

If `adr-check.sh` is only called in one place, pivot to embedding its logic more broadly rather than adding a new check script.

## Findings

### 1. Where adr-check.sh is invoked

| Invocation point | Skill / script | Trigger | What it checks |
|------------------|---------------|---------|----------------|
| **swain-design SKILL.md step 8** | swain-design | Artifact creation — after step 7 (parent ref validation), before step 9 (specwatch). **All artifact types** (SPEC, EPIC, VISION, ADR, etc.) | Frontmatter linkage + content overlap against Adopted ADRs |
| **swain-design phase transitions** | swain-design | Phase transitions to Active, Ready, In Progress, or Complete | Same as above — ADR compliance check before committing |
| **swain-sync** | swain-sync | After staging changes, before commit | ADR compliance check on modified artifacts |
| **Pre-tool hook (Gemini)** | `.gemini/hooks/pretool-adr-gate.sh` | Before tool use in Gemini runtime | ADR gate — blocks or warns if adr-check fails |
| **swain-design audits** | swain-design | On operator request ("audit") | Runs adr-check against every non-ADR artifact, plus content-level review |

### 2. What adr-check.sh validates

The script performs **frontmatter-level** checks only (no content analysis):

- **RELEVANT**: Adopted ADRs whose scope overlaps the artifact. Agent must do content-level review.
- **DEAD_REF**: Artifact references a Retired or Superseded ADR. Agent must check against replacement.
- **STALE**: ADR adopted after the artifact was last updated. Artifact may need revision.

Exit codes: 0 = clean, 1 = advisory (non-stale RELEVANT), 2 = actionable (DEAD_REF or stale), 3 = error.

### 3. Where ADR alignment is NOT checked

| Gap | Why it matters | Current risk |
|-----|---------------|-------------|
| **Ticket create/edit/close** | Tickets are where scope drift enters. A ticket under a SPEC may describe work outside the SPEC's acceptance criteria or contradict an ADR. | swain-do has zero ADR awareness. Tickets can freely drift from ADR decisions. |
| **SPEC edit (non-transition)** | adr-check runs on SPEC creation and phase transitions, but not on plain edits to an Active SPEC. An edit that broadens scope or contradicts an ADR goes unchecked. | A SPEC can silently drift from its parent EPIC or relevant ADRs between transitions. |
| **EPIC/VISION/Initiative edit (non-transition)** | Same gap as SPEC edits, at higher levels. | Architectural drift accumulates at the strategy layer without detection. |
| **swain-do task completion** | When a task completes, no check validates that the implementation stayed aligned with the SPEC's ADR-linked constraints. | Implementation can drift from ADR decisions without signal until audit or retro. |
| **swain-retro completion** | Retros document learnings but don't check whether past decisions need ADR updates. | A retro may surface a decision change without triggering an ADR revision. |

### 4. Summary

ADR alignment checks run in **3 of 6** relevant workflow points: artifact creation, phase transitions, and sync. They do not run on edits, ticket operations, task completion, or retros. The checks themselves are frontmatter-only — content-level review requires agent judgment, which is only prompted during formal audits.

The SPEC-307 drift check (ticket → SPEC, SPEC → parent) is complementary but different: it checks scope alignment against parent artifacts, not ADR compliance. Both are needed. ADR checks catch architectural decision violations; drift checks catch scope creep within the artifact hierarchy.
## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-13 | — | Initial creation |
| Complete | 2026-04-13 | — | All findings populated. Go: gaps identified, complementary to SPEC-307. |
