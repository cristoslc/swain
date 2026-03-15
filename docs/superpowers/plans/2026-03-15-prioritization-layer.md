# Prioritization Layer Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a prioritization layer to swain that introduces the Initiative artifact type, vision weights, decision debt scoring, attention tracking, and two operating modes (vision/detail) in swain-status.

**Architecture:** The Initiative artifact type slots into the existing specgraph graph model as a new container-track artifact with a `parent-initiative` edge type. Vision weights flow through the graph via a new `priority-weight` frontmatter field. A new `attention.py` module computes attention distribution from git history. swain-status gains mode inference, focus lane awareness, and vision-anchored recommendations.

**Tech Stack:** Python 3 (specgraph), Bash (swain-status.sh, swain-session), jq (status cache processing), pytest (tests)

**Spec:** `docs/superpowers/specs/2026-03-14-prioritization-layer-design.md`

---

## Chunk 1: Initiative Artifact Type + Specgraph Foundation

### Task 1: Create Initiative artifact template and definition

**Files:**
- Create: `skills/swain-design/references/initiative-template.md.template`
- Create: `skills/swain-design/references/initiative-definition.md`

- [ ] **Step 1: Create initiative template**

```markdown
<!-- Jinja2 structural template — uses {{ variable }} placeholders. Read as a structural reference; no rendering pipeline needed. -->
---
title: "{{ title }}"
artifact: INITIATIVE-{{ number }}
track: container
status: {{ status | default("Proposed") }}
author: {{ author }}
created: {{ created_date }}
last-updated: {{ last_updated_date }}
parent-vision: VISION-{{ parent_vision_number }}
priority-weight: {{ priority_weight | default("") }}
success-criteria:
{%- for criterion in success_criteria %}
  - {{ criterion }}
{%- endfor %}
depends-on-artifacts:
{%- for dep in depends_on_artifacts | default([]) %}
  - {{ dep }}
{%- endfor %}
addresses:
{%- for pp in addresses | default([]) %}
  - {{ pp }}
{%- endfor %}
evidence-pool: {{ evidence_pool | default("") }}
---

# {{ title }}

## Strategic Bet

{{ strategic_bet | default("What strategic bet is this initiative making? What problem does it address?") }}

## Scope Boundaries

{{ scope | default("What is in scope and what is explicitly out of scope.") }}

## Child Epics

{{ child_epics | default("Updated as Epics are created under this initiative.") }}

## Small Work (Epic-less Specs)

{{ small_work | default("Specs attached directly to this initiative without an epic wrapper.") }}

## Key Dependencies

{{ dependencies | default("Dependencies on other Initiatives or external factors.") }}

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| {{ status | default("Proposed") }} | {{ created_date }} | {{ commit_hash }} | Initial creation |
```

Write to: `skills/swain-design/references/initiative-template.md.template`

- [ ] **Step 2: Create initiative definition**

Write a definition file modeled after `skills/swain-design/references/epic-definition.md` but for the Initiative type. Key fields:
- Track: container
- Phases: Proposed → Active → Complete (same as Epic)
- Required frontmatter: title, artifact, track, status, parent-vision
- Optional frontmatter: priority-weight, success-criteria, depends-on-artifacts, addresses, evidence-pool
- Must have `parent-vision` — initiatives without a vision parent are flagged as orphans
- May contain child Epics (via `parent-initiative` on the Epic) and standalone Specs (via `parent-initiative` on the Spec)

Write to: `skills/swain-design/references/initiative-definition.md`

- [ ] **Step 3: Create docs/initiative/ directory structure**

```bash
mkdir -p docs/initiative/{Proposed,Active,Complete,Abandoned,Superseded}
```

- [ ] **Step 4: Commit**

```bash
git add skills/swain-design/references/initiative-template.md.template \
      skills/swain-design/references/initiative-definition.md \
      docs/initiative/
git commit -m "feat(specgraph): add Initiative artifact type template and definition"
```

### Task 2: Register INITIATIVE in specgraph type system

**Files:**
- Modify: `skills/swain-design/scripts/specgraph/xref.py:10-13`
- Modify: `skills/swain-design/scripts/specgraph/resolved.py:34`
- Test: `skills/swain-design/scripts/tests/test_resolved.py`

- [ ] **Step 1: Write test for Initiative resolution**

Add to `skills/swain-design/scripts/tests/test_resolved.py`:

```python
def test_initiative_container_track():
    """INITIATIVE uses container track — resolved only at terminal statuses."""
    assert not is_resolved("INITIATIVE", "Proposed")
    assert not is_resolved("INITIATIVE", "Active")
    assert is_resolved("INITIATIVE", "Complete")
    assert is_resolved("INITIATIVE", "Abandoned")
    assert is_resolved("INITIATIVE", "Superseded")


def test_initiative_with_track_field():
    """INITIATIVE with explicit track=container works correctly."""
    assert not is_resolved("INITIATIVE", "Active", track="container")
    assert is_resolved("INITIATIVE", "Complete", track="container")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest skills/swain-design/scripts/tests/test_resolved.py -v -k initiative`
Expected: FAIL — `_infer_track("INITIATIVE")` returns `"implementable"` (unknown type fallback)

- [ ] **Step 3: Add INITIATIVE to _CONTAINER_TYPES**

In `skills/swain-design/scripts/specgraph/resolved.py:34`, change:
```python
_CONTAINER_TYPES = frozenset({"EPIC", "SPIKE"})
```
to:
```python
_CONTAINER_TYPES = frozenset({"EPIC", "SPIKE", "INITIATIVE"})
```

- [ ] **Step 4: Add INITIATIVE to _KNOWN_ARTIFACT_PREFIXES**

In `skills/swain-design/scripts/specgraph/xref.py:10-13`, add `"INITIATIVE"` to the frozenset:
```python
_KNOWN_ARTIFACT_PREFIXES = frozenset({
    "VISION", "EPIC", "SPEC", "SPIKE", "ADR", "JOURNEY",
    "PERSONA", "DESIGN", "RUNBOOK", "STORY", "BUG", "INITIATIVE",
})
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest skills/swain-design/scripts/tests/test_resolved.py -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add skills/swain-design/scripts/specgraph/resolved.py \
      skills/swain-design/scripts/specgraph/xref.py \
      skills/swain-design/scripts/tests/test_resolved.py
git commit -m "feat(specgraph): register INITIATIVE as container-track artifact type"
```

### Task 3: Add parent-initiative edge type to graph building

**Files:**
- Modify: `skills/swain-design/scripts/specgraph/graph.py:84-103`
- Modify: `skills/swain-design/scripts/specgraph/queries.py:206,412`
- Test: `skills/swain-design/scripts/tests/test_graph.py`
- Test: `skills/swain-design/scripts/tests/test_queries.py`

- [ ] **Step 1: Write test for parent-initiative edge extraction**

Add to `skills/swain-design/scripts/tests/test_graph.py` a test that verifies when a frontmatter has `parent-initiative: INITIATIVE-001`, the graph builder emits an edge `{from: "EPIC-XXX", to: "INITIATIVE-001", type: "parent-initiative"}`.

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest skills/swain-design/scripts/tests/test_graph.py -v -k parent_initiative`
Expected: FAIL

- [ ] **Step 3: Add parent-initiative edge extraction to graph.py**

In `skills/swain-design/scripts/specgraph/graph.py`, after the `parent-epic` block (lines 96-102), add:

```python
        # parent-initiative (scalar or list)
        pi = extract_scalar_id(fields, "parent-initiative")
        if pi is None:
            pis = extract_list_ids(fields, "parent-initiative")
            pi = pis[0] if pis else None
        if pi:
            add_edge(aid, pi, "parent-initiative")
```

- [ ] **Step 4: Add parent-initiative to _PARENT_EDGE_TYPES in queries.py**

In `skills/swain-design/scripts/specgraph/queries.py:206`, change:
```python
_PARENT_EDGE_TYPES = frozenset({"parent-epic", "parent-vision"})
```
to:
```python
_PARENT_EDGE_TYPES = frozenset({"parent-epic", "parent-vision", "parent-initiative"})
```

- [ ] **Step 5: Add parent-initiative to _MERMAID_CORE_EDGE_TYPES in queries.py**

In `skills/swain-design/scripts/specgraph/queries.py:412`, change:
```python
_MERMAID_CORE_EDGE_TYPES = frozenset({"depends-on", "parent-epic", "parent-vision"})
```
to:
```python
_MERMAID_CORE_EDGE_TYPES = frozenset({"depends-on", "parent-epic", "parent-vision", "parent-initiative"})
```

- [ ] **Step 6: Write test for parent chain walking through initiative**

Add to `skills/swain-design/scripts/tests/test_queries.py`:

```python
class TestInitiativeParentChain:
    """Test parent chain walking includes parent-initiative edges."""

    NODES = {
        "SPEC-010": {"title": "Spec 10", "status": "Ready", "type": "SPEC", "file": "", "description": ""},
        "EPIC-010": {"title": "Epic 10", "status": "Active", "type": "EPIC", "file": "", "description": ""},
        "INITIATIVE-001": {"title": "Initiative 1", "status": "Active", "type": "INITIATIVE", "file": "", "description": ""},
        "VISION-001": {"title": "Vision 1", "status": "Active", "type": "VISION", "file": "", "description": ""},
    }

    EDGES = [
        {"from": "SPEC-010", "to": "EPIC-010", "type": "parent-epic"},
        {"from": "EPIC-010", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
    ]

    def test_walk_parent_chain_through_initiative(self):
        """Parent chain walks SPEC → EPIC → INITIATIVE → VISION."""
        from specgraph.queries import _walk_parent_chain
        chain = _walk_parent_chain("SPEC-010", self.EDGES)
        assert chain == ["EPIC-010", "INITIATIVE-001", "VISION-001"]

    def test_find_vision_ancestor_through_initiative(self):
        """Vision ancestor found through initiative layer."""
        from specgraph.queries import _find_vision_ancestor
        vision = _find_vision_ancestor("SPEC-010", self.NODES, self.EDGES)
        assert vision == "VISION-001"

    def test_find_vision_ancestor_from_initiative(self):
        """Vision ancestor found directly from initiative."""
        from specgraph.queries import _find_vision_ancestor
        vision = _find_vision_ancestor("INITIATIVE-001", self.NODES, self.EDGES)
        assert vision == "VISION-001"
```

- [ ] **Step 7: Run all tests to verify they pass**

Run: `python3 -m pytest skills/swain-design/scripts/tests/ -v`
Expected: All PASS

- [ ] **Step 8: Commit**

```bash
git add skills/swain-design/scripts/specgraph/graph.py \
      skills/swain-design/scripts/specgraph/queries.py \
      skills/swain-design/scripts/tests/test_graph.py \
      skills/swain-design/scripts/tests/test_queries.py
git commit -m "feat(specgraph): add parent-initiative edge type and hierarchy traversal"
```

### Task 4: Add priority-weight field to node data model

**Files:**
- Modify: `skills/swain-design/scripts/specgraph/graph.py:75-82`
- Test: `skills/swain-design/scripts/tests/test_graph.py`

- [ ] **Step 1: Write test for priority-weight extraction**

Add to `skills/swain-design/scripts/tests/test_graph.py` a test that verifies when a Vision artifact has `priority-weight: high` in its frontmatter, the resulting node dict includes `"priority_weight": "high"`.

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest skills/swain-design/scripts/tests/test_graph.py -v -k priority_weight`
Expected: FAIL

- [ ] **Step 3: Extract priority-weight into node data**

In `skills/swain-design/scripts/specgraph/graph.py`, within the node-building block (lines 75-82), add the `priority_weight` field:

```python
        nodes[aid] = {
            "title": artifact.title,
            "status": artifact.status,
            "type": artifact.type,
            "track": track,
            "file": artifact.file,
            "description": artifact.description,
            "priority_weight": fields.get("priority-weight", ""),
        }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest skills/swain-design/scripts/tests/test_graph.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add skills/swain-design/scripts/specgraph/graph.py \
      skills/swain-design/scripts/tests/test_graph.py
git commit -m "feat(specgraph): extract priority-weight field into node data model"
```

### Task 5: Add priority-weight to vision template

**Files:**
- Modify: `skills/swain-design/references/vision-template.md.template`

- [ ] **Step 1: Add priority-weight field to vision template frontmatter**

In `skills/swain-design/references/vision-template.md.template`, add after the `last-updated` line:

```yaml
priority-weight: {{ priority_weight | default("") }}
```

- [ ] **Step 2: Commit**

```bash
git add skills/swain-design/references/vision-template.md.template
git commit -m "feat(specgraph): add priority-weight field to vision template"
```

### Task 6: Add parent-initiative field to epic and spec templates

**Files:**
- Modify: `skills/swain-design/references/epic-template.md.template`
- Modify: `skills/swain-design/references/spec-template.md.template`

- [ ] **Step 1: Add parent-initiative to epic template**

In `skills/swain-design/references/epic-template.md.template`, add after the `parent-vision` line:

```yaml
parent-initiative: {{ parent_initiative | default("") }}
```

- [ ] **Step 2: Add parent-initiative to spec template**

In `skills/swain-design/references/spec-template.md.template`, add after the `parent-epic` line:

```yaml
parent-initiative: {{ parent_initiative | default("") }}
```

- [ ] **Step 3: Commit**

```bash
git add skills/swain-design/references/epic-template.md.template \
      skills/swain-design/references/spec-template.md.template
git commit -m "feat(specgraph): add parent-initiative field to epic and spec templates"
```

### Task 7: Validate xref for parent-initiative and dual-parent rejection

**Files:**
- Modify: `skills/swain-design/scripts/specgraph/xref.py:17-29`
- Test: `skills/swain-design/scripts/tests/test_xref.py`

- [ ] **Step 1: Write test for parent-initiative in xref scalar fields**

Add to `skills/swain-design/scripts/tests/test_xref.py`:

```python
def test_collect_frontmatter_ids_includes_parent_initiative():
    """parent-initiative scalar is collected by collect_frontmatter_ids."""
    from specgraph.xref import collect_frontmatter_ids
    fm = {"parent-initiative": "INITIATIVE-001"}
    ids = collect_frontmatter_ids(fm)
    assert "INITIATIVE-001" in ids
```

- [ ] **Step 2: Write test for dual-parent spec rejection**

Add to `skills/swain-design/scripts/tests/test_graph.py`:

```python
def test_dual_parent_spec_produces_xref_warning():
    """A spec with both parent-epic and parent-initiative produces a warning in xref."""
    # Build a minimal graph with a dual-parent spec
    import tempfile, os
    from specgraph.graph import build_graph
    with tempfile.TemporaryDirectory() as tmpdir:
        docs = os.path.join(tmpdir, "docs", "spec", "Ready")
        os.makedirs(docs)
        spec_dir = os.path.join(docs, "(SPEC-099)-Dual-Parent")
        os.makedirs(spec_dir)
        with open(os.path.join(spec_dir, "(SPEC-099)-Dual-Parent.md"), "w") as f:
            f.write("---\ntitle: Dual Parent\nartifact: SPEC-099\nstatus: Ready\nparent-epic: EPIC-001\nparent-initiative: INITIATIVE-001\n---\nBody.\n")
        result = build_graph(Path(tmpdir))
        # Check for dual-parent warning in xref
        warnings = [x for x in result.get("xref", []) if x.get("artifact") == "SPEC-099"]
        # At minimum, the dual-parent should be flagged
        assert any("dual_parent" in str(w) for w in warnings), f"Expected dual_parent warning, got: {warnings}"
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python3 -m pytest skills/swain-design/scripts/tests/test_xref.py -v -k parent_initiative && python3 -m pytest skills/swain-design/scripts/tests/test_graph.py -v -k dual_parent`
Expected: Both FAIL

- [ ] **Step 4: Add parent-initiative to xref scalar fields**

In `skills/swain-design/scripts/specgraph/xref.py:65`, change:
```python
    for key in ("parent-epic", "parent-vision", "superseded-by"):
```
to:
```python
    for key in ("parent-epic", "parent-vision", "parent-initiative", "superseded-by"):
```

- [ ] **Step 4b: Add dual-parent rejection to graph.py**

In `skills/swain-design/scripts/specgraph/graph.py`, inside `build_graph()`, after the `parent-initiative` edge extraction (added in Task 3), add:

```python
        # Dual-parent rejection: spec with both parent-epic and parent-initiative
        has_parent_epic = pe is not None
        has_parent_initiative = pi is not None
        if has_parent_epic and has_parent_initiative:
            # Record as a warning to surface in xref output
            nodes[aid]["_dual_parent_warning"] = True
```

Then in the xref computation section (after `compute_xref` call), add dual-parent warnings:

```python
    # Append dual-parent warnings to xref
    for aid, node in nodes.items():
        if node.pop("_dual_parent_warning", False):
            xref.append({
                "artifact": aid,
                "file": node.get("file", ""),
                "body_not_in_frontmatter": [],
                "frontmatter_not_in_body": [],
                "missing_reciprocal": [],
                "dual_parent": True,
                "dual_parent_message": f"{aid} has both parent-epic and parent-initiative — use exactly one",
            })
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest skills/swain-design/scripts/tests/ -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add skills/swain-design/scripts/specgraph/xref.py \
      skills/swain-design/scripts/specgraph/graph.py \
      skills/swain-design/scripts/tests/test_xref.py
git commit -m "feat(specgraph): validate parent-initiative xrefs and reject dual-parent specs"
```

---

## Chunk 2: Decision Debt + Vision Weight Scoring

### Task 8: Implement vision weight resolution

**Files:**
- Create: `skills/swain-design/scripts/specgraph/priority.py`
- Test: `skills/swain-design/scripts/tests/test_priority.py`

- [ ] **Step 1: Write test for vision weight resolution**

Create `skills/swain-design/scripts/tests/test_priority.py`:

```python
"""Tests for prioritization scoring functions."""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from specgraph.priority import resolve_vision_weight, WEIGHT_MAP


class TestVisionWeightResolution:
    """Test resolving the effective vision weight for any artifact."""

    NODES = {
        "VISION-001": {"title": "V1", "status": "Active", "type": "VISION", "priority_weight": "high", "file": "", "description": ""},
        "VISION-002": {"title": "V2", "status": "Active", "type": "VISION", "priority_weight": "", "file": "", "description": ""},
        "INITIATIVE-001": {"title": "I1", "status": "Active", "type": "INITIATIVE", "priority_weight": "", "file": "", "description": ""},
        "INITIATIVE-002": {"title": "I2", "status": "Active", "type": "INITIATIVE", "priority_weight": "low", "file": "", "description": ""},
        "EPIC-001": {"title": "E1", "status": "Active", "type": "EPIC", "priority_weight": "", "file": "", "description": ""},
        "SPEC-001": {"title": "S1", "status": "Ready", "type": "SPEC", "priority_weight": "", "file": "", "description": ""},
    }

    EDGES = [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "INITIATIVE-002", "to": "VISION-001", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
    ]

    def test_vision_returns_own_weight(self):
        assert resolve_vision_weight("VISION-001", self.NODES, self.EDGES) == 3  # high

    def test_vision_default_medium(self):
        assert resolve_vision_weight("VISION-002", self.NODES, self.EDGES) == 2  # medium default

    def test_initiative_inherits_vision_weight(self):
        assert resolve_vision_weight("INITIATIVE-001", self.NODES, self.EDGES) == 3  # inherits high

    def test_initiative_override(self):
        assert resolve_vision_weight("INITIATIVE-002", self.NODES, self.EDGES) == 1  # overrides to low

    def test_epic_inherits_through_initiative(self):
        assert resolve_vision_weight("EPIC-001", self.NODES, self.EDGES) == 3  # EPIC→INIT→VISION(high)

    def test_spec_inherits_through_chain(self):
        assert resolve_vision_weight("SPEC-001", self.NODES, self.EDGES) == 3  # SPEC→EPIC→INIT→VISION(high)

    def test_orphan_returns_default(self):
        assert resolve_vision_weight("ORPHAN-001", self.NODES, self.EDGES) == 2  # medium default
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest skills/swain-design/scripts/tests/test_priority.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'specgraph.priority'`

- [ ] **Step 3: Implement priority.py**

Create `skills/swain-design/scripts/specgraph/priority.py`:

```python
"""Prioritization scoring for specgraph artifacts.

Implements the recommendation algorithm from the prioritization layer design spec:
  score = unblock_count × vision_weight

Vision weight cascades: Vision → Initiative (can override) → Epic → Spec.
"""

from __future__ import annotations

from .queries import _walk_parent_chain

WEIGHT_MAP = {"high": 3, "medium": 2, "low": 1}
DEFAULT_WEIGHT = 2  # medium


def resolve_vision_weight(
    artifact_id: str,
    nodes: dict,
    edges: list[dict],
) -> int:
    """Resolve the effective priority weight for an artifact.

    Walk the parent chain upward. If the artifact or any ancestor has a
    priority_weight set, use the closest one (initiative override > vision default).
    If the artifact is a Vision, use its own weight. Default: medium (2).
    """
    node = nodes.get(artifact_id)
    if node is None:
        return DEFAULT_WEIGHT

    # Check self first (Vision with own weight, or Initiative with override)
    own_weight = node.get("priority_weight", "")
    if own_weight and own_weight in WEIGHT_MAP:
        # If this is a Vision, return its weight directly
        if node.get("type", "").upper() == "VISION":
            return WEIGHT_MAP[own_weight]
        # If this is an Initiative with an override, use the override
        if node.get("type", "").upper() == "INITIATIVE":
            return WEIGHT_MAP[own_weight]

    # Walk parent chain and find the nearest weight
    chain = _walk_parent_chain(artifact_id, edges)
    # Check for initiative override first, then vision weight
    for ancestor_id in chain:
        ancestor = nodes.get(ancestor_id, {})
        ancestor_weight = ancestor.get("priority_weight", "")
        if ancestor_weight and ancestor_weight in WEIGHT_MAP:
            ancestor_type = ancestor.get("type", "").upper()
            if ancestor_type == "INITIATIVE":
                # Initiative override — use it
                return WEIGHT_MAP[ancestor_weight]
            if ancestor_type == "VISION":
                # Vision weight — use it (no initiative override found)
                return WEIGHT_MAP[ancestor_weight]

    return DEFAULT_WEIGHT
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest skills/swain-design/scripts/tests/test_priority.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add skills/swain-design/scripts/specgraph/priority.py \
      skills/swain-design/scripts/tests/test_priority.py
git commit -m "feat(specgraph): implement vision weight resolution with initiative override"
```

### Task 9: Implement decision debt computation

**Files:**
- Modify: `skills/swain-design/scripts/specgraph/priority.py`
- Test: `skills/swain-design/scripts/tests/test_priority.py`

- [ ] **Step 1: Write test for decision debt per vision**

Add to `skills/swain-design/scripts/tests/test_priority.py`:

```python
class TestDecisionDebt:
    """Test decision debt computation per vision."""

    NODES = {
        "VISION-001": {"title": "V1", "status": "Active", "type": "VISION", "priority_weight": "high", "file": "", "description": ""},
        "VISION-002": {"title": "V2", "status": "Active", "type": "VISION", "priority_weight": "medium", "file": "", "description": ""},
        "INITIATIVE-001": {"title": "I1", "status": "Active", "type": "INITIATIVE", "priority_weight": "", "file": "", "description": ""},
        "EPIC-001": {"title": "E1", "status": "Proposed", "type": "EPIC", "priority_weight": "", "file": "", "description": ""},
        "EPIC-002": {"title": "E2", "status": "Proposed", "type": "EPIC", "priority_weight": "", "file": "", "description": ""},
        "SPIKE-001": {"title": "S1", "status": "Proposed", "type": "SPIKE", "priority_weight": "", "file": "", "description": ""},
        "SPEC-001": {"title": "SP1", "status": "Ready", "type": "SPEC", "priority_weight": "", "file": "", "description": ""},
    }

    EDGES = [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "EPIC-002", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "SPIKE-001", "to": "VISION-002", "type": "parent-vision"},
        {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
        # EPIC-002 depends on SPIKE-001 (blocked)
        {"from": "EPIC-002", "to": "SPIKE-001", "type": "depends-on"},
    ]

    def test_decision_debt_counts_ready_items_per_vision(self):
        from specgraph.priority import compute_decision_debt
        debt = compute_decision_debt(self.NODES, self.EDGES)
        # VISION-001: EPIC-001 (ready), SPEC-001 (ready) = 2 decisions. EPIC-002 is blocked.
        # VISION-002: SPIKE-001 (ready) = 1 decision
        assert debt["VISION-001"]["count"] == 2
        assert debt["VISION-002"]["count"] == 1

    def test_decision_debt_includes_weighted_unblocks(self):
        from specgraph.priority import compute_decision_debt
        debt = compute_decision_debt(self.NODES, self.EDGES)
        # SPIKE-001 being completed would unblock EPIC-002
        assert debt["VISION-002"]["total_unblocks"] >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest skills/swain-design/scripts/tests/test_priority.py -v -k decision_debt`
Expected: FAIL

- [ ] **Step 3: Implement compute_decision_debt**

Add to `skills/swain-design/scripts/specgraph/priority.py`:

```python
from .queries import _compute_ready_set, _find_vision_ancestor, _node_is_resolved

# Decision-type detection (matches swain-status is_decision logic)
_DECISION_ONLY_TYPES = {"VISION", "JOURNEY", "PERSONA", "ADR", "DESIGN"}
_DECISION_PHASES = {"Proposed", "Draft", "Review", "Planned"}


def _is_decision_type(node: dict) -> bool:
    """Check if an artifact is a decision (requires operator, not agent)."""
    t = node.get("type", "").upper()
    if t in _DECISION_ONLY_TYPES:
        return True
    if t in ("EPIC", "INITIATIVE", "SPIKE") and node.get("status", "") in _DECISION_PHASES:
        return True
    if t == "SPEC" and node.get("status", "") in _DECISION_PHASES:
        return True
    return False


def _compute_unblock_count(artifact_id: str, nodes: dict, edges: list[dict]) -> int:
    """Count how many unresolved artifacts depend on this one."""
    count = 0
    for edge in edges:
        if edge.get("to") == artifact_id and edge.get("type") == "depends-on":
            source = edge.get("from", "")
            if source and source in nodes and not _node_is_resolved(source, nodes):
                count += 1
    return count


def compute_decision_debt(
    nodes: dict,
    edges: list[dict],
) -> dict[str, dict]:
    """Compute decision debt per vision.

    Only counts decision-type artifacts (operator-gated), not implementation work.
    Returns: {vision_id: {count: N, total_unblocks: N, items: [...]}}
    Items not attached to any vision go into an "_unaligned" bucket.
    """
    ready_set = _compute_ready_set(nodes, edges)

    # Group decision-type ready items by vision
    debt: dict[str, dict] = {}
    for rid in ready_set:
        node = nodes.get(rid, {})
        if not _is_decision_type(node):
            continue  # Skip implementation-type items
        vision = _find_vision_ancestor(rid, nodes, edges)
        bucket = vision or "_unaligned"
        unblocks = _compute_unblock_count(rid, nodes, edges)
        if bucket not in debt:
            debt[bucket] = {"count": 0, "total_unblocks": 0, "items": []}
        debt[bucket]["count"] += 1
        debt[bucket]["total_unblocks"] += unblocks
        debt[bucket]["items"].append(rid)

    return debt
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest skills/swain-design/scripts/tests/test_priority.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add skills/swain-design/scripts/specgraph/priority.py \
      skills/swain-design/scripts/tests/test_priority.py
git commit -m "feat(specgraph): implement decision debt computation per vision"
```

### Task 10: Implement recommendation scoring

**Files:**
- Modify: `skills/swain-design/scripts/specgraph/priority.py`
- Test: `skills/swain-design/scripts/tests/test_priority.py`

- [ ] **Step 1: Write test for recommendation scoring**

Add to `skills/swain-design/scripts/tests/test_priority.py`:

```python
class TestRecommendationScoring:
    """Test the score = unblock_count × vision_weight ranking."""

    NODES = {
        "VISION-001": {"title": "V1", "status": "Active", "type": "VISION", "priority_weight": "high", "file": "", "description": ""},
        "VISION-002": {"title": "V2", "status": "Active", "type": "VISION", "priority_weight": "low", "file": "", "description": ""},
        "INITIATIVE-001": {"title": "I1", "status": "Active", "type": "INITIATIVE", "priority_weight": "", "file": "", "description": ""},
        "INITIATIVE-002": {"title": "I2", "status": "Active", "type": "INITIATIVE", "priority_weight": "", "file": "", "description": ""},
        "EPIC-001": {"title": "E1", "status": "Proposed", "type": "EPIC", "priority_weight": "", "file": "", "description": ""},
        "EPIC-002": {"title": "E2", "status": "Proposed", "type": "EPIC", "priority_weight": "", "file": "", "description": ""},
        "SPEC-010": {"title": "SP10", "status": "Proposed", "type": "SPEC", "priority_weight": "", "file": "", "description": ""},
        "SPEC-011": {"title": "SP11", "status": "Proposed", "type": "SPEC", "priority_weight": "", "file": "", "description": ""},
        "SPEC-012": {"title": "SP12", "status": "Proposed", "type": "SPEC", "priority_weight": "", "file": "", "description": ""},
    }

    EDGES = [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "INITIATIVE-002", "to": "VISION-002", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "EPIC-002", "to": "INITIATIVE-002", "type": "parent-initiative"},
        # EPIC-002 (low vision) unblocks 3 specs
        {"from": "SPEC-010", "to": "EPIC-002", "type": "depends-on"},
        {"from": "SPEC-011", "to": "EPIC-002", "type": "depends-on"},
        {"from": "SPEC-012", "to": "EPIC-002", "type": "depends-on"},
        # EPIC-001 (high vision) unblocks 1 spec (but still scores higher: 1*3=3 vs 3*1=3 → tiebreak)
    ]

    def test_unblock_count_times_weight_determines_rank(self):
        from specgraph.priority import rank_recommendations
        ranked = rank_recommendations(self.NODES, self.EDGES)
        # EPIC-001: 0 unblocks × 3 (high) = 0. EPIC-002: 3 unblocks × 1 (low) = 3
        # Score 3 > 0 so EPIC-002 ranks first despite lower vision weight
        assert ranked[0]["id"] == "EPIC-002"

    def test_ranking_is_deterministic(self):
        from specgraph.priority import rank_recommendations
        ranked1 = rank_recommendations(self.NODES, self.EDGES)
        ranked2 = rank_recommendations(self.NODES, self.EDGES)
        assert [r["id"] for r in ranked1] == [r["id"] for r in ranked2]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest skills/swain-design/scripts/tests/test_priority.py -v -k recommendation`
Expected: FAIL

- [ ] **Step 3: Implement rank_recommendations**

Add to `skills/swain-design/scripts/specgraph/priority.py`:

```python
def rank_recommendations(
    nodes: dict,
    edges: list[dict],
    focus_vision: str | None = None,
) -> list[dict]:
    """Rank all ready items by score = unblock_count × vision_weight.

    If focus_vision is set, only score items under that vision.
    Returns list of {id, score, unblock_count, vision_weight, vision_id, type} sorted descending.

    Tiebreakers:
    1. Higher decision debt in the item's vision
    2. Decision-type artifacts over implementation-type
    3. Artifact ID (deterministic fallback)
    """
    ready_set = _compute_ready_set(nodes, edges)
    debt = compute_decision_debt(nodes, edges)

    # Decision-type detection (matches swain-status is_decision logic)
    _DECISION_ONLY_TYPES = {"VISION", "JOURNEY", "PERSONA", "ADR", "DESIGN"}
    _DECISION_PHASES = {"Proposed", "Draft", "Review", "Planned"}

    scored: list[dict] = []
    for rid in ready_set:
        node = nodes.get(rid, {})
        vision = _find_vision_ancestor(rid, nodes, edges)

        if focus_vision and vision != focus_vision:
            continue

        weight = resolve_vision_weight(rid, nodes, edges)
        unblock_count = _compute_unblock_count(rid, nodes, edges)
        vision_debt = debt.get(vision or "_unaligned", {}).get("count", 0)

        scored.append({
            "id": rid,
            "score": unblock_count * weight,
            "unblock_count": unblock_count,
            "vision_weight": weight,
            "vision_id": vision,
            "vision_debt": vision_debt,
            "is_decision": _is_decision_type(node),
            "type": node.get("type", ""),
        })

    # Sort: score desc, then vision_debt desc, then is_decision desc, then id asc
    scored.sort(key=lambda x: (-x["score"], -x["vision_debt"], -int(x["is_decision"]), x["id"]))
    return scored
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest skills/swain-design/scripts/tests/test_priority.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add skills/swain-design/scripts/specgraph/priority.py \
      skills/swain-design/scripts/tests/test_priority.py
git commit -m "feat(specgraph): implement recommendation scoring with vision weight tiebreakers"
```

### Task 11: Add CLI commands for priority queries

**Files:**
- Modify: `skills/swain-design/scripts/specgraph/cli.py`

- [ ] **Step 1: Write tests for CLI commands**

Add to `skills/swain-design/scripts/tests/test_queries.py` (or a new `test_cli.py`):

```python
class TestPriorityCLICommands:
    """Test decision-debt and recommend CLI dispatch."""

    def test_decision_debt_outputs_json(self):
        """decision-debt command produces valid JSON output."""
        import subprocess
        result = subprocess.run(
            ["python3", "skills/swain-design/scripts/specgraph.py", "decision-debt"],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        assert result.returncode == 0
        import json
        data = json.loads(result.stdout)
        assert isinstance(data, dict)

    def test_recommend_outputs_text(self):
        """recommend command produces text output."""
        import subprocess
        result = subprocess.run(
            ["python3", "skills/swain-design/scripts/specgraph.py", "recommend"],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        assert result.returncode == 0

    def test_recommend_json_outputs_valid_json(self):
        """recommend --json produces valid JSON list."""
        import subprocess
        result = subprocess.run(
            ["python3", "skills/swain-design/scripts/specgraph.py", "recommend", "--json"],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        assert result.returncode == 0
        import json
        data = json.loads(result.stdout)
        assert isinstance(data, list)
```

(Set `REPO_ROOT` to the git repo root via `subprocess.run(["git", "rev-parse", "--show-toplevel"], ...)`)

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest skills/swain-design/scripts/tests/ -v -k PriorityCLI`
Expected: FAIL

- [ ] **Step 3: Add decision-debt and recommend commands to cli.py**

In `skills/swain-design/scripts/specgraph/cli.py`, add subparser entries in the setup section (lines 138-155, before the `args = parser.parse_args(argv)` line):

```python
    # Priority commands
    subparsers.add_parser("decision-debt", help="Show decision debt per vision")
    rec_parser = subparsers.add_parser("recommend", help="Show ranked recommendation")
    rec_parser.add_argument("--focus", default=None, help="Focus vision ID (e.g. VISION-001)")
    rec_parser.add_argument("--json", action="store_true", help="Output raw JSON")
```

Add dispatch cases inside the `else` block (after line 169 `data = _ensure_cache(repo_root)`), before the final `else: print(f"Unknown command")`:

```python
        elif args.command == "decision-debt":
            from .priority import compute_decision_debt
            debt = compute_decision_debt(nodes, edges)
            import json as _json
            print(_json.dumps(debt, indent=2))
        elif args.command == "recommend":
            from .priority import rank_recommendations
            focus = getattr(args, "focus", None)
            ranked = rank_recommendations(nodes, edges, focus_vision=focus)
            if getattr(args, "json", False):
                import json as _json
                print(_json.dumps(ranked, indent=2))
            else:
                for i, item in enumerate(ranked[:10]):
                    marker = "→ " if i == 0 else "  "
                    print(f"{marker}{item['id']}  score={item['score']}  unblocks={item['unblock_count']}  weight={item['vision_weight']}  vision={item['vision_id'] or 'unaligned'}")
```

These must go inside the `else` block that calls `_ensure_cache` so `nodes` and `edges` are available.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest skills/swain-design/scripts/tests/ -v -k PriorityCLI`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add skills/swain-design/scripts/specgraph/cli.py
git commit -m "feat(specgraph): add decision-debt and recommend CLI commands"
```

---

## Chunk 3: Attention Tracking Module

> **Prerequisite:** Chunk 2 (Tasks 8-11) must be complete — `attention.py` imports from `priority.py`.

### Task 12: Implement attention tracking from git history

**Files:**
- Create: `skills/swain-design/scripts/specgraph/attention.py`
- Test: `skills/swain-design/scripts/tests/test_attention.py`

- [ ] **Step 1: Write tests for attention tracking**

Create `skills/swain-design/scripts/tests/test_attention.py`:

```python
"""Tests for attention tracking module."""

import sys
from pathlib import Path
from datetime import datetime, timezone

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from specgraph.attention import parse_git_log_entry, attribute_to_vision, compute_attention


class TestParseGitLogEntry:
    """Test parsing git log --name-only output."""

    def test_extracts_artifact_id_from_path(self):
        path = "docs/epic/Active/(EPIC-001)-Title/(EPIC-001)-Title.md"
        result = parse_git_log_entry(path)
        assert result == "EPIC-001"

    def test_extracts_spec_id(self):
        path = "docs/spec/Complete/(SPEC-042)-MOTD-Fix/(SPEC-042)-MOTD-Fix.md"
        result = parse_git_log_entry(path)
        assert result == "SPEC-042"

    def test_extracts_initiative_id(self):
        path = "docs/initiative/Active/(INITIATIVE-001)-Security/(INITIATIVE-001)-Security.md"
        result = parse_git_log_entry(path)
        assert result == "INITIATIVE-001"

    def test_returns_none_for_non_artifact(self):
        path = "skills/swain-status/scripts/swain-status.sh"
        result = parse_git_log_entry(path)
        assert result is None

    def test_returns_none_for_readme(self):
        path = "docs/epic/README.md"
        result = parse_git_log_entry(path)
        assert result is None


class TestAttributeToVision:
    """Test vision attribution via parent chain."""

    NODES = {
        "VISION-001": {"type": "VISION"},
        "INITIATIVE-001": {"type": "INITIATIVE"},
        "EPIC-001": {"type": "EPIC"},
        "SPEC-001": {"type": "SPEC"},
    }

    EDGES = [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
    ]

    def test_spec_attributed_to_vision(self):
        result = attribute_to_vision("SPEC-001", self.NODES, self.EDGES)
        assert result == "VISION-001"

    def test_orphan_returns_unaligned(self):
        result = attribute_to_vision("ORPHAN-001", self.NODES, self.EDGES)
        assert result == "_unaligned"


class TestComputeAttention:
    """Test the full attention computation from structured log data."""

    def test_aggregates_by_vision(self):
        # Simulate pre-parsed log data: list of (artifact_id, date)
        log_entries = [
            ("SPEC-001", datetime(2026, 3, 1, tzinfo=timezone.utc)),
            ("SPEC-001", datetime(2026, 3, 5, tzinfo=timezone.utc)),
            ("EPIC-002", datetime(2026, 3, 10, tzinfo=timezone.utc)),
        ]
        nodes = {
            "VISION-001": {"type": "VISION"},
            "INITIATIVE-001": {"type": "INITIATIVE"},
            "SPEC-001": {"type": "SPEC"},
            "EPIC-002": {"type": "EPIC"},
        }
        edges = [
            {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
            {"from": "SPEC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        ]
        result = compute_attention(log_entries, nodes, edges)
        assert result["VISION-001"]["transitions"] == 2
        assert result["_unaligned"]["transitions"] == 1  # EPIC-002 is orphan
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest skills/swain-design/scripts/tests/test_attention.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement attention.py**

Create `skills/swain-design/scripts/specgraph/attention.py`:

```python
"""Attention tracking — computes operator attention distribution from git history.

Scans git log for artifact file changes, attributes each to a vision via the
parent chain, and aggregates into a per-vision activity summary.

No persistent state — recomputed from git history on each invocation.
"""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .queries import _find_vision_ancestor

_ARTIFACT_ID_RE = re.compile(r"\(([A-Z]+-\d+)\)")


def parse_git_log_entry(filepath: str) -> str | None:
    """Extract artifact ID from a docs/ file path.

    Looks for (ARTIFACT-NNN) pattern in the path.
    Returns None for non-artifact files.
    """
    if not filepath.startswith("docs/"):
        return None
    match = _ARTIFACT_ID_RE.search(filepath)
    return match.group(1) if match else None


def attribute_to_vision(
    artifact_id: str,
    nodes: dict,
    edges: list[dict],
) -> str:
    """Attribute an artifact to its vision ancestor. Returns '_unaligned' if none."""
    vision = _find_vision_ancestor(artifact_id, nodes, edges)
    return vision or "_unaligned"


def scan_git_log(
    repo_root: Path,
    days: int = 30,
) -> list[tuple[str, datetime]]:
    """Scan git log for artifact file changes in the last N days.

    Returns list of (artifact_id, commit_date) tuples.
    """
    try:
        result = subprocess.run(
            [
                "git", "log",
                f"--since={days} days ago",
                "--name-only",
                "--pretty=format:%aI",
                "--diff-filter=AMRC",
                "--", "docs/",
            ],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    entries: list[tuple[str, datetime]] = []
    current_date: datetime | None = None

    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        # Try parsing as ISO date first
        try:
            current_date = datetime.fromisoformat(line)
            continue
        except ValueError:
            pass
        # Must be a file path
        if current_date is not None:
            artifact_id = parse_git_log_entry(line)
            if artifact_id:
                entries.append((artifact_id, current_date))

    return entries


def compute_attention(
    log_entries: list[tuple[str, datetime]],
    nodes: dict,
    edges: list[dict],
) -> dict[str, dict]:
    """Compute attention distribution from parsed log entries.

    Returns: {vision_id: {transitions: N, last_activity: ISO date string}}
    """
    attention: dict[str, dict] = {}

    for artifact_id, commit_date in log_entries:
        vision = attribute_to_vision(artifact_id, nodes, edges)
        if vision not in attention:
            attention[vision] = {"transitions": 0, "last_activity": None}
        attention[vision]["transitions"] += 1
        date_str = commit_date.isoformat()
        if attention[vision]["last_activity"] is None or date_str > attention[vision]["last_activity"]:
            attention[vision]["last_activity"] = date_str

    return attention


def compute_drift(
    attention: dict[str, dict],
    nodes: dict,
    drift_thresholds: dict | None = None,
) -> list[dict]:
    """Detect attention drift — visions with zero activity exceeding threshold.

    Default thresholds: high=14 days, medium=28 days, low=never.
    Returns list of {vision_id, weight, days_since_activity, threshold}.
    """
    from .priority import resolve_vision_weight, WEIGHT_MAP

    if drift_thresholds is None:
        drift_thresholds = {"high": 14, "medium": 28}

    now = datetime.now(timezone.utc)
    drifting: list[dict] = []

    for node_id, node in nodes.items():
        if node.get("type", "").upper() != "VISION":
            continue
        weight_label = node.get("priority_weight", "") or "medium"
        if weight_label == "low":
            continue  # Low-weight visions don't trigger drift

        threshold_days = drift_thresholds.get(weight_label, 28)
        vision_attention = attention.get(node_id, {})
        last_activity = vision_attention.get("last_activity")

        if last_activity:
            last_dt = datetime.fromisoformat(last_activity)
            days_since = (now - last_dt).days
        else:
            days_since = 999  # No activity ever

        if days_since >= threshold_days:
            drifting.append({
                "vision_id": node_id,
                "weight": weight_label,
                "days_since_activity": days_since,
                "threshold": threshold_days,
            })

    return drifting
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest skills/swain-design/scripts/tests/test_attention.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add skills/swain-design/scripts/specgraph/attention.py \
      skills/swain-design/scripts/tests/test_attention.py
git commit -m "feat(specgraph): implement attention tracking from git history"
```

### Task 13: Add attention CLI command

**Files:**
- Modify: `skills/swain-design/scripts/specgraph/cli.py`

- [ ] **Step 1: Add attention command to cli.py**

```python
# In subparser setup:
att_parser = subparsers.add_parser("attention", help="Show attention distribution by vision")
att_parser.add_argument("--days", type=int, default=30, help="Lookback window in days")
att_parser.add_argument("--json", action="store_true", help="Output raw JSON")

# In dispatch:
elif args.command == "attention":
    from .attention import scan_git_log, compute_attention, compute_drift
    log_entries = scan_git_log(repo_root, days=getattr(args, "days", 30))
    attention = compute_attention(log_entries, nodes, edges)
    drift = compute_drift(attention, nodes)
    if getattr(args, "json", False):
        import json as _json
        print(_json.dumps({"attention": attention, "drift": drift}, indent=2))
    else:
        print("=== Attention Distribution ===")
        for vid, data in sorted(attention.items()):
            vnode = nodes.get(vid, {})
            label = vnode.get("title", vid)
            weight = vnode.get("priority_weight", "medium") or "medium"
            print(f"  {vid} ({label}) [weight: {weight}] — {data['transitions']} transitions, last: {data['last_activity'] or 'never'}")
        if drift:
            print()
            print("=== Attention Drift ===")
            for d in drift:
                print(f"  {d['vision_id']} (weight: {d['weight']}) — {d['days_since_activity']} days since last activity (threshold: {d['threshold']})")
```

- [ ] **Step 2: Run manually to verify**

```bash
python3 skills/swain-design/scripts/specgraph.py attention
python3 skills/swain-design/scripts/specgraph.py attention --json
```

- [ ] **Step 3: Commit**

```bash
git add skills/swain-design/scripts/specgraph/cli.py
git commit -m "feat(specgraph): add attention CLI command for drift detection"
```

---

## Chunk 4: swain-status Integration

> **Prerequisite:** Chunks 1-3 (Tasks 1-13) must be complete and passing before starting this chunk.

### Task 14: Update swain-status.sh to include priority data in cache

**Files:**
- Modify: `skills/swain-status/scripts/swain-status.sh`

- [ ] **Step 1: Add priority data collectors to build_cache**

In `swain-status.sh`, the `build_cache()` function (around line 402) calls separate collector functions and merges results. Add three new collector calls **in `build_cache()`** alongside the existing `git_data`, `artifact_data`, `task_data`, etc.:

```bash
# Add after the existing collector calls in build_cache():
local recommend_data debt_data attention_data

recommend_data=$(python3 "$SPECGRAPH" recommend --json 2>/dev/null || echo '[]')
debt_data=$(python3 "$SPECGRAPH" decision-debt 2>/dev/null || echo '{}')
attention_data=$(python3 "$SPECGRAPH" attention --json 2>/dev/null || echo '{"attention":{},"drift":[]}')
```

Then in the `build_cache()` function's final jq merge (the jq call that combines all data sources), add three new `--argjson` parameters and a new `priority` key:

```bash
jq -n \
  --argjson git "$git_data" \
  --argjson artifacts "$artifact_data" \
  --argjson tasks "$task_data" \
  --argjson issues "$issue_data" \
  --argjson session "$session_data" \
  --argjson linked "$linked_data" \
  --argjson recommend "$recommend_data" \
  --argjson debt "$debt_data" \
  --argjson attention "$attention_data" \
  '{
    timestamp: now | strftime("%Y-%m-%dT%H:%M:%SZ"),
    repo: $git.repo,
    project: $git.project,
    git: $git,
    artifacts: $artifacts,
    tasks: $tasks,
    issues: $issues,
    linkedIssues: $linked,
    session: $session,
    priority: {
      recommendations: $recommend,
      decision_debt: $debt,
      attention: $attention.attention,
      drift: $attention.drift
    }
  }' > "$CACHE_FILE"
```

Note: The exact jq merge structure should match the existing `build_cache()` pattern — inspect the function and add the new fields alongside existing ones.

- [ ] **Step 2: Verify cache includes priority data**

```bash
bash skills/swain-status/scripts/swain-status.sh --refresh --json | jq '.priority'
```

Expected: JSON with recommendations, attention, drift, and decision_debt fields.

- [ ] **Step 3: Commit**

```bash
git add skills/swain-status/scripts/swain-status.sh
git commit -m "feat(swain-status): include priority scoring and attention data in status cache"
```

### Task 15: Update swain-status rendering with vision-anchored recommendation

**Files:**
- Modify: `skills/swain-status/scripts/swain-status.sh`

- [ ] **Step 1: Update the Decisions section to show vision context**

In the terminal output rendering section of `swain-status.sh`, modify the "Decisions Waiting on You" block to include vision attribution and weight for each decision item. Use the priority data from the cache.

The jq filter should:
1. Read `.priority.recommendations[]` instead of sorting raw ready items
2. For each recommendation, show: artifact ID, title, vision name + weight, unblock count
3. Sort by score descending (already sorted by `rank_recommendations`)

- [ ] **Step 2: Add attention drift section**

After the Decisions section, if `.priority.drift` is non-empty, render:

```
## Attention Drift

- VISION-001 (Security) [weight: high] — 18 days since last activity (threshold: 14)
```

- [ ] **Step 3: Add placeholder for peripheral awareness**

Add a conditional block that checks for `.priority.focus_lane` in the cache (will be populated after Task 18). If present, render a summary line for non-focus visions:

```
Meanwhile: Design has 4 pending decisions (weight: medium), Session has 1 (weight: low)
```

If not present, skip this section. The focus_lane field will be wired in Task 18.

- [ ] **Step 4: Verify rendering**

```bash
bash skills/swain-status/scripts/swain-status.sh --refresh
```

Check that the output includes vision-anchored recommendations and drift warnings.

- [ ] **Step 5: Commit**

```bash
git add skills/swain-status/scripts/swain-status.sh
git commit -m "feat(swain-status): render vision-anchored recommendations and attention drift"
```

### Task 16: Update agent summary template for new sections

**Files:**
- Modify: `skills/swain-status/references/agent-summary-template.md`

- [ ] **Step 1: Update recommendation section**

Update the Section 0: Recommendation to use the new scoring:

```markdown
## Section 0: Recommendation

Read `.priority.recommendations[0]` from the JSON cache. Write exactly two sentences:

- **Action:** One sentence naming the action (e.g., "Activate EPIC-017.")
- **Why:** One sentence naming the score, vision context, and unblock count
  (e.g., "Security is weighted high with 3 pending decisions — activating this
  unblocks EPIC-023. Note: your last 2 weeks of work has been in design tooling.")

Include attention drift context if any drift is detected for the recommendation's vision.
```

- [ ] **Step 2: Add peripheral awareness section**

Add a new section after Recommendation:

```markdown
## Section 0.5: Peripheral Awareness

If a focus lane is set and there are decisions in other visions, summarize:
"Meanwhile: [Vision Name] has N pending decisions (weight: W)"

One line per non-focus vision with pending decisions. Omit if no focus set.
```

- [ ] **Step 3: Commit**

```bash
git add skills/swain-status/references/agent-summary-template.md
git commit -m "docs(swain-status): update agent summary template for prioritization layer"
```

---

## Chunk 5: Session, Doctor, and Settings Integration

### Task 17: Add focus lane to session state

**Files:**
- Modify: `skills/swain-session/scripts/swain-bookmark.sh` (or equivalent session state script)
- Modify: `.agents/session.json` schema

- [ ] **Step 1: Extend session.json schema**

The session.json schema needs two new fields:

```json
{
  "focus_lane": "VISION-001",
  "status_mode": "vision"
}
```

`focus_lane` is a vision ID or initiative ID (or null).
`status_mode` is "vision" or "detail" (or null — trigger inference).

- [ ] **Step 2: Create swain-focus.sh helper script**

Create `skills/swain-session/scripts/swain-focus.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Set or clear the focus lane in session.json
# Usage: swain-focus.sh set VISION-001
#        swain-focus.sh clear

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
SESSION_FILE="$REPO_ROOT/.agents/session.json"

ACTION="${1:-}"
FOCUS_ID="${2:-}"

if [[ ! -f "$SESSION_FILE" ]]; then
  echo '{}' > "$SESSION_FILE"
fi

case "$ACTION" in
  set)
    if [[ -z "$FOCUS_ID" ]]; then
      echo "Usage: swain-focus.sh set <VISION-ID or INITIATIVE-ID>" >&2
      exit 1
    fi
    jq --arg focus "$FOCUS_ID" '.focus_lane = $focus' "$SESSION_FILE" > "${SESSION_FILE}.tmp" \
      && mv "${SESSION_FILE}.tmp" "$SESSION_FILE"
    echo "Focus lane set to: $FOCUS_ID"
    ;;
  clear)
    jq 'del(.focus_lane)' "$SESSION_FILE" > "${SESSION_FILE}.tmp" \
      && mv "${SESSION_FILE}.tmp" "$SESSION_FILE"
    echo "Focus lane cleared"
    ;;
  *)
    # Show current focus
    CURRENT=$(jq -r '.focus_lane // "none"' "$SESSION_FILE" 2>/dev/null || echo "none")
    echo "Current focus: $CURRENT"
    ;;
esac
```

- [ ] **Step 3: Update swain-session SKILL.md to expose focus lane**

Add a Focus Lane section to `skills/swain-session/SKILL.md` documenting:
- "focus [VISION-ID|INITIATIVE-ID]" — set focus lane
- "focus clear" — clear focus lane
- "focus" (no args) — show current focus
- The agent invokes `swain-focus.sh` when the operator says "focus on security" or similar

- [ ] **Step 4: Make executable and commit**

```bash
chmod +x skills/swain-session/scripts/swain-focus.sh
git add skills/swain-session/scripts/swain-focus.sh skills/swain-session/SKILL.md
git commit -m "feat(swain-session): add focus lane management with user-facing docs"
```

### Task 18: Update swain-status to read focus lane and infer mode

**Files:**
- Modify: `skills/swain-status/scripts/swain-status.sh`

- [ ] **Step 1: Read focus lane from session.json**

In the `collect_session` function, extract `focus_lane` and `status_mode`:

```bash
local FOCUS_LANE
FOCUS_LANE=$(jq -r '.focus_lane // empty' "$SESSION_FILE" 2>/dev/null || echo "")

local STATUS_MODE
STATUS_MODE=$(jq -r '.status_mode // empty' "$SESSION_FILE" 2>/dev/null || echo "")
```

Include in the session data passed to the cache builder.

- [ ] **Step 2: Pass focus lane to specgraph recommend**

If focus lane is set, pass it to `specgraph recommend --focus <VISION-ID>`:

```bash
if [[ -n "$FOCUS_LANE" ]]; then
  RECOMMEND_JSON=$(python3 "$SPECGRAPH" recommend --focus "$FOCUS_LANE" --json 2>/dev/null || echo '[]')
fi
```

- [ ] **Step 3: Commit**

```bash
git add skills/swain-status/scripts/swain-status.sh
git commit -m "feat(swain-status): integrate focus lane with recommendation scoring"
```

### Task 19: Add prioritization settings to swain.settings.json

**Files:**
- Modify: `swain.settings.json`

- [ ] **Step 1: Add prioritization section**

Add to `swain.settings.json`:

```json
{
  "prioritization": {
    "driftThresholds": {
      "high": 14,
      "medium": 28
    },
    "minActivityThreshold": 5,
    "attentionWindowDays": 30
  }
}
```

- [ ] **Step 2: Wire settings into attention CLI command**

In `skills/swain-design/scripts/specgraph/cli.py`, update the `attention` command dispatch to read thresholds from `swain.settings.json`:

```python
elif args.command == "attention":
    from .attention import scan_git_log, compute_attention, compute_drift
    # Read settings for drift thresholds
    import json as _json
    settings_path = repo_root / "swain.settings.json"
    drift_thresholds = None
    if settings_path.exists():
        try:
            settings = _json.loads(settings_path.read_text())
            p = settings.get("prioritization", {})
            drift_thresholds = p.get("driftThresholds")
        except (ValueError, KeyError):
            pass
    days = getattr(args, "days", 30)
    if drift_thresholds is None:
        # Check settings for window
        try:
            days = settings.get("prioritization", {}).get("attentionWindowDays", days)
        except (NameError, AttributeError):
            pass
    log_entries = scan_git_log(repo_root, days=days)
    attention = compute_attention(log_entries, nodes, edges)
    drift = compute_drift(attention, nodes, drift_thresholds=drift_thresholds)
    # ... rest of output rendering
```

- [ ] **Step 3: Commit**

```bash
git add swain.settings.json skills/swain-design/scripts/specgraph/attention.py
git commit -m "feat: add prioritization settings with configurable drift thresholds"
```

### Task 20: Add migration detection to swain-doctor

**Files:**
- Modify: `skills/swain-doctor/scripts/swain-preflight.sh`

- [ ] **Step 1: Add initiative layer check**

Add a new check to `swain-preflight.sh` that detects when epics have `parent-vision` but no `parent-initiative` (pre-migration state). This is advisory, not blocking.

```bash
# Check for epics without parent-initiative (initiative migration advisory)
EPICS_WITHOUT_INITIATIVE=0
while IFS= read -r -d '' f; do
  if grep -q '^parent-vision:' "$f" 2>/dev/null && ! grep -q '^parent-initiative:' "$f" 2>/dev/null; then
    EPICS_WITHOUT_INITIATIVE=$((EPICS_WITHOUT_INITIATIVE + 1))
  fi
done < <(find docs/epic -name '*.md' -not -name 'README.md' -not -name 'list-*.md' -print0 2>/dev/null)
if [[ "$EPICS_WITHOUT_INITIATIVE" -gt 0 ]]; then
  echo "advisory: $EPICS_WITHOUT_INITIATIVE epic(s) without parent-initiative — run initiative migration"
fi
```

- [ ] **Step 2: Commit**

```bash
git add skills/swain-doctor/scripts/swain-preflight.sh
git commit -m "feat(swain-doctor): detect epics without parent-initiative for migration advisory"
```

### Task 21: Update swain-status SKILL.md for new capabilities

**Files:**
- Modify: `skills/swain-status/SKILL.md`

- [ ] **Step 1: Document new recommendation algorithm**

Update the Recommendation section to describe the `score = unblock_count × vision_weight` formula and the tiebreaker chain.

- [ ] **Step 2: Document mode inference rules**

Add a Mode Inference section with the priority-ordered rules from the spec.

- [ ] **Step 3: Document focus lane**

Add a Focus Lane section describing how the operator sets focus and how it affects recommendations.

- [ ] **Step 4: Document peripheral awareness**

Add a Peripheral Awareness section describing how non-focus visions are summarized.

- [ ] **Step 5: Commit**

```bash
git add skills/swain-status/SKILL.md
git commit -m "docs(swain-status): document prioritization layer capabilities"
```

### Task 22: Update AGENTS.md for initiative artifact type

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Add initiative to artifact type documentation**

In the AGENTS.md skill routing section, add INITIATIVE to the list of artifact types handled by swain-design.

- [ ] **Step 2: Update hierarchy documentation**

Add a section or update existing docs to reflect Vision → Initiative → Epic → Spec hierarchy.

- [ ] **Step 3: Commit**

```bash
git add AGENTS.md
git commit -m "docs: update AGENTS.md for initiative artifact type and prioritization layer"
```

### Task 23: Run full test suite and verify

- [ ] **Step 1: Run all specgraph tests**

```bash
python3 -m pytest skills/swain-design/scripts/tests/ -v
```

Expected: All PASS

- [ ] **Step 2: Run swain-status manually**

```bash
bash skills/swain-status/scripts/swain-status.sh --refresh
```

Expected: Output includes vision-anchored recommendation, no errors.

- [ ] **Step 3: Run specgraph commands**

```bash
python3 skills/swain-design/scripts/specgraph.py recommend
python3 skills/swain-design/scripts/specgraph.py decision-debt
python3 skills/swain-design/scripts/specgraph.py attention
python3 skills/swain-design/scripts/specgraph.py overview
```

Expected: All produce output without errors.

- [ ] **Step 4: Run swain-preflight**

```bash
bash skills/swain-doctor/scripts/swain-preflight.sh
```

Expected: Advisory about epics without parent-initiative.

- [ ] **Step 5: Commit any fixes**

If any issues found, fix and commit.
