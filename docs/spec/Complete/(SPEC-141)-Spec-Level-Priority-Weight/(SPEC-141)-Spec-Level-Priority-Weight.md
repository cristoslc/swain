---
title: "Spec-Level Priority Weight"
artifact: SPEC-141
track: implementable
status: Complete
author: cristos
created: 2026-03-21
last-updated: 2026-03-21
type: enhancement
parent-epic: ""
parent-initiative: INITIATIVE-005
linked-artifacts:
  - ADR-010
  - EPIC-001
  - SPEC-001
  - VISION-001
depends-on-artifacts:
addresses:
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Spec-Level Priority Weight

## Problem Statement

`priority-weight` cascades Vision → Initiative → Epic → Spec, but SPECs cannot set their own override. This creates an asymmetry: Epics can escalate or de-escalate priority relative to their Initiative, but individual SPECs cannot do the same relative to their Epic. When a high-priority Epic contains a mix of critical and low-value items, there is no way to signal that distinction at the SPEC level — all SPECs inherit the same score.

Additionally, the documentation and template coverage for `priority-weight` is inconsistent across artifact types: the field is present in the Vision, Initiative, and Epic templates but absent from the Spec template, and the spec-definition.md has no priority section at all.

## External Behavior

- `priority-weight: high | medium | low` becomes a recognized optional frontmatter field on SPEC artifacts.
- When set, a SPEC's own `priority-weight` takes precedence over its inherited parent chain weight, consistent with how Epic overrides Initiative.
- When unset (default), a SPEC inherits from the nearest ancestor with a weight — behavior unchanged from current.
- The `priority.py` scoring engine applies the SPEC's own weight when present, skipping the parent-chain walk for that artifact.
- No breaking change to existing SPECs that omit the field.
- Other artifact types (SPIKE, ADR, DESIGN, RUNBOOK, PERSONA, TRAIN, JOURNEY) may also carry `priority_weight` in frontmatter; the resolver honors the field on any artifact type, not just the current whitelist of VISION/INITIATIVE/EPIC/SPEC.

## Acceptance Criteria

**Given** a SPEC with `priority-weight: low` whose parent Epic has `priority-weight: high`,
**When** `resolve_vision_weight` is called for that SPEC,
**Then** it returns 1 (low), not 3 (high).

**Given** a SPEC with no `priority-weight` field whose parent Epic has `priority-weight: high`,
**When** `resolve_vision_weight` is called for that SPEC,
**Then** it returns 3 (high) — unchanged inheritance behavior.

**Given** an existing SPEC on disk with no `priority-weight` in its frontmatter,
**When** the scorer processes it,
**Then** no error is raised and inheritance behavior is preserved.

**Given** the spec-template.md.template,
**When** a new SPEC is created from the template,
**Then** the `priority-weight` field is present (empty/commented, optional) alongside a comment explaining it defaults to inheriting from parent.

**Given** spec-definition.md,
**When** a reader looks for priority documentation,
**Then** they find a section describing the field, accepted values, inheritance behavior, and when to use an override.

**Given** SKILL.md's "Updating artifact metadata" section,
**When** it describes the cascade,
**Then** it reads "→ Spec (can override)" rather than "→ Spec (inherits nearest)" — consistent with Epic and Initiative wording.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| SPEC with `priority-weight: low`, parent Epic has `high` → `resolve_vision_weight` returns 1 | `test_spec_overrides_epic_weight` in `skills/swain-design/scripts/tests/test_priority.py` | Pass |
| SPEC with no `priority-weight`, parent Epic has `high` → returns 3 (unchanged inheritance) | `test_spec_without_weight_still_inherits` in `skills/swain-design/scripts/tests/test_priority.py` | Pass |
| Existing SPEC with no field → no error, inheritance preserved | `test_spec_inherits_through_chain`, `test_spec_without_weight_still_inherits`; all 17 tests pass | Pass |
| `spec-template.md.template` includes optional `priority-weight` field with comment | `priority-weight: ""  # optional: high \| medium \| low` added after `last-updated` in template (commit 9f89b07) | Pass |
| `spec-definition.md` has Priority field documentation | Priority field bullet added after Type field in `skills/swain-design/references/spec-definition.md` (commit 9f89b07) | Pass |
| SKILL.md cascade reads "→ Spec (can override)" | `skills/swain-design/SKILL.md` cascade updated: `→ Spec (can override)` and field description includes Specs (commit 9f89b07) | Pass |

## Scope & Constraints

**In scope:**
- `priority.py` — remove the VISION/INITIATIVE/EPIC type whitelist from `resolve_vision_weight`; honor `priority_weight` on any artifact type that sets it.
- `spec-template.md.template` — add optional `priority-weight: ""` field with inline comment.
- `spec-definition.md` — add a Priority section documenting the field.
- `SKILL.md` — update the `priority-weight` description in "Updating artifact metadata" to list SPEC as a type that can override, and update the cascade description.
- `test_priority.py` — add `test_spec_overrides_epic_weight` and `test_spec_without_weight_inherits` test cases.

**Out of scope:**
- Adding `priority-weight` to SPIKE, ADR, DESIGN, RUNBOOK, PERSONA, TRAIN, or JOURNEY templates. The resolver change (removing the whitelist) means these types can carry the field and have it honored, but documenting and adding the field to each template is deferred — that is a documentation-only change with no behavioral urgency.
- ADR-010's recursive summation model. This SPEC is compatible with that model: when ADR-010 lands, the SPEC-level weight becomes the local delta in the recursive formula. No re-work required.
- `list-spec.md` index — priority-weight is not a column in the index; no index update needed.

## Implementation Approach

### 1. Update `priority.py` — remove type whitelist

In `resolve_vision_weight`, replace the type guard that restricts own-weight check to `("VISION", "INITIATIVE", "EPIC")` with a check that applies to any artifact type:

```python
# Before:
if node_type in ("VISION", "INITIATIVE", "EPIC"):
    return WEIGHT_MAP[own_weight]

# After: honor own weight for any artifact type
return WEIGHT_MAP[own_weight]
```

This means the full block becomes:
```python
own_weight = node.get("priority_weight", "")
if own_weight and own_weight in WEIGHT_MAP:
    return WEIGHT_MAP[own_weight]
```

The parent-chain walk is unchanged and still only honors ancestors of type EPIC, INITIATIVE, or VISION:
```python
for ancestor_id in chain:
    ancestor = nodes.get(ancestor_id, {})
    ancestor_weight = ancestor.get("priority_weight", "")
    if ancestor_weight and ancestor_weight in WEIGHT_MAP:
        ancestor_type = ancestor.get("type", "").upper()
        if ancestor_type in ("EPIC", "INITIATIVE", "VISION"):
            return WEIGHT_MAP[ancestor_weight]
```

### 2. Update `spec-template.md.template`

Add `priority-weight: ""` after `last-updated`, with a comment:

```yaml
priority-weight: ""  # optional: high | medium | low. Omit to inherit from parent Epic or Initiative.
```

### 3. Update `spec-definition.md`

Add a **Priority** section after the Type field documentation:

> **`priority-weight` (optional):** Accepts `high`, `medium`, or `low`. When set, overrides the inherited weight from the parent Epic or Initiative for this SPEC only. Omit the field to inherit — behavior is identical to the current cascade. Use a SPEC-level override when a single SPEC within a high-priority Epic is low-value or vice-versa.

### 4. Update `SKILL.md`

In the "Updating artifact metadata" section, change:
- Cascade description from `→ Spec (inherits nearest)` to `→ Spec (can override)`
- `priority-weight` bullet from `on Visions, Initiatives, and Epics` to `on Visions, Initiatives, Epics, and Specs`

### 5. Add tests to `test_priority.py`

Add to `TestVisionWeightResolution`:

```python
def test_spec_overrides_epic_weight(self):
    """SPEC with priority-weight overrides its parent Epic's weight."""
    nodes = {
        "VISION-001": {"type": "VISION", "priority_weight": "high", ...},
        "EPIC-001": {"type": "EPIC", "priority_weight": "high", ...},
        "SPEC-001": {"type": "SPEC", "priority_weight": "low", ...},
    }
    edges = [
        {"from": "EPIC-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
    ]
    assert resolve_vision_weight("SPEC-001", nodes, edges) == 1  # low=1, not high=3

def test_spec_without_weight_still_inherits(self):
    """SPEC with no priority-weight still inherits from parent chain."""
    # (verifies no regression — same as existing test_spec_inherits_through_chain)
    assert resolve_vision_weight("SPEC-001", self.NODES, self.EDGES) == 3
```

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-21 | c063592 | Initial creation |
| Needs Manual Test | 2026-03-21 | 0926173 | Implementation complete; all 6 acceptance criteria verified |
| Complete | 2026-03-21 | bae2db9 | Operator waived manual test; all criteria evidenced by automated tests |
