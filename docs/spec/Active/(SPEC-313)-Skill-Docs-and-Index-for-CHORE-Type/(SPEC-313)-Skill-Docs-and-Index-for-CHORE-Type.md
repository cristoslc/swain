---
title: "Skill Docs and Index for CHORE Type"
artifact: SPEC-313
track: implementable
status: Active
author: cristos
created: 2026-04-14
last-updated: 2026-04-14
type: enhancement
parent-epic: EPIC-077
linked-artifacts:
  - [SPEC-312](../(SPEC-312)-Python-Tooling-Support-for-CHORE-Type/(SPEC-312)-Python-Tooling-Support-for-CHORE-Type.md)
  - [ADR-045](../../../adr/Active/(ADR-045)-Chores-As-A-Lightweight-Artifact-Type/(ADR-045)-Chores-As-A-Lightweight-Artifact-Type.md)
depends-on-artifacts:
  - SPEC-312
addresses:
  - PERSONA-002
swain-do: required
---

# Skill Docs and Index for CHORE Type

## Problem Statement

The swain-design SKILL.md documents artifact types and their templates. It doesn't include CHORE. The lifecycle tracks reference omits it. No `list-chores.md` index exists.

## Scope

### 1. `swain-design/SKILL.md` — Type table

Add a CHORE row to the artifact type table. Also add CHORE to the "Choosing the right artifact type" guidance ("small cleanup" → CHORE).

### 2. `swain-design/SKILL.md` — Bare-ID regex

Add `CHORE` to the regex in step 6.5: `(SPEC|EPIC|...|TRAIN|CHORE)-[0-9]+`.

### 3. `swain-design/references/lifecycle-tracks.md`

Add CHORE to the implementable track: `SPEC, CHORE`.

### 4. CHORE definition and template files

Create `chore-definition.md` and `chore-template.md.template` in `references/`. Reduced frontmatter (no `parent-epic`, `swain-do`, `type`, `priority-weight`, `addresses`, `evidence-pool`). Body sections: Problem, Checklist, Notes.

### 5. `docs/chores/list-chores.md`

Generate via `rebuild-index.sh chores`. Depends on SPEC-312 adding chores support.

## Acceptance Criteria

- [ ] SKILL.md type table includes CHORE row with links
- [ ] SKILL.md step 6.5 regex includes CHORE
- [ ] `lifecycle-tracks.md` lists CHORE in implementable track
- [ ] `chore-definition.md` exists with lifecycle and body sections
- [ ] `chore-template.md.template` exists with reduced frontmatter
- [ ] `docs/chores/list-chores.md` contains CHORE-001

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| SKILL.md type table | CHORE row present | |
| SKILL.md regex | `CHORE` in step 6.5 pattern | |
| lifecycle-tracks.md | CHORE in implementable track | |
| Definition file | `references/chore-definition.md` exists | |
| Template file | `references/chore-template.md.template` exists | |
| Index | `docs/chores/list-chores.md` has CHORE-001 | |

## Scope & Constraints

- **In scope:** Skill docs, reference files, index generation
- **Out of scope:** Bash scripts (SPEC-311), Python modules (SPEC-312)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-14 | — | Initial creation |