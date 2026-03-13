---
title: "Externalize Skill Reference Content"
artifact: SPEC-015
status: Complete
type: enhancement
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
parent-epic: EPIC-006
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
linked-artifacts:
  - SPIKE-010
  - SPIKE-011
depends-on-artifacts: []
---

# Externalize Skill Reference Content

## Problem Statement

The top 3 skills by context footprint (swain-design 6,319 tokens, swain-doctor 5,509, swain-do 5,019) inline substantial reference content that the agent only needs during specific sub-workflows. This consumes context on every invocation whether or not that content is relevant.

SPIKE-010 identified the content categories; SPIKE-011 confirmed that externalization (Strategy A) is the primary reduction lever, achieving 48-55% reduction for the top 3 skills.

## External Behavior

After this change, SKILL.md files for swain-design, swain-doctor, and swain-do are smaller. Reference-only content lives in `references/` files, loaded on demand via "Read [references/X] before doing Y" directives. No skill behavior changes — only the packaging of instructions.

### Content to externalize

**swain-design:**
- ER diagram and artifact relationship model → `references/relationship-model.md`
- Tooling table → already partially done; complete the migration
- Lifecycle table format → `references/lifecycle-format.md`
- Index maintenance rules → `references/index-maintenance.md`

**swain-doctor:**
- Platform dotfolder cleanup procedures (~1,625 tokens of bash) → `references/platform-cleanup.md`
- Legacy skill cleanup procedures → `references/legacy-cleanup.md`

**swain-do:**
- Escalation procedures and triage table (~650 tokens) → `references/escalation.md`
- Anti-rationalization table → `references/tdd-enforcement.md`
- Plan ingestion details → `references/plan-ingestion.md`

### Content to keep in SKILL.md

- Operating rules and workflow entry points
- Term mapping tables (swain-do)
- Phase transition workflow steps (swain-design)
- Bootstrap and configuration (swain-do)

## Acceptance Criteria

- **Given** swain-design SKILL.md, **when** measured, **then** it is ≤2,800 tokens (down from 6,319)
- **Given** swain-doctor SKILL.md, **when** measured, **then** it is ≤2,300 tokens (down from 5,509)
- **Given** swain-do SKILL.md, **when** measured, **then** it is ≤2,200 tokens (down from 5,019)
- **Given** externalized content, **when** the relevant sub-workflow fires, **then** the agent reads the reference file and completes the workflow correctly
- **Given** any skill invocation, **when** no sub-workflow fires, **then** no reference files are loaded (no wasted reads)

## Scope & Constraints

- Only moves content; does not rewrite, compress, or delete content (that's SPEC-016)
- Reference files must be self-contained — readable without SKILL.md context
- SKILL.md retains directive pointers with clear trigger conditions

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-13 | — | Initial creation from EPIC-006 decomposition |
| Implemented | 2026-03-13 | da6cb61 | Transitioned — all 3 skills externalized to reference files |
