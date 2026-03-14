---
title: "swain-design Fast-Path Complexity Gate"
artifact: SPEC-045
track: implementable
status: Proposed
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
type: enhancement
parent-epic: EPIC-014
linked-artifacts:
  - SPIKE-018
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# swain-design Fast-Path Complexity Gate

## Problem Statement

Every artifact creation in swain-design runs three optional checks unconditionally: `adr-check.sh`, `specgraph.sh scope`, and `specwatch.sh scan`. For low-complexity artifacts (bug SPECs, standalone SPECs with no parent epic, no downstream dependents), these checks add ~2.5s and ~700 tokens of ceremony cost with near-zero marginal value. SPIKE-018 established that specwatch scan (353ms, high token cost) and specgraph scope are safely skippable for this class of artifact.

## External Behavior

When swain-design creates or transitions an artifact, it evaluates the artifact's complexity tier before running optional checks:

- **Low complexity**: `type: bug` or `type: fix`, no `parent-epic`, no entries in `depends-on-artifacts` → skip `specwatch.sh scan` and `specgraph.sh scope`; still run `adr-check.sh` if the artifact references an ADR
- **Standard complexity**: anything else → full ceremony (unchanged behavior)

The complexity tier is determined from frontmatter alone — no additional file reads required. No user prompt is needed; the gate is automatic.

The SKILL.md authoring workflow (steps 7, 8, 8a, 9) gains conditional guards. The full-ceremony path remains available for all artifact types.

## Acceptance Criteria

1. **Given** a SPEC with `type: bug` and no `parent-epic`, **when** swain-design creates it, **then** `specwatch.sh scan` and `specgraph.sh scope` are not invoked
2. **Given** a SPEC with `type: feature` or any `parent-epic`, **when** swain-design creates it, **then** the full ceremony runs (specwatch + scope + adr-check all run)
3. **Given** any artifact type (EPIC, ADR, VISION), **when** swain-design creates it, **then** the full ceremony runs (fast-path applies only to low-complexity SPECs)
4. **Given** a low-complexity SPEC with a broken frontmatter reference, **when** the fast-path skips specwatch, **then** the breakage is detectable on the next full specwatch run (deferred, not lost)
5. **Given** SKILL.md step 8a (alignment check), **when** the fast-path applies, **then** the step is documented as skipped in the agent's response (not silently omitted)

## Scope & Constraints

**In scope:**
- Updating swain-design SKILL.md workflow steps 7, 8, 8a, 9 with complexity gate conditions
- Documenting the fast-path definition in `skills/swain-design/references/fast-path.md`
- Acceptance criteria 1-5 above

**Out of scope:**
- Modifying `specwatch.sh`, `specgraph.sh`, or `adr-check.sh` scripts
- Changing the artifact schema or templates
- Performance optimization of the scripts themselves
- User-facing prompts asking about complexity (must be automatic)

## Implementation Approach

1. Create `skills/swain-design/references/fast-path.md` defining complexity tiers and skip rules
2. Update SKILL.md §Creating artifacts steps 8, 8a, 9 with conditional guards keyed on complexity tier
3. Add a `_is_low_complexity(frontmatter)` evaluation rule (pseudocode in fast-path.md) that skill implementations follow

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation from SPIKE-018 GO decision |
