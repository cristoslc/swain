# Vision-Rooted Chart Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `swain chart` — a unified, vision-rooted hierarchy display that subsumes specgraph and provides lens-based filtering across all artifact views.

**Architecture:** New `VisionTree` renderer in the specgraph package renders vision-rooted trees from any node set. A `Lens` abstraction defines node selection, annotation, sort order, and default depth. `chart.sh` is the new shell entry point; `specgraph.sh` becomes a deprecated alias. The existing specgraph Python package (`graph.py`, `parser.py`, `priority.py`, etc.) is reused as-is for graph building and queries.

**Tech Stack:** Python 3 (no new dependencies), bash, jq (for session.json updates)

---

## Chunk 1: Foundation — VisionTree Renderer + Priority Cascade

### Task 1: Extend priority-weight to Epics

**Files:**
- Modify: `skills/swain-design/references/epic-definition.md`
- Modify: `skills/swain-design/references/epic-template.md.template`
- Modify: `skills/swain-design/scripts/specgraph/priority.py`
- Test: `skills/swain-design/scripts/tests/test_priority.py`

- [ ] **Step 1: Write the failing test for Epic-level priority override**

Add to `test_priority.py`:

```python
def test_epic_overrides_initiative_weight(self):
    """Epic with priority-weight overrides its parent initiative's weight."""
    nodes = {
        "VISION-001": {"status": "Active", "type": "VISION", "track": "standing",
                       "priority_weight": "high"},
        "INITIATIVE-001": {"status": "Active", "type": "INITIATIVE", "track": "container",
                           "priority_weight": "medium"},
        "EPIC-001": {"status": "Active", "type": "EPIC", "track": "container",
                     "priority_weight": "low"},
        "SPEC-001": {"status": "Proposed", "type": "SPEC", "track": "implementable"},
    }
    edges = [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
    ]
    # SPEC inherits from EPIC's override (low=1), not INITIATIVE (medium=2)
    assert resolve_vision_weight("SPEC-001", nodes, edges) == 1

def test_epic_without_weight_inherits_from_initiative(self):
    """Epic without priority-weight inherits from parent initiative."""
    nodes = {
        "VISION-001": {"status": "Active", "type": "VISION", "track": "standing",
                       "priority_weight": "high"},
        "INITIATIVE-001": {"status": "Active", "type": "INITIATIVE", "track": "container",
                           "priority_weight": "medium"},
        "EPIC-001": {"status": "Active", "type": "EPIC", "track": "container"},
        "SPEC-001": {"status": "Proposed", "type": "SPEC", "track": "implementable"},
    }
    edges = [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
    ]
    # SPEC inherits from INITIATIVE (medium=2) since EPIC has no weight
    assert resolve_vision_weight("SPEC-001", nodes, edges) == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd skills/swain-design/scripts && python -m pytest tests/test_priority.py -v -k "test_epic_overrides or test_epic_without_weight_inherits"`
Expected: FAIL — current `resolve_vision_weight` doesn't check EPIC nodes for `priority_weight`

- [ ] **Step 3: Update `resolve_vision_weight` to include Epic in cascade**

In `skills/swain-design/scripts/specgraph/priority.py`, update the `resolve_vision_weight` function. Currently it checks for `priority_weight` on VISION and INITIATIVE types. Add EPIC to the check:

```python
def resolve_vision_weight(artifact_id, nodes, edges):
    """Walk parent chain and return effective priority weight (int).

    Cascade: Vision -> Initiative (can override) -> Epic (can override) -> Spec (inherits).
    """
    node = nodes.get(artifact_id, {})
    # Check self first (VISION, INITIATIVE, or EPIC with explicit weight)
    pw = node.get("priority_weight")
    if pw and node.get("type") in ("VISION", "INITIATIVE", "EPIC"):
        return WEIGHT_MAP.get(pw, DEFAULT_WEIGHT)

    # Walk parent chain for nearest weight
    chain = _walk_parent_chain(artifact_id, edges)
    for parent_id in chain:
        parent = nodes.get(parent_id, {})
        ppw = parent.get("priority_weight")
        if ppw and parent.get("type") in ("VISION", "INITIATIVE", "EPIC"):
            return WEIGHT_MAP.get(ppw, DEFAULT_WEIGHT)

    return DEFAULT_WEIGHT
```

Note: `_walk_parent_chain` is imported from `queries.py` or duplicated locally. Check the existing import structure — if `priority.py` already has its own parent-chain walk, update that.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd skills/swain-design/scripts && python -m pytest tests/test_priority.py -v`
Expected: ALL PASS (including existing tests — no regressions)

- [ ] **Step 5: Update epic definition and template**

In `skills/swain-design/references/epic-definition.md`, after the line about `addresses:`, add:
```
- **Priority weight (optional):** `priority-weight: high | medium | low` in frontmatter. Overrides the parent Initiative/Vision weight for this Epic and its children. When absent, weight is inherited from the parent chain.
```

In `skills/swain-design/references/epic-template.md.template`, add after `parent-initiative:`:
```yaml
priority-weight: {{ priority_weight | default("") }}
```

- [ ] **Step 6: Commit**

```bash
git add skills/swain-design/scripts/specgraph/priority.py \
      skills/swain-design/scripts/tests/test_priority.py \
      skills/swain-design/references/epic-definition.md \
      skills/swain-design/references/epic-template.md.template
git commit -m "feat(specgraph): extend priority-weight cascade to epics

Epics can now override their parent Initiative/Vision weight.
Cascade: Vision -> Initiative -> Epic -> Spec (inherits nearest).

Part of SPEC-052."
```

---

### Task 2: VisionTree renderer — core tree building

**Files:**
- Create: `skills/swain-design/scripts/specgraph/tree_renderer.py`
- Test: `skills/swain-design/scripts/tests/test_tree_renderer.py`

- [ ] **Step 1: Write failing test for basic vision-rooted tree**

Create `skills/swain-design/scripts/tests/test_tree_renderer.py`:

```python
"""Tests for VisionTree renderer."""
import pytest
from specgraph.tree_renderer import render_vision_tree


def _make_nodes(**overrides):
    """Helper to create a minimal node set with a VISION > INITIATIVE > EPIC hierarchy."""
    base = {
        "VISION-001": {"status": "Active", "type": "VISION", "track": "standing",
                       "title": "Swain", "priority_weight": "high"},
        "INITIATIVE-001": {"status": "Active", "type": "INITIATIVE", "track": "container",
                           "title": "Operator Awareness"},
        "EPIC-001": {"status": "Active", "type": "EPIC", "track": "container",
                     "title": "Chart Hierarchy"},
        "SPEC-001": {"status": "Active", "type": "SPEC", "track": "implementable",
                     "title": "Tree Renderer"},
        "SPEC-002": {"status": "Active", "type": "SPEC", "track": "implementable",
                     "title": "CLI Entry Point"},
    }
    base.update(overrides)
    return base


def _make_edges():
    return [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
        {"from": "SPEC-002", "to": "EPIC-001", "type": "parent-epic"},
    ]


class TestRenderVisionTree:
    def test_basic_tree_depth_2(self):
        """At depth 2, epics are leaf nodes with child counts."""
        nodes = _make_nodes()
        edges = _make_edges()
        lines = render_vision_tree(
            nodes={"SPEC-001", "SPEC-002", "EPIC-001", "INITIATIVE-001", "VISION-001"},
            all_nodes=nodes,
            edges=edges,
            depth=2,
        )
        output = "\n".join(lines)
        assert "Swain" in output
        assert "Operator Awareness" in output
        assert "Chart Hierarchy" in output
        assert "2 specs" in output
        # At depth 2, individual specs should NOT appear
        assert "Tree Renderer" not in output
        assert "CLI Entry Point" not in output

    def test_basic_tree_depth_4(self):
        """At depth 4, individual specs appear."""
        nodes = _make_nodes()
        edges = _make_edges()
        lines = render_vision_tree(
            nodes={"SPEC-001", "SPEC-002", "EPIC-001", "INITIATIVE-001", "VISION-001"},
            all_nodes=nodes,
            edges=edges,
            depth=4,
        )
        output = "\n".join(lines)
        assert "Tree Renderer" in output
        assert "CLI Entry Point" in output

    def test_unanchored_section(self):
        """Artifacts without Vision ancestry appear in Unanchored section."""
        nodes = _make_nodes(**{
            "EPIC-099": {"status": "Active", "type": "EPIC", "track": "container",
                         "title": "Orphan Epic"},
        })
        edges = _make_edges()
        lines = render_vision_tree(
            nodes={"EPIC-099", "VISION-001", "INITIATIVE-001", "EPIC-001"},
            all_nodes=nodes,
            edges=edges,
            depth=2,
        )
        output = "\n".join(lines)
        assert "Unanchored" in output
        assert "Orphan Epic" in output

    def test_titles_are_primary_labels(self):
        """Titles should appear, IDs should NOT appear by default."""
        nodes = _make_nodes()
        edges = _make_edges()
        lines = render_vision_tree(
            nodes={"VISION-001", "INITIATIVE-001", "EPIC-001"},
            all_nodes=nodes,
            edges=edges,
            depth=2,
        )
        output = "\n".join(lines)
        assert "Swain" in output
        # IDs should be hidden by default
        assert "VISION-001" not in output

    def test_show_ids(self):
        """With show_ids=True, IDs appear alongside titles."""
        nodes = _make_nodes()
        edges = _make_edges()
        lines = render_vision_tree(
            nodes={"VISION-001", "INITIATIVE-001", "EPIC-001"},
            all_nodes=nodes,
            edges=edges,
            depth=2,
            show_ids=True,
        )
        output = "\n".join(lines)
        assert "VISION-001" in output
        assert "Swain" in output

    def test_legend_at_bottom(self):
        """Legend line appears at the bottom of output."""
        nodes = _make_nodes()
        edges = _make_edges()
        lines = render_vision_tree(
            nodes={"VISION-001"},
            all_nodes=nodes,
            edges=edges,
            depth=2,
        )
        output = "\n".join(lines)
        assert "ready" in output.split("\n")[-1].lower() or "blocked" in output.split("\n")[-1].lower()

    def test_flattening_when_intermediate_missing(self):
        """Spec directly under Initiative (no Epic) should flatten."""
        nodes = {
            "VISION-001": {"status": "Active", "type": "VISION", "track": "standing",
                           "title": "Swain"},
            "INITIATIVE-001": {"status": "Active", "type": "INITIATIVE", "track": "container",
                               "title": "Awareness"},
            "SPEC-001": {"status": "Active", "type": "SPEC", "track": "implementable",
                         "title": "Direct Spec"},
        }
        edges = [
            {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
            {"from": "SPEC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        ]
        lines = render_vision_tree(
            nodes={"VISION-001", "INITIATIVE-001", "SPEC-001"},
            all_nodes=nodes,
            edges=edges,
            depth=4,
        )
        output = "\n".join(lines)
        assert "Direct Spec" in output

    def test_sort_key(self):
        """Custom sort_key orders siblings."""
        nodes = {
            "VISION-001": {"status": "Active", "type": "VISION", "track": "standing",
                           "title": "Swain"},
            "EPIC-001": {"status": "Active", "type": "EPIC", "track": "container",
                         "title": "Zebra Epic"},
            "EPIC-002": {"status": "Active", "type": "EPIC", "track": "container",
                         "title": "Alpha Epic"},
        }
        edges = [
            {"from": "EPIC-001", "to": "VISION-001", "type": "parent-vision"},
            {"from": "EPIC-002", "to": "VISION-001", "type": "parent-vision"},
        ]
        # Default sort (alphabetical by title) — Alpha before Zebra
        lines = render_vision_tree(
            nodes={"VISION-001", "EPIC-001", "EPIC-002"},
            all_nodes=nodes,
            edges=edges,
            depth=2,
        )
        output = "\n".join(lines)
        alpha_pos = output.index("Alpha Epic")
        zebra_pos = output.index("Zebra Epic")
        assert alpha_pos < zebra_pos

    def test_phase_filter(self):
        """Phase filter excludes artifacts not in the specified phases."""
        nodes = _make_nodes(**{
            "SPEC-003": {"status": "Complete", "type": "SPEC", "track": "implementable",
                         "title": "Done Spec"},
        })
        edges = _make_edges() + [
            {"from": "SPEC-003", "to": "EPIC-001", "type": "parent-epic"},
        ]
        lines = render_vision_tree(
            nodes={"VISION-001", "INITIATIVE-001", "EPIC-001", "SPEC-001", "SPEC-002", "SPEC-003"},
            all_nodes=nodes,
            edges=edges,
            depth=4,
            phase_filter={"Active"},
        )
        output = "\n".join(lines)
        assert "Done Spec" not in output
        assert "Tree Renderer" in output
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd skills/swain-design/scripts && python -m pytest tests/test_tree_renderer.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'specgraph.tree_renderer'`

- [ ] **Step 3: Implement `tree_renderer.py`**

Create `skills/swain-design/scripts/specgraph/tree_renderer.py`:

```python
"""VisionTree renderer — renders artifact sets as vision-rooted hierarchy trees.

All lenses and surface integrations consume this renderer. It handles:
- Walking parent edges to Vision roots
- Including structural ancestors (dimmed)
- Flattening when intermediate levels are missing
- Elbow connector rendering
- Depth control and phase filtering
- Unanchored section for parentless artifacts
"""
from __future__ import annotations

from typing import Callable, Optional

from specgraph.resolved import is_resolved as _is_resolved_raw

_PARENT_EDGE_TYPES = {"parent-epic", "parent-vision", "parent-initiative"}
_LEVEL_ORDER = {"VISION": 0, "INITIATIVE": 1, "EPIC": 2, "SPEC": 3, "SPIKE": 3,
                "ADR": 3, "DESIGN": 3, "RUNBOOK": 3, "PERSONA": 3, "JOURNEY": 3}
_STATUS_ICONS = {"ready": "\u2192", "blocked": "\u2298", "in_progress": "\u00b7",
                 "resolved": "\u2713"}
_CHILD_TYPE_LABELS = {"SPEC": "spec", "SPIKE": "spike", "ADR": "adr", "DESIGN": "design",
                      "RUNBOOK": "runbook"}


def _node_is_resolved(artifact_id: str, nodes: dict) -> bool:
    """Wrapper: check if a node is resolved using its type/status/track."""
    node = nodes.get(artifact_id, {})
    return _is_resolved_raw(
        node.get("type", ""),
        node.get("status", ""),
        node.get("track"),
    )


def _get_children(parent_id: str, edges: list[dict]) -> list[str]:
    """Return artifact IDs that have parent_id as their parent."""
    children = []
    for e in edges:
        if e["type"] in _PARENT_EDGE_TYPES and e.get("to") == parent_id:
            children.append(e["from"])
    return children


def _walk_to_vision(artifact_id: str, edges: list[dict], visited: set | None = None) -> list[str]:
    """Walk parent edges from artifact up to Vision root. Returns path [self, ..., vision]."""
    if visited is None:
        visited = set()
    if artifact_id in visited:
        return [artifact_id]
    visited.add(artifact_id)
    chain = [artifact_id]
    for e in edges:
        if e["from"] == artifact_id and e["type"] in _PARENT_EDGE_TYPES:
            parent_chain = _walk_to_vision(e["to"], edges, visited)
            chain.extend(parent_chain)
            break
    return chain


def _child_count_label(parent_id: str, all_nodes: dict, edges: list[dict],
                       phase_filter: set[str] | None) -> str:
    """Compute child count summary like '3 specs, 1 spike'."""
    children = _get_children(parent_id, edges)
    counts: dict[str, int] = {}
    for cid in children:
        cnode = all_nodes.get(cid, {})
        if phase_filter and cnode.get("status") not in phase_filter:
            continue
        ctype = cnode.get("type", "SPEC")
        label = _CHILD_TYPE_LABELS.get(ctype, ctype.lower())
        counts[label] = counts.get(label, 0) + 1
    if not counts:
        return ""
    parts = []
    for label in ("spec", "spike", "adr", "design", "runbook"):
        if label in counts:
            n = counts[label]
            parts.append(f"{n} {label}{'s' if n != 1 else ''}")
    # Any remaining types
    for label, n in sorted(counts.items()):
        if label not in ("spec", "spike", "adr", "design", "runbook"):
            parts.append(f"{n} {label}{'s' if n != 1 else ''}")
    return ", ".join(parts)


def _compute_ready_set(nodes: dict, edges: list[dict]) -> set[str]:
    """Return set of artifact IDs that are unresolved and have all deps satisfied."""
    ready = set()
    for aid in nodes:
        if _node_is_resolved(aid, nodes):
            continue
        deps = [e["to"] for e in edges if e["from"] == aid and e["type"] == "depends-on"]
        if all(_node_is_resolved(d, nodes) for d in deps):
            ready.add(aid)
    return ready


def _status_icon(artifact_id: str, all_nodes: dict, edges: list[dict],
                 ready_set: set[str]) -> str:
    """Return status icon for an artifact."""
    if _node_is_resolved(artifact_id, all_nodes):
        return _STATUS_ICONS["resolved"]
    if artifact_id in ready_set:
        return _STATUS_ICONS["ready"]
    # Check if blocked (has unresolved deps)
    deps = [e["to"] for e in edges if e["from"] == artifact_id and e["type"] == "depends-on"]
    unresolved_deps = [d for d in deps if not _node_is_resolved(d, all_nodes)]
    if unresolved_deps:
        return _STATUS_ICONS["blocked"]
    return _STATUS_ICONS["in_progress"]


def _render_node_line(artifact_id: str, all_nodes: dict, edges: list[dict],
                      ready_set: set[str], annotations: dict[str, str],
                      show_ids: bool, depth: int, current_depth: int,
                      phase_filter: set[str] | None, is_structural: bool) -> str:
    """Render a single node's display text."""
    node = all_nodes.get(artifact_id, {})
    title = node.get("title", artifact_id)
    icon = _status_icon(artifact_id, all_nodes, edges, ready_set)

    # At depth limit, show child counts instead of expanding
    at_depth_limit = current_depth >= depth
    child_label = ""
    if at_depth_limit:
        cl = _child_count_label(artifact_id, all_nodes, edges, phase_filter)
        if cl:
            child_label = f"  {cl}"

    annotation = annotations.get(artifact_id, "")
    if annotation:
        annotation = f"  {annotation}"

    id_suffix = f" [{artifact_id}]" if show_ids else ""

    if is_structural:
        # Structural ancestors: no icon, no annotation
        return f"{title}{id_suffix}"
    else:
        return f"{icon} {title}{id_suffix}{child_label}{annotation}"


def _render_subtree(artifact_id: str, all_nodes: dict, edges: list[dict],
                    ready_set: set[str], annotations: dict[str, str],
                    sort_key: Callable, show_ids: bool, depth: int,
                    phase_filter: set[str] | None, display_nodes: set[str],
                    current_depth: int, prefix: str, is_last: bool,
                    lines: list[str], visited: set[str]) -> None:
    """Recursively render a subtree with elbow connectors."""
    if artifact_id in visited:
        return
    visited.add(artifact_id)

    node = all_nodes.get(artifact_id, {})

    # Phase filter
    if phase_filter and node.get("status") not in phase_filter:
        # But always show structural ancestors
        if artifact_id not in display_nodes:
            return

    is_structural = artifact_id not in display_nodes
    connector = "\u2514\u2500\u2500 " if is_last else "\u251c\u2500\u2500 "
    if current_depth == 0:
        connector = ""
        child_prefix = ""
    else:
        child_prefix = prefix + ("\u2502   " if not is_last else "    ")

    line = _render_node_line(artifact_id, all_nodes, edges, ready_set,
                             annotations, show_ids, depth, current_depth,
                             phase_filter, is_structural)
    lines.append(f"{prefix}{connector}{line}")

    # Stop expanding at depth limit
    if current_depth >= depth:
        return

    # Get and sort children
    children = _get_children(artifact_id, edges)
    # Filter to children that are in our node set or are structural ancestors
    visible_children = []
    for cid in children:
        cnode = all_nodes.get(cid, {})
        if phase_filter and cnode.get("status") not in phase_filter:
            if cid not in display_nodes:
                continue
        visible_children.append(cid)

    visible_children = sorted(visible_children, key=lambda c: sort_key(c, all_nodes, edges))

    for i, child_id in enumerate(visible_children):
        is_last_child = (i == len(visible_children) - 1)
        _render_subtree(child_id, all_nodes, edges, ready_set, annotations,
                        sort_key, show_ids, depth, phase_filter, display_nodes,
                        current_depth + 1, child_prefix, is_last_child,
                        lines, visited)


def _default_sort_key(artifact_id: str, all_nodes: dict, edges: list[dict]) -> str:
    """Default sort: alphabetical by title."""
    return all_nodes.get(artifact_id, {}).get("title", artifact_id).lower()


def render_vision_tree(
    nodes: set[str],
    all_nodes: dict,
    edges: list[dict],
    depth: int = 2,
    phase_filter: set[str] | None = None,
    annotations: dict[str, str] | None = None,
    sort_key: Callable | None = None,
    show_ids: bool = False,
) -> list[str]:
    """Render a vision-rooted hierarchy tree.

    Args:
        nodes: Set of artifact IDs to display (the lens's result set).
        all_nodes: Complete node dict from graph cache.
        edges: Complete edge list from graph cache.
        depth: Max tree depth (0=Vision only, 2=strategic, 4=execution).
        phase_filter: If set, only show artifacts in these phases.
        annotations: Dict of artifact_id -> annotation string.
        sort_key: Callable(artifact_id, all_nodes, edges) -> sort value. Default: by title.
        show_ids: Whether to show artifact IDs alongside titles.

    Returns:
        List of rendered lines (join with newlines for display).
    """
    if annotations is None:
        annotations = {}
    if sort_key is None:
        sort_key = _default_sort_key

    ready_set = _compute_ready_set(all_nodes, edges)

    # Expand nodes to include structural ancestors
    display_nodes = set(nodes)
    all_ancestors: set[str] = set()
    for nid in nodes:
        chain = _walk_to_vision(nid, edges)
        all_ancestors.update(chain)

    # All nodes to render (display + structural ancestors)
    render_nodes = display_nodes | all_ancestors

    # Find vision roots
    vision_roots = sorted(
        [nid for nid in render_nodes
         if all_nodes.get(nid, {}).get("type") == "VISION"],
        key=lambda v: sort_key(v, all_nodes, edges)
    )

    # Find unanchored artifacts (in display set but can't reach a Vision)
    anchored = set()
    for nid in display_nodes:
        chain = _walk_to_vision(nid, edges)
        if any(all_nodes.get(c, {}).get("type") == "VISION" for c in chain):
            anchored.add(nid)
    unanchored = display_nodes - anchored

    lines: list[str] = []
    visited: set[str] = set()

    # Render each vision tree
    for i, vid in enumerate(vision_roots):
        if i > 0:
            lines.append("")
        _render_subtree(vid, all_nodes, edges, ready_set, annotations,
                        sort_key, show_ids, depth, phase_filter, display_nodes,
                        0, "", True, lines, visited)

    # Render unanchored section
    if unanchored:
        lines.append("")
        lines.append("=== Unanchored ===")
        for uid in sorted(unanchored, key=lambda u: sort_key(u, all_nodes, edges)):
            node = all_nodes.get(uid, {})
            title = node.get("title", uid)
            id_suffix = f" [{uid}]" if show_ids else ""
            # Show partial ancestry if available
            partial_chain = _walk_to_vision(uid, edges)
            if len(partial_chain) > 1:
                ancestors = " > ".join(
                    all_nodes.get(a, {}).get("title", a)
                    for a in reversed(partial_chain[1:])
                )
                lines.append(f"\u26a0 {title}{id_suffix} (under: {ancestors})")
            else:
                lines.append(f"\u26a0 {title}{id_suffix} [no Vision ancestry]")

    # Legend
    lines.append("")
    lines.append("---")
    lines.append("\u2192 ready   \u2298 blocked   \u00b7 in progress   \u2713 complete (hidden by default)")

    return lines


def render_breadcrumb(
    artifact_id: str,
    all_nodes: dict,
    edges: list[dict],
) -> str:
    """Render a Vision ancestry breadcrumb for an artifact.

    Returns string like: "Swain > Operator Awareness > Chart Hierarchy"
    """
    chain = _walk_to_vision(artifact_id, edges)
    # chain is [self, parent, ..., vision] — reverse for display
    titles = [
        all_nodes.get(aid, {}).get("title", aid)
        for aid in reversed(chain)
    ]
    return " > ".join(titles)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd skills/swain-design/scripts && python -m pytest tests/test_tree_renderer.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add skills/swain-design/scripts/specgraph/tree_renderer.py \
      skills/swain-design/scripts/tests/test_tree_renderer.py
git commit -m "feat(specgraph): add VisionTree renderer

Shared tree renderer that produces vision-rooted hierarchy trees.
Handles depth control, phase filtering, sort keys, unanchored
detection, elbow connectors, and ancestry breadcrumbs.

Part of SPEC-052."
```

---

## Chunk 2: CLI + Default Lens + Lens Framework

### Task 3: Lens abstraction and default lens

**Files:**
- Create: `skills/swain-design/scripts/specgraph/lenses.py`
- Test: `skills/swain-design/scripts/tests/test_lenses.py`

- [ ] **Step 1: Write failing test for default lens**

Create `skills/swain-design/scripts/tests/test_lenses.py`:

```python
"""Tests for chart lenses."""
import pytest
from specgraph.lenses import DefaultLens, ReadyLens, RecommendLens, UnanchoredLens


def _make_graph():
    nodes = {
        "VISION-001": {"status": "Active", "type": "VISION", "track": "standing",
                       "title": "Swain", "priority_weight": "high"},
        "INITIATIVE-001": {"status": "Active", "type": "INITIATIVE", "track": "container",
                           "title": "Awareness"},
        "EPIC-001": {"status": "Active", "type": "EPIC", "track": "container",
                     "title": "Chart"},
        "SPEC-001": {"status": "Active", "type": "SPEC", "track": "implementable",
                     "title": "Renderer"},
        "SPEC-002": {"status": "Complete", "type": "SPEC", "track": "implementable",
                     "title": "Done Spec"},
    }
    edges = [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
        {"from": "SPEC-002", "to": "EPIC-001", "type": "parent-epic"},
    ]
    return nodes, edges


class TestDefaultLens:
    def test_selects_non_terminal(self):
        nodes, edges = _make_graph()
        lens = DefaultLens()
        selected = lens.select(nodes, edges)
        assert "SPEC-001" in selected
        assert "SPEC-002" not in selected  # Complete = terminal

    def test_default_depth_is_strategic(self):
        lens = DefaultLens()
        assert lens.default_depth == 2

    def test_sort_key_is_alphabetical(self):
        nodes, edges = _make_graph()
        lens = DefaultLens()
        key_fn = lens.sort_key
        # Alphabetical by title
        assert key_fn("SPEC-001", nodes, edges) < key_fn("VISION-001", nodes, edges)


class TestReadyLens:
    def test_selects_only_ready(self):
        nodes, edges = _make_graph()
        lens = ReadyLens()
        selected = lens.select(nodes, edges)
        # SPEC-001 is ready (no unresolved deps), SPEC-002 is complete
        assert "SPEC-001" in selected
        assert "SPEC-002" not in selected

    def test_default_depth_is_execution(self):
        lens = ReadyLens()
        assert lens.default_depth == 4


class TestUnanchoredLens:
    def test_selects_only_unanchored(self):
        nodes, edges = _make_graph()
        nodes["EPIC-099"] = {"status": "Active", "type": "EPIC", "track": "container",
                             "title": "Orphan"}
        lens = UnanchoredLens()
        selected = lens.select(nodes, edges)
        assert "EPIC-099" in selected
        assert "SPEC-001" not in selected
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd skills/swain-design/scripts && python -m pytest tests/test_lenses.py -v`
Expected: FAIL — module doesn't exist

- [ ] **Step 3: Implement `lenses.py`**

Create `skills/swain-design/scripts/specgraph/lenses.py`:

```python
"""Chart lenses — define node selection, annotation, sort order, and default depth.

Each lens answers a different question about the project hierarchy.
The tree renderer handles display; lenses handle semantics.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable

from specgraph.resolved import is_resolved as _is_resolved_raw
from specgraph.priority import resolve_vision_weight, WEIGHT_MAP, rank_recommendations, compute_decision_debt
from specgraph.tree_renderer import _compute_ready_set, _walk_to_vision, _node_is_resolved


class Lens(ABC):
    """Base class for chart lenses."""

    @property
    @abstractmethod
    def default_depth(self) -> int:
        """Default tree depth (2=strategic, 4=execution)."""
        ...

    @abstractmethod
    def select(self, nodes: dict, edges: list[dict]) -> set[str]:
        """Select which artifact IDs to display."""
        ...

    def annotate(self, nodes: dict, edges: list[dict]) -> dict[str, str]:
        """Return annotations for displayed nodes. Default: empty."""
        return {}

    def sort_key(self, artifact_id: str, nodes: dict, edges: list[dict]) -> tuple:
        """Sort key for ordering siblings. Default: alphabetical by title.

        Note: edges parameter allows lenses to compute dependency-aware sort values.
        """
        return (nodes.get(artifact_id, {}).get("title", artifact_id).lower(),)


class DefaultLens(Lens):
    """Default overview — all non-terminal artifacts with status icons."""

    @property
    def default_depth(self) -> int:
        return 2

    def select(self, nodes: dict, edges: list[dict]) -> set[str]:
        return {aid for aid in nodes if not _node_is_resolved(aid, nodes)}


class ReadyLens(Lens):
    """Unblocked artifacts ready for work."""

    @property
    def default_depth(self) -> int:
        return 4

    def select(self, nodes: dict, edges: list[dict]) -> set[str]:
        return _compute_ready_set(nodes, edges)

    def sort_key(self, artifact_id: str, nodes: dict, edges: list[dict]) -> tuple:
        # Sort by unblock count desc, then title
        unblock_count = sum(
            1 for e in edges
            if e.get("to") == artifact_id and e.get("type") == "depends-on"
            and not _node_is_resolved(e["from"], nodes)
        )
        title = nodes.get(artifact_id, {}).get("title", artifact_id).lower()
        return (-unblock_count, title)


class RecommendLens(Lens):
    """Scored by priority x unblock count."""

    def __init__(self, focus_vision: str | None = None):
        self._focus = focus_vision
        self._scores: dict[str, int] = {}

    @property
    def default_depth(self) -> int:
        return 2

    def select(self, nodes: dict, edges: list[dict]) -> set[str]:
        ranked = rank_recommendations(nodes, edges, focus_vision=self._focus)
        self._scores = {item["id"]: item["score"] for item in ranked}
        return {item["id"] for item in ranked}

    def annotate(self, nodes: dict, edges: list[dict]) -> dict[str, str]:
        ranked = rank_recommendations(nodes, edges, focus_vision=self._focus)
        return {item["id"]: f"score={item['score']}" for item in ranked}

    def sort_key(self, artifact_id: str, nodes: dict, edges: list[dict]) -> tuple:
        # Higher score first; use cached scores, fall back to weight calc
        score = self._scores.get(artifact_id)
        if score is None:
            weight = resolve_vision_weight(artifact_id, nodes, edges)
            unblock_count = sum(
                1 for e in edges
                if e.get("to") == artifact_id and e.get("type") == "depends-on"
                and not _node_is_resolved(e["from"], nodes)
            )
            score = unblock_count * weight
        title = nodes.get(artifact_id, {}).get("title", artifact_id).lower()
        return (-score, title)


class AttentionLens(Lens):
    """Recent git activity per vision."""

    def __init__(self, days: int = 30):
        self._days = days

    @property
    def default_depth(self) -> int:
        return 2

    def select(self, nodes: dict, edges: list[dict]) -> set[str]:
        # Select all non-terminal — attention annotates rather than filters
        return {aid for aid in nodes if not _node_is_resolved(aid, nodes)}

    def annotate(self, nodes: dict, edges: list[dict]) -> dict[str, str]:
        # Attention data requires git log — computed at CLI level, passed in
        return {}


class DebtLens(Lens):
    """Unresolved decision-type artifacts (Proposed Spikes, ADRs, Epics)."""

    @property
    def default_depth(self) -> int:
        return 2

    def select(self, nodes: dict, edges: list[dict]) -> set[str]:
        debt = compute_decision_debt(nodes, edges)
        result = set()
        for vision_id, info in debt.items():
            # items is a list of artifact ID strings
            for item_id in info.get("items", []):
                result.add(item_id)
        return result

    def annotate(self, nodes: dict, edges: list[dict]) -> dict[str, str]:
        debt = compute_decision_debt(nodes, edges)
        annotations = {}
        for vision_id, info in debt.items():
            for item_id in info.get("items", []):
                # Use created date from node if available, otherwise mark unknown
                node = nodes.get(item_id, {})
                status = node.get("status", "")
                annotations[item_id] = f"[{status}]"
        return annotations

    def sort_key(self, artifact_id: str, nodes: dict, edges: list[dict]) -> tuple:
        return (nodes.get(artifact_id, {}).get("title", artifact_id).lower(),)


class UnanchoredLens(Lens):
    """Artifacts with no Vision ancestry."""

    @property
    def default_depth(self) -> int:
        return 2

    def select(self, nodes: dict, edges: list[dict]) -> set[str]:
        unanchored = set()
        for aid in nodes:
            chain = _walk_to_vision(aid, edges)
            has_vision = any(
                nodes.get(c, {}).get("type") == "VISION" for c in chain
            )
            if not has_vision and not _node_is_resolved(aid, nodes):
                unanchored.add(aid)
        return unanchored


class StatusLens(Lens):
    """All artifacts grouped by phase."""

    @property
    def default_depth(self) -> int:
        return 2

    def select(self, nodes: dict, edges: list[dict]) -> set[str]:
        return set(nodes.keys())

    def annotate(self, nodes: dict, edges: list[dict]) -> dict[str, str]:
        return {aid: f"[{node.get('status', '?')}]" for aid, node in nodes.items()}

    def sort_key(self, artifact_id: str, nodes: dict, edges: list[dict]) -> tuple:
        # Sort by phase progression
        phase_order = {"Proposed": 0, "Active": 1, "Ready": 1, "InProgress": 2,
                       "NeedsManualTest": 3, "Complete": 4, "Abandoned": 5}
        status = nodes.get(artifact_id, {}).get("status", "")
        return (phase_order.get(status, 99), nodes.get(artifact_id, {}).get("title", "").lower())


# Lens registry
LENSES = {
    "default": DefaultLens,
    "ready": ReadyLens,
    "recommend": RecommendLens,
    "attention": AttentionLens,
    "debt": DebtLens,
    "unanchored": UnanchoredLens,
    "status": StatusLens,
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd skills/swain-design/scripts && python -m pytest tests/test_lenses.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add skills/swain-design/scripts/specgraph/lenses.py \
      skills/swain-design/scripts/tests/test_lenses.py
git commit -m "feat(specgraph): add lens framework for swain chart

Seven lenses: default, ready, recommend, attention, debt,
unanchored, status. Each defines node selection, annotation,
sort order, and default depth.

Part of SPEC-052."
```

---

### Task 4: `chart.sh` shell wrapper and CLI entry point

**Files:**
- Create: `skills/swain-design/scripts/chart.sh`
- Modify: `skills/swain-design/scripts/specgraph/cli.py`

- [ ] **Step 1: Create `chart.sh` shell wrapper**

Create `skills/swain-design/scripts/chart.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
# swain chart — vision-rooted hierarchy display
# Subsumes specgraph. All commands route through the Python CLI.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH:-}"

exec python3 "${SCRIPT_DIR}/specgraph.py" "$@"
```

Make executable: `chmod +x skills/swain-design/scripts/chart.sh`

The existing `specgraph.py` entry point calls `cli.main()`. We'll update `cli.py` to support the new lens-based commands.

- [ ] **Step 2: Update `cli.py` to support lens commands**

Add new subcommands to the argparse setup in `cli.py`. Keep all existing commands working (backward compat). Add new lens-based commands that route through the tree renderer.

At the top of `main()` in `cli.py`, after the existing subcommand parsers, add:

```python
# --- Lens-based tree commands (swain chart) ---
# These produce vision-rooted tree output via the tree renderer.

# Common args for all tree commands
def _add_tree_args(parser):
    parser.add_argument("--depth", type=int, default=None,
                        help="Tree depth (2=strategic, 4=execution)")
    parser.add_argument("--detail", action="store_const", const=4, dest="depth",
                        help="Alias for --depth 4")
    parser.add_argument("--phase", type=str, default=None,
                        help="Comma-separated phases to include")
    parser.add_argument("--hide-terminal", action="store_true",
                        help="Exclude terminal-phase artifacts")
    parser.add_argument("--flat", action="store_true",
                        help="Flat list output (no tree)")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="JSON output")
    parser.add_argument("--ids", action="store_true",
                        help="Show artifact IDs alongside titles")
```

Then add handling in the command dispatch to instantiate the appropriate lens, call `lens.select()` and `lens.annotate()`, compute depth (explicit > focus lane > lens default), apply phase filter, and call `render_vision_tree()`.

The full implementation handles:
1. Parse `--phase` into a set
2. Read focus lane from `.agents/session.json` if no `--depth` given
3. Instantiate the lens
4. Call `lens.select(nodes, edges)` to get node set
5. Call `lens.annotate(nodes, edges)` to get annotations
6. Determine effective depth
7. Call `render_vision_tree(...)` or format as flat/json
8. Print output

- [ ] **Step 3: Test end-to-end**

Run: `bash skills/swain-design/scripts/chart.sh`
Expected: Vision-rooted tree output with Swain as root, titles as labels

Run: `bash skills/swain-design/scripts/chart.sh ready`
Expected: Ready artifacts in tree form

Run: `bash skills/swain-design/scripts/chart.sh --ids`
Expected: Same tree with artifact IDs shown

Run: `bash skills/swain-design/scripts/chart.sh --flat`
Expected: Flat list output

- [ ] **Step 4: Make `specgraph.sh` a deprecated alias**

Add a deprecation notice to `specgraph.sh` (at the top, after set):

```bash
# DEPRECATED: Use chart.sh instead. This wrapper will be removed in a future version.
if [[ "${SWAIN_SPECGRAPH_NO_DEPRECATION_WARNING:-}" != "1" ]]; then
    echo "Warning: specgraph.sh is deprecated. Use 'swain chart' instead." >&2
fi
```

- [ ] **Step 5: Commit**

```bash
git add skills/swain-design/scripts/chart.sh \
      skills/swain-design/scripts/specgraph/cli.py \
      skills/swain-design/scripts/specgraph.sh
git commit -m "feat: add swain chart CLI entry point

chart.sh routes through the specgraph Python package with lens-based
tree rendering. specgraph.sh becomes a deprecated alias.

Part of SPEC-052."
```

---

## Chunk 3: Specgraph Subsumption + Surface Integrations

### Task 5: Rename `specgraph tree` to `deps` and add all subcommand aliases

**Files:**
- Modify: `skills/swain-design/scripts/specgraph/cli.py`

- [ ] **Step 1: Add `deps` as alias for `tree` in argparse**

In `cli.py`, find the `tree` subparser and add `deps` as an alias:

```python
# Rename: 'tree' shows dependency closure, not hierarchy
p_deps = sub.add_parser("deps", help="Transitive dependency closure (ancestors)")
p_deps.add_argument("id", help="Artifact ID")
# Keep 'tree' as hidden alias for backward compat
p_tree = sub.add_parser("tree", help=argparse.SUPPRESS)
p_tree.add_argument("id", help="Artifact ID")
```

In the dispatch section, handle both `deps` and `tree` the same way.

- [ ] **Step 2: Test**

Run: `bash skills/swain-design/scripts/chart.sh deps SPEC-001 2>/dev/null`
Expected: Same output as `specgraph tree SPEC-001`

- [ ] **Step 3: Commit**

```bash
git add skills/swain-design/scripts/specgraph/cli.py
git commit -m "feat: rename 'tree' to 'deps' for clarity, keep backward alias

Part of SPEC-052."
```

### Task 6: Surface integration — swain-session breadcrumb

**Files:**
- Modify: `skills/swain-session/scripts/swain-bookmark.sh`
- Modify: `skills/swain-session/SKILL.md`

- [ ] **Step 1: Add breadcrumb generation to bookmark display**

When `swain-bookmark.sh` is called without arguments (display mode), or when the bookmark is shown on session resume, include the Vision ancestry breadcrumb if the bookmark references an artifact.

This requires a helper that calls specgraph to get the parent chain. Add to `swain-bookmark.sh`:

```bash
# --- Breadcrumb helper ---
_ancestry_breadcrumb() {
    local artifact_id="$1"
    local chart_sh
    chart_sh="$(find "$REPO_ROOT" -path '*/swain-design/scripts/chart.sh' -print -quit 2>/dev/null)"
    if [[ -n "$chart_sh" && -n "$artifact_id" ]]; then
        python3 -c "
import sys; sys.path.insert(0, '$(dirname "$chart_sh")')
from specgraph.graph import cache_path, read_cache, build_graph, needs_rebuild, write_cache, repo_hash
from specgraph.tree_renderer import render_breadcrumb
rr = '$REPO_ROOT'
cp = cache_path(rr)
if needs_rebuild(cp, rr + '/docs'):
    data = build_graph(rr); write_cache(data, cp)
else:
    data = read_cache(cp)
print(render_breadcrumb('$artifact_id', data['nodes'], data['edges']))
" 2>/dev/null || true
    fi
}
```

- [ ] **Step 2: Update SKILL.md to describe breadcrumb behavior**

Add a line to swain-session SKILL.md noting that bookmark display includes Vision ancestry breadcrumb when the bookmark note contains an artifact ID.

- [ ] **Step 3: Test**

Set a bookmark referencing an artifact, then display it:
```bash
bash skills/swain-session/scripts/swain-bookmark.sh "Working on SPEC-052" --files docs/spec/Active/\(SPEC-052\)-Vision-Rooted-Chart-Hierarchy/\(SPEC-052\)-Vision-Rooted-Chart-Hierarchy.md
```
Expected: On next display, should show ancestry breadcrumb.

- [ ] **Step 4: Commit**

```bash
git add skills/swain-session/scripts/swain-bookmark.sh skills/swain-session/SKILL.md
git commit -m "feat(swain-session): add Vision ancestry breadcrumb to bookmarks

Part of SPEC-052."
```

### Task 7: Surface integration — swain-status tree view

**Files:**
- Modify: `skills/swain-status/SKILL.md`

- [ ] **Step 1: Update SKILL.md to use chart.sh for status output**

In swain-status SKILL.md, update the instructions to use `chart.sh` for the artifact summary section instead of flat specgraph output. The status script should:

1. Run `chart.sh recommend --json` to get ranked artifacts in tree form
2. Use the tree output as the primary status view
3. Respect focus lane (already handled by chart.sh via session.json)

Update the relevant section in SKILL.md:

```markdown
## Artifact summary

Run `bash skills/swain-design/scripts/chart.sh recommend` to get the vision-rooted
hierarchy with priority-scored recommendations. This replaces the flat artifact listing.
If focus lane is set, chart.sh automatically scopes to that vision/initiative.
```

- [ ] **Step 2: Commit**

```bash
git add skills/swain-status/SKILL.md
git commit -m "feat(swain-status): use vision-rooted chart for artifact summary

Part of SPEC-052."
```

### Task 8: Surface integration — swain-do ancestry breadcrumb

**Files:**
- Modify: `skills/swain-do/SKILL.md`

- [ ] **Step 1: Update SKILL.md to show ancestry when claiming work**

Add instruction to swain-do SKILL.md that when a task is claimed, if it has a `spec:SPEC-NNN` tag, show the ancestry breadcrumb:

```markdown
## Context on claim

When claiming a task tagged with `spec:<ID>`, show the Vision ancestry breadcrumb
to provide strategic context:

```bash
bash skills/swain-design/scripts/chart.sh scope <SPEC-ID> 2>/dev/null | head -1
```

This tells the agent/operator how the current task connects to project strategy.
```

- [ ] **Step 2: Commit**

```bash
git add skills/swain-do/SKILL.md
git commit -m "feat(swain-do): show ancestry breadcrumb on task claim

Part of SPEC-052."
```

### Task 9: Unanchored enforcement in swain-design

**Files:**
- Modify: `skills/swain-design/SKILL.md` (or `.claude/skills/swain-design/SKILL.md`)

- [ ] **Step 1: Add creation-time warning**

In the swain-design SKILL.md, in the "Creating artifacts" section (step 7, after validating parent references), add:

```markdown
7a. **Unanchored check** — after validating parent references, check if the new artifact
has a path to a Vision via parent edges. If not, warn:
`⚠ No Vision ancestry — this artifact will appear as Unanchored`
Offer to attach to an existing Initiative or Epic. Do not block creation.
```

- [ ] **Step 2: Add audit check**

In the "Auditing artifacts" section, add unanchored detection to the audit procedure (reference `references/auditing.md`):

```markdown
Add an **unanchored check** alongside alignment and ADR compliance:
Run `bash skills/swain-design/scripts/chart.sh unanchored` and report any findings.
```

- [ ] **Step 3: Commit**

```bash
git add skills/swain-design/SKILL.md .claude/skills/swain-design/SKILL.md
git commit -m "feat(swain-design): add unanchored warnings at creation and audit

Part of SPEC-052."
```

### Task 10: Update specgraph-guide reference doc

**Files:**
- Modify: `skills/swain-design/references/specgraph-guide.md`

- [ ] **Step 1: Update the reference doc to reflect `swain chart` subsumption**

Update the command table, add the new lens commands, note the deprecation of `specgraph.sh`, and document the new CLI interface. Include the lens descriptions, depth control, phase filtering, and output modes.

- [ ] **Step 2: Commit**

```bash
git add skills/swain-design/references/specgraph-guide.md
git commit -m "docs: update specgraph guide for swain chart subsumption

Part of SPEC-052."
```

---

## Implementation Notes

### File structure summary

```
skills/swain-design/scripts/
├── chart.sh                          # NEW — swain chart entry point
├── specgraph.sh                      # MODIFIED — deprecated alias
├── specgraph.py                      # UNCHANGED — entry point for Python CLI
├── specgraph/
│   ├── __init__.py                   # UNCHANGED
│   ├── cli.py                        # MODIFIED — add lens commands + tree args
│   ├── graph.py                      # UNCHANGED (already parses priority_weight)
│   ├── parser.py                     # UNCHANGED
│   ├── queries.py                    # UNCHANGED (low-level queries still available)
│   ├── priority.py                   # MODIFIED — Epic in cascade
│   ├── attention.py                  # UNCHANGED (reused by attention lens)
│   ├── resolved.py                   # UNCHANGED
│   ├── xref.py                       # UNCHANGED
│   ├── links.py                      # UNCHANGED
│   ├── tree_renderer.py              # NEW — VisionTree renderer + breadcrumb
│   └── lenses.py                     # NEW — 7 lens implementations
└── tests/
    ├── test_tree_renderer.py          # NEW
    ├── test_lenses.py                 # NEW
    ├── test_priority.py               # MODIFIED — Epic cascade tests
    └── ... (existing tests unchanged)
```

### Testing strategy

- Unit tests for tree_renderer.py (rendering, depth, filtering, unanchored, sort)
- Unit tests for lenses.py (node selection, annotations, sort keys)
- Unit tests for priority.py epic cascade (existing test file extended)
- Integration tests via chart.sh against the real repo artifacts
- All existing specgraph tests must continue passing (no regressions)

### Migration path

1. `chart.sh` is the new entry point
2. `specgraph.sh` continues working with a deprecation warning
3. All skill SKILL.md files updated to reference `chart.sh`
4. `specgraph.sh` removal is a future cleanup task (not in this spec)
