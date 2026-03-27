---
title: "Brief Description Frontmatter Field"
artifact: SPEC-144
track: implementable
status: Active
author: cristos
created: 2026-03-21
last-updated: 2026-03-21
type: enhancement
parent-epic: ""
parent-initiative: INITIATIVE-005
linked-artifacts:
  - SPEC-143
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Brief Description Frontmatter Field

## Problem Statement

Vision and Initiative artifacts lack a machine-readable one-line summary. Their intent is buried in body sections (Value Proposition, Goal/Objective) which require an agent to read and interpret. Downstream consumers — scoped roadmap slices (SPEC-143), specgraph tooltips, index listings, CLI summaries — all need a short description but have no structured field to pull from.

## Desired Outcomes

Every Vision and Initiative carries a `brief-description` frontmatter field: a single sentence (≤120 chars) summarizing the artifact's intent. Downstream tools can consume this field directly without parsing body text or relying on agent-authored summaries. This makes artifact summaries deterministic and consistent across all rendering surfaces.

## External Behavior

### New frontmatter field: `brief-description`

Added to Vision and Initiative templates as an optional field (empty string default). A single sentence, max 120 characters, summarizing the artifact's intent.

**Vision example:**
```yaml
brief-description: "Agent-native product management platform for solo operators"
```

**Initiative example:**
```yaml
brief-description: "Give operators real-time awareness of project state and priorities"
```

### Template changes

- `vision-template.md.template`: add `brief-description: {{ brief_description | default("") }}` after `priority-weight`
- `initiative-template.md.template`: add `brief-description: {{ brief_description | default("") }}` after `priority-weight`

### Creation workflow change

When creating a Vision or Initiative, after populating other frontmatter fields, prompt the agent to write a `brief-description` derived from the body content. The field is optional — empty is valid — but swain-design should populate it by default during creation.

### Backfill

Existing Vision and Initiative artifacts should be backfilled with `brief-description` fields. This can be done incrementally (agent fills it in when touching the artifact for other reasons) or as a one-time batch.

### Consumer integration

Once this field exists, [SPEC-143](../../Complete/(SPEC-143)-Per-Vision-Per-Initiative-Roadmap-Slices/(SPEC-143)-Per-Vision-Per-Initiative-Roadmap-Slices.md)'s scoped roadmap generator should prefer `brief-description` over agent-authored summaries for the intent line.

## Acceptance Criteria

### AC1: Vision template includes brief-description

**Given** the vision template,
**When** a new Vision is created,
**Then** the frontmatter includes a `brief-description` field.

### AC2: Initiative template includes brief-description

**Given** the initiative template,
**When** a new Initiative is created,
**Then** the frontmatter includes a `brief-description` field.

### AC3: Field is optional

**Given** an artifact with `brief-description: ""`,
**When** any consumer reads the frontmatter,
**Then** the empty value is treated as absent (no error, fallback to body parsing or placeholder).

### AC4: Character limit enforced by convention

**Given** a `brief-description` value exceeding 120 characters,
**When** specwatch scans the artifact,
**Then** a warning is emitted (advisory, not blocking).

### AC5: Existing artifacts accept the field

**Given** an existing Vision or Initiative without `brief-description`,
**When** the field is added manually or by an agent,
**Then** no tooling breaks (backward compatible).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

**In scope:**
- Adding `brief-description` to Vision and Initiative templates
- swain-design creation workflow populates the field
- specwatch advisory warning for >120 chars
- Documentation in vision-definition.md and initiative-definition.md

**Out of scope:**
- Adding `brief-description` to other artifact types (Epic, Spec, etc.) — evaluate after Visions and Initiatives prove the pattern
- Automated backfill script — incremental backfill is sufficient
- Enforcing the field as required — it is optional

## Implementation Approach

1. **RED:** Test that vision and initiative templates include `brief-description` in frontmatter.
2. **GREEN:** Add the field to both templates.
3. **RED:** Test that specwatch warns on >120 char values.
4. **GREEN:** Add advisory check to specwatch.
5. Update vision-definition.md and initiative-definition.md to document the field.
6. Backfill existing artifacts (can be incremental).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-21 | — | Initial creation; supports SPEC-143 intent summary |
