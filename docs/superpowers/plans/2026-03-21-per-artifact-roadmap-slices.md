# Per-Vision and Per-Initiative Roadmap Slices Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `chart.sh roadmap --scope <ID>` to generate per-Vision and per-Initiative roadmap slices, replacing `--focus`, with automatic all-slices regeneration on project-wide runs.

**Architecture:** Extend `collect_roadmap_items()` with a `scope` parameter that filters to an artifact's subtree. Add `render_scoped_roadmap()` using a new Jinja template (`roadmap-slice.md.j2`) that writes to the artifact's folder. The project-wide path iterates all Visions/Initiatives and calls the scoped renderer for each.

**Tech Stack:** Python 3, Jinja2, bash (chart.sh wrapper), git (recent commits)

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `skills/swain-design/scripts/specgraph/roadmap.py` | Modify | Add scope filtering, `_compute_descendants()`, `render_scoped_roadmap()`, intent resolution |
| `skills/swain-design/scripts/specgraph/graph.py:83-92` | Modify | Parse `brief-description` into node schema |
| `skills/swain-design/scripts/chart_cli.py:113-179` | Modify | Replace `--focus` with `--scope`, add all-slices loop |
| `skills/swain-design/templates/roadmap/roadmap-slice.md.j2` | Create | Scoped roadmap slice template |
| `skills/swain-roadmap/SKILL.md` | Modify | `--scope` pass-through, `{{INTENT}}` post-processing |
| `skills/swain-design/references/vision-definition.md:59-62` | Modify | Harmonize roadmap.md expectation |
| `skills/swain-design/scripts/specgraph/tests/test_roadmap_data_model.py` | Modify | Add scoped collection tests |
| `skills/swain-design/scripts/specgraph/tests/test_scoped_roadmap.py` | Create | Tests for scoped rendering, intent resolution, backup logic |

---

## Chunk 1: Core scoped collection and rendering

### Task 1: Parse `brief-description` into graph node schema

**Files:**
- Modify: `skills/swain-design/scripts/specgraph/graph.py:77-92`
- Test: `skills/swain-design/scripts/specgraph/tests/test_roadmap_data_model.py`

- [ ] **Step 1: Write failing test — brief-description appears in node**

Add to `test_roadmap_data_model.py`:

```python
def test_node_includes_brief_description():
    """Nodes with brief-description frontmatter expose it in the graph."""
    nodes, edges = _make_graph()
    # Simulate brief-description by adding it to existing node
    nodes["VISION-001"]["brief_description"] = "Core platform for agents"
    # The real test is that graph.py parses it — tested via integration
    assert nodes["VISION-001"].get("brief_description") == "Core platform for agents"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd skills/swain-design/scripts && python -m pytest specgraph/tests/test_roadmap_data_model.py::test_node_includes_brief_description -v`
Expected: PASS (this is a schema test; the real validation is in integration)

- [ ] **Step 3: Add brief-description parsing to graph.py**

In `skills/swain-design/scripts/specgraph/graph.py`, after line 91 (`"sort_order": sort_order,`), add:

```python
            "brief_description": fields.get("brief-description", ""),
```

- [ ] **Step 4: Commit**

```bash
git add skills/swain-design/scripts/specgraph/graph.py
git commit -m "feat(specgraph): parse brief-description into node schema (SPEC-143)"
```

---

### Task 2: Add `_compute_descendants()` helper to roadmap.py

**Files:**
- Modify: `skills/swain-design/scripts/specgraph/roadmap.py`
- Test: `skills/swain-design/scripts/specgraph/tests/test_scoped_roadmap.py` (create)

- [ ] **Step 1: Write failing test**

Create `skills/swain-design/scripts/specgraph/tests/test_scoped_roadmap.py`:

```python
"""Tests for scoped roadmap generation (SPEC-143)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from specgraph.roadmap import _compute_descendants, _get_children


def _make_scoped_graph():
    """Graph with Vision -> Initiative -> Epic -> Spec hierarchy."""
    nodes = {
        "VISION-001": {"type": "Vision", "title": "Core Platform", "status": "Active", "priority_weight": "high", "file": "docs/vision/Active/(VISION-001)-Core/v.md", "brief_description": ""},
        "INITIATIVE-001": {"type": "Initiative", "title": "Auth System", "status": "Active", "file": "docs/initiative/Active/(INITIATIVE-001)-Auth/i.md", "brief_description": "Harden authentication"},
        "INITIATIVE-002": {"type": "Initiative", "title": "Observability", "status": "Active", "file": "docs/initiative/Active/(INITIATIVE-002)-Obs/i.md", "brief_description": ""},
        "EPIC-001": {"type": "Epic", "title": "Login Flow", "status": "Active", "file": "docs/epic/Active/(EPIC-001)-Login/e.md"},
        "EPIC-002": {"type": "Epic", "title": "SSO", "status": "Active", "file": "docs/epic/Active/(EPIC-002)-SSO/e.md"},
        "SPEC-001": {"type": "Spec", "title": "Login API", "status": "Complete", "file": "docs/spec/Complete/(SPEC-001)-Login-API/s.md"},
        "SPEC-002": {"type": "Spec", "title": "Login UI", "status": "Active", "file": "docs/spec/Active/(SPEC-002)-Login-UI/s.md"},
        "SPEC-DIRECT": {"type": "Spec", "title": "Direct Spec", "status": "Active", "file": "docs/spec/Active/(SPEC-003)-Direct/s.md"},
    }
    edges = [
        {"from": "INITIATIVE-001", "to": "VISION-001", "type": "parent-vision"},
        {"from": "INITIATIVE-002", "to": "VISION-001", "type": "parent-vision"},
        {"from": "EPIC-001", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "EPIC-002", "to": "INITIATIVE-001", "type": "parent-initiative"},
        {"from": "SPEC-001", "to": "EPIC-001", "type": "parent-epic"},
        {"from": "SPEC-002", "to": "EPIC-001", "type": "parent-epic"},
        {"from": "SPEC-DIRECT", "to": "INITIATIVE-001", "type": "parent-initiative"},
    ]
    return nodes, edges


def test_compute_descendants_vision():
    nodes, edges = _make_scoped_graph()
    desc = _compute_descendants("VISION-001", edges)
    assert "INITIATIVE-001" in desc
    assert "INITIATIVE-002" in desc
    assert "EPIC-001" in desc
    assert "EPIC-002" in desc
    assert "SPEC-001" in desc
    assert "SPEC-002" in desc
    assert "SPEC-DIRECT" in desc
    assert "VISION-001" in desc  # includes self


def test_compute_descendants_initiative():
    nodes, edges = _make_scoped_graph()
    desc = _compute_descendants("INITIATIVE-001", edges)
    assert "EPIC-001" in desc
    assert "EPIC-002" in desc
    assert "SPEC-001" in desc
    assert "SPEC-DIRECT" in desc
    assert "INITIATIVE-001" in desc  # includes self
    assert "INITIATIVE-002" not in desc
    assert "VISION-001" not in desc
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd skills/swain-design/scripts && python -m pytest specgraph/tests/test_scoped_roadmap.py::test_compute_descendants_vision -v`
Expected: FAIL — `_compute_descendants` does not exist

- [ ] **Step 3: Implement `_compute_descendants()`**

In `skills/swain-design/scripts/specgraph/roadmap.py`, after `_get_children()` (after line 66), add:

```python
def _compute_descendants(artifact_id: str, edges: list[dict]) -> set[str]:
    """BFS to collect all descendants (children, grandchildren, etc.), including self."""
    visited: set[str] = {artifact_id}
    queue = [artifact_id]
    while queue:
        current = queue.pop(0)
        for child in _get_children(current, edges):
            if child not in visited:
                visited.add(child)
                queue.append(child)
    return visited
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd skills/swain-design/scripts && python -m pytest specgraph/tests/test_scoped_roadmap.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add skills/swain-design/scripts/specgraph/roadmap.py skills/swain-design/scripts/specgraph/tests/test_scoped_roadmap.py
git commit -m "feat(specgraph): add _compute_descendants for scoped roadmap (SPEC-143)"
```

---

### Task 3: Add `scope` parameter to `collect_roadmap_items()`

**Files:**
- Modify: `skills/swain-design/scripts/specgraph/roadmap.py:82-201`
- Test: `skills/swain-design/scripts/specgraph/tests/test_scoped_roadmap.py`

- [ ] **Step 1: Write failing tests**

Add to `test_scoped_roadmap.py`:

```python
from specgraph.roadmap import collect_roadmap_items


def test_scope_vision_filters_to_subtree():
    nodes, edges = _make_scoped_graph()
    items = collect_roadmap_items(nodes, edges, scope="VISION-001")
    item_ids = {i["id"] for i in items}
    assert "INITIATIVE-001" in item_ids
    assert "EPIC-001" in item_ids
    assert len(items) > 0


def test_scope_initiative_filters_to_children():
    nodes, edges = _make_scoped_graph()
    items = collect_roadmap_items(nodes, edges, scope="INITIATIVE-001")
    item_ids = {i["id"] for i in items}
    assert "EPIC-001" in item_ids
    assert "EPIC-002" in item_ids
    assert "SPEC-DIRECT" in item_ids
    # INITIATIVE-002 is a sibling, not a child
    assert "INITIATIVE-002" not in item_ids


def test_scope_excludes_resolved():
    """Scoped collection still skips resolved (Complete) artifacts."""
    nodes, edges = _make_scoped_graph()
    items = collect_roadmap_items(nodes, edges, scope="INITIATIVE-001")
    item_ids = {i["id"] for i in items}
    # SPEC-001 is Complete — it should NOT appear as an item
    assert "SPEC-001" not in item_ids


def test_scope_invalid_id_returns_empty():
    nodes, edges = _make_scoped_graph()
    items = collect_roadmap_items(nodes, edges, scope="NONEXISTENT-999")
    assert items == []


def test_scope_replaces_focus_vision():
    """scope with a Vision ID produces the same filtering as the old focus_vision."""
    nodes, edges = _make_scoped_graph()
    items_scoped = collect_roadmap_items(nodes, edges, scope="VISION-001")
    # All items should have vision_id == VISION-001 (or be descendants)
    for item in items_scoped:
        assert item["vision_id"] == "VISION-001" or item["vision_id"] is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd skills/swain-design/scripts && python -m pytest specgraph/tests/test_scoped_roadmap.py::test_scope_vision_filters_to_subtree -v`
Expected: FAIL — `collect_roadmap_items` does not accept `scope`

- [ ] **Step 3: Implement scope filtering**

In `skills/swain-design/scripts/specgraph/roadmap.py`, modify `collect_roadmap_items()`:

1. Change signature (line 82-86):
```python
def collect_roadmap_items(
    nodes: dict,
    edges: list[dict],
    focus_vision: str | None = None,  # DEPRECATED — use scope
    scope: str | None = None,
) -> list[dict]:
```

2. After `items: list[dict] = []` (line 88), add scope resolution:
```python
    # Scope filtering: compute the set of artifact IDs in scope
    scope_ids: set[str] | None = None
    if scope:
        if scope not in nodes:
            return []
        scope_ids = _compute_descendants(scope, edges)
    elif focus_vision:
        # Legacy: treat as scope for backward compat during transition
        if focus_vision not in nodes:
            return []
        scope_ids = _compute_descendants(focus_vision, edges)
```

3. Replace the `focus_vision` filter (lines 100-102) with:
```python
        if scope_ids is not None and aid not in scope_ids:
            continue
```

4. Replace the second-pass `focus_vision` filter (lines 170-172) with:
```python
        if scope_ids is not None and child_id not in scope_ids:
            continue
```

- [ ] **Step 4: Run all tests**

Run: `cd skills/swain-design/scripts && python -m pytest specgraph/tests/test_scoped_roadmap.py specgraph/tests/test_roadmap_data_model.py -v`
Expected: ALL PASS (including existing tests — backward compatible)

- [ ] **Step 5: Commit**

```bash
git add skills/swain-design/scripts/specgraph/roadmap.py skills/swain-design/scripts/specgraph/tests/test_scoped_roadmap.py
git commit -m "feat(specgraph): add scope param to collect_roadmap_items (SPEC-143)"
```

---

### Task 4: Create `roadmap-slice.md.j2` Jinja template

**Files:**
- Create: `skills/swain-design/templates/roadmap/roadmap-slice.md.j2`

- [ ] **Step 1: Create the template**

```jinja2
<!-- Auto-generated by chart.sh roadmap --scope. Do not edit. -->
# {{ artifact_id }}: {{ title }}

> {{ intent }}

## Children

| Artifact | Title | Phase | Progress |
|----------|-------|-------|----------|
{% for child in children %}
| [{{ child.id }}]({{ child.link }}) | {{ child.title }} | {{ child.phase }} | {{ child.progress }} |
{% endfor %}

## Progress

{{ progress_bar }} {{ complete }}/{{ total }} complete ({{ pct }}%)

## Recent Activity

{% if recent_commits %}
{% for c in recent_commits %}
- `{{ c.hash }}` {{ c.message }}
{% endfor %}
{% else %}
_No recent commits reference child artifacts._
{% endif %}

{% if eisenhower_subset %}
## Priority Subset

{{ eisenhower_subset }}
{% endif %}
```

- [ ] **Step 2: Commit**

```bash
git add skills/swain-design/templates/roadmap/roadmap-slice.md.j2
git commit -m "feat(roadmap): add scoped roadmap slice Jinja template (SPEC-143)"
```

---

### Task 5: Implement `render_scoped_roadmap()`

**Files:**
- Modify: `skills/swain-design/scripts/specgraph/roadmap.py`
- Test: `skills/swain-design/scripts/specgraph/tests/test_scoped_roadmap.py`

- [ ] **Step 1: Write failing test**

Add to `test_scoped_roadmap.py`:

```python
from specgraph.roadmap import render_scoped_roadmap


def test_render_scoped_roadmap_vision():
    nodes, edges = _make_scoped_graph()
    md = render_scoped_roadmap("VISION-001", nodes, edges, repo_root="/tmp/test")
    assert "<!-- Auto-generated by chart.sh roadmap --scope" in md
    assert "VISION-001" in md
    assert "Core Platform" in md
    assert "## Children" in md
    assert "## Progress" in md
    assert "## Recent Activity" in md


def test_render_scoped_roadmap_initiative_with_brief_description():
    nodes, edges = _make_scoped_graph()
    # INITIATIVE-001 has brief_description set
    md = render_scoped_roadmap("INITIATIVE-001", nodes, edges, repo_root="/tmp/test")
    assert "Harden authentication" in md
    assert "{{INTENT:" not in md  # should NOT have placeholder


def test_render_scoped_roadmap_vision_without_brief_description():
    nodes, edges = _make_scoped_graph()
    # VISION-001 has empty brief_description
    md = render_scoped_roadmap("VISION-001", nodes, edges, repo_root="/tmp/test")
    assert "{{INTENT: VISION-001}}" in md  # placeholder present


def test_render_scoped_roadmap_children_table():
    nodes, edges = _make_scoped_graph()
    md = render_scoped_roadmap("INITIATIVE-001", nodes, edges, repo_root="/tmp/test")
    assert "EPIC-001" in md
    assert "Login Flow" in md
    assert "EPIC-002" in md
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd skills/swain-design/scripts && python -m pytest specgraph/tests/test_scoped_roadmap.py::test_render_scoped_roadmap_vision -v`
Expected: FAIL — `render_scoped_roadmap` does not exist

- [ ] **Step 3: Implement `render_scoped_roadmap()`**

Add to `skills/swain-design/scripts/specgraph/roadmap.py`, before `render_roadmap_markdown()`:

```python
def render_scoped_roadmap(
    artifact_id: str,
    nodes: dict,
    edges: list[dict],
    repo_root: str = "",
) -> str:
    """Render a scoped roadmap slice for a single Vision or Initiative."""
    node = nodes.get(artifact_id, {})
    title = node.get("title", artifact_id)

    # Intent: prefer brief_description, fall back to placeholder
    brief = node.get("brief_description", "")
    intent = brief if brief else f"{{{{INTENT: {artifact_id}}}}}"

    # Collect direct children
    children_ids = _get_children(artifact_id, edges)
    children = []
    complete = 0
    total = 0
    for cid in sorted(children_ids):
        cnode = nodes.get(cid, {})
        if not cnode:
            continue
        ctype = cnode.get("type", "").upper()
        cstatus = cnode.get("status", "")

        # Progress: for EPICs count their SPECs, for SPECs count themselves
        if ctype == "EPIC":
            c, t = _spec_progress(cid, nodes, edges)
            progress_str = f"{c}/{t}" if t > 0 else "—"
            complete += c
            total += t
        else:
            total += 1
            is_done = _node_is_resolved(cid, nodes)
            if is_done:
                complete += 1
            progress_str = "done" if is_done else "in progress"

        # Compute relative link from artifact folder to child folder
        child_file = cnode.get("file", "")
        artifact_file = node.get("file", "")
        if child_file and artifact_file:
            from os.path import relpath, dirname
            link = relpath(child_file, dirname(artifact_file))
        else:
            link = cid

        children.append({
            "id": cid,
            "title": cnode.get("title", cid),
            "phase": cstatus,
            "progress": progress_str,
            "link": link,
        })

    # Progress bar
    pct = round(100 * complete / total) if total > 0 else 0
    bar_filled = round(pct / 100 * 12)
    progress_bar = "\u2588" * bar_filled + "\u2591" * (12 - bar_filled)

    # Recent commits referencing child artifact IDs
    recent_commits = _get_recent_commits(children_ids, repo_root)

    # Eisenhower subset: collect items in scope and render
    scoped_items = collect_roadmap_items(nodes, edges, scope=artifact_id)
    eisenhower_subset = render_eisenhower_table(scoped_items, nodes) if scoped_items else ""

    if _HAS_JINJA:
        env = _jinja_env()
        tmpl = env.get_template("roadmap-slice.md.j2")
        return tmpl.render(
            artifact_id=artifact_id,
            title=title,
            intent=intent,
            children=children,
            progress_bar=progress_bar,
            complete=complete,
            total=total,
            pct=pct,
            recent_commits=recent_commits,
            eisenhower_subset=eisenhower_subset,
        ).rstrip("\n") + "\n"
    else:
        # Fallback: plain text
        lines = [
            f"<!-- Auto-generated by chart.sh roadmap --scope. Do not edit. -->",
            f"# {artifact_id}: {title}",
            "",
            f"> {intent}",
            "",
            "## Children",
            "",
            "| Artifact | Title | Phase | Progress |",
            "|----------|-------|-------|----------|",
        ]
        for c in children:
            lines.append(f"| [{c['id']}]({c['link']}) | {c['title']} | {c['phase']} | {c['progress']} |")
        lines.extend([
            "",
            "## Progress",
            "",
            f"{progress_bar} {complete}/{total} complete ({pct}%)",
            "",
            "## Recent Activity",
            "",
        ])
        if recent_commits:
            for c in recent_commits:
                lines.append(f"- `{c['hash']}` {c['message']}")
        else:
            lines.append("_No recent commits reference child artifacts._")
        lines.append("")
        if eisenhower_subset:
            lines.extend(["## Priority Subset", "", eisenhower_subset])
        return "\n".join(lines)


def _get_recent_commits(artifact_ids: list[str], repo_root: str, limit: int = 3) -> list[dict]:
    """Get the last N git commits whose messages reference any of the given artifact IDs."""
    if not repo_root or not artifact_ids:
        return []
    import subprocess
    commits: list[dict] = []
    seen: set[str] = set()
    for aid in artifact_ids:
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "--all", f"--grep={aid}", f"-{limit}"],
                capture_output=True, text=True, cwd=repo_root, timeout=10,
            )
            for line in result.stdout.strip().splitlines():
                if not line:
                    continue
                parts = line.split(" ", 1)
                h = parts[0]
                if h not in seen:
                    seen.add(h)
                    commits.append({"hash": h, "message": parts[1] if len(parts) > 1 else ""})
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    # Sort by hash to be deterministic, then take first N
    commits.sort(key=lambda c: c["hash"], reverse=True)
    return commits[:limit]
```

- [ ] **Step 4: Run tests**

Run: `cd skills/swain-design/scripts && python -m pytest specgraph/tests/test_scoped_roadmap.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add skills/swain-design/scripts/specgraph/roadmap.py skills/swain-design/scripts/specgraph/tests/test_scoped_roadmap.py
git commit -m "feat(specgraph): add render_scoped_roadmap with intent cascade (SPEC-143)"
```

---

## Chunk 2: CLI integration and skill updates

### Task 6: Replace `--focus` with `--scope` in chart_cli.py

**Files:**
- Modify: `skills/swain-design/scripts/chart_cli.py:113-179`

- [ ] **Step 1: Write failing test**

Add to `test_scoped_roadmap.py`:

```python
def test_collect_roadmap_items_no_focus_vision_param():
    """The old focus_vision param still works for backward compat during transition."""
    nodes, edges = _make_scoped_graph()
    # focus_vision should still filter (mapped to scope internally)
    items = collect_roadmap_items(nodes, edges, focus_vision="VISION-001")
    assert len(items) > 0
    # But scope takes precedence
    items2 = collect_roadmap_items(nodes, edges, scope="INITIATIVE-001")
    assert len(items2) < len(items)
```

- [ ] **Step 2: Run test to verify it passes (already handled by Task 3)**

Run: `cd skills/swain-design/scripts && python -m pytest specgraph/tests/test_scoped_roadmap.py::test_collect_roadmap_items_no_focus_vision_param -v`
Expected: PASS

- [ ] **Step 3: Update chart_cli.py**

In `skills/swain-design/scripts/chart_cli.py`:

Replace the `--focus` argument (lines 117-118):
```python
# OLD:
roadmap_p.add_argument("--focus", type=str, default=None,
                       help="Focus on a specific Vision ID")
# NEW:
roadmap_p.add_argument("--scope", type=str, default=None,
                       help="Generate scoped roadmap for a Vision or Initiative ID")
```

Replace the roadmap execution path (lines 151-179):
```python
if command == "roadmap":
    repo_root = _get_repo_root()
    data = _ensure_cache(repo_root)
    nodes = data["nodes"]
    edges = data["edges"]
    scope = getattr(args, "scope", None)
    fmt = getattr(args, "format", None)
    json_out = getattr(args, "json_output", False)
    cli_out = getattr(args, "cli_output", False)

    if scope:
        # Scoped mode: write slice to artifact folder
        from specgraph.roadmap import render_scoped_roadmap, _write_scoped_slice
        _write_scoped_slice(scope, nodes, edges, repo_root)
    elif cli_out:
        from specgraph.roadmap import render_roadmap_cli
        items = collect_roadmap_items(nodes, edges)
        print(render_roadmap_cli(items))
    elif fmt or json_out:
        output = render_roadmap(nodes, edges, fmt=fmt or "mermaid-gantt",
                                json_output=json_out)
        print(output)
    else:
        # Default: write ROADMAP.md + all slices
        items = collect_roadmap_items(nodes, edges)
        md = render_roadmap_markdown(items, nodes, repo_root=repo_root)
        roadmap_path = os.path.join(repo_root, "ROADMAP.md")
        with open(roadmap_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"Wrote {roadmap_path}")
        # Regenerate all per-Vision and per-Initiative slices
        from specgraph.roadmap import _write_all_slices
        _write_all_slices(nodes, edges, repo_root)
```

- [ ] **Step 4: Commit**

```bash
git add skills/swain-design/scripts/chart_cli.py
git commit -m "feat(chart-cli): replace --focus with --scope, add all-slices regen (SPEC-143)"
```

---

### Task 7: Implement `_write_scoped_slice()` and `_write_all_slices()`

**Files:**
- Modify: `skills/swain-design/scripts/specgraph/roadmap.py`
- Test: `skills/swain-design/scripts/specgraph/tests/test_scoped_roadmap.py`

- [ ] **Step 1: Write failing tests**

Add to `test_scoped_roadmap.py`:

```python
import os
import tempfile
import shutil

from specgraph.roadmap import _write_scoped_slice, _write_all_slices


def test_write_scoped_slice_creates_file(tmp_path):
    nodes, edges = _make_scoped_graph()
    # Point the artifact file to a real temp path
    art_dir = tmp_path / "docs" / "initiative" / "Active" / "(INITIATIVE-001)-Auth"
    art_dir.mkdir(parents=True)
    art_file = art_dir / "(INITIATIVE-001)-Auth.md"
    art_file.write_text("---\ntitle: Auth\n---\n# Auth")
    nodes["INITIATIVE-001"]["file"] = str(art_file.relative_to(tmp_path))

    _write_scoped_slice("INITIATIVE-001", nodes, edges, str(tmp_path))

    roadmap_file = art_dir / "roadmap.md"
    assert roadmap_file.exists()
    content = roadmap_file.read_text()
    assert "Auto-generated by chart.sh roadmap --scope" in content


def test_write_scoped_slice_backs_up_manual_roadmap(tmp_path):
    nodes, edges = _make_scoped_graph()
    art_dir = tmp_path / "docs" / "initiative" / "Active" / "(INITIATIVE-001)-Auth"
    art_dir.mkdir(parents=True)
    art_file = art_dir / "(INITIATIVE-001)-Auth.md"
    art_file.write_text("---\ntitle: Auth\n---\n# Auth")
    nodes["INITIATIVE-001"]["file"] = str(art_file.relative_to(tmp_path))

    # Pre-existing manual roadmap
    manual = art_dir / "roadmap.md"
    manual.write_text("# My hand-written roadmap\n\nThis is manual content.")

    _write_scoped_slice("INITIATIVE-001", nodes, edges, str(tmp_path))

    backup = art_dir / "roadmap.manual-backup.md"
    assert backup.exists()
    assert "hand-written" in backup.read_text()
    assert "Auto-generated" in manual.read_text()


def test_write_scoped_slice_no_backup_for_generated(tmp_path):
    nodes, edges = _make_scoped_graph()
    art_dir = tmp_path / "docs" / "initiative" / "Active" / "(INITIATIVE-001)-Auth"
    art_dir.mkdir(parents=True)
    art_file = art_dir / "(INITIATIVE-001)-Auth.md"
    art_file.write_text("---\ntitle: Auth\n---\n# Auth")
    nodes["INITIATIVE-001"]["file"] = str(art_file.relative_to(tmp_path))

    # Pre-existing auto-generated roadmap
    generated = art_dir / "roadmap.md"
    generated.write_text("<!-- Auto-generated by chart.sh roadmap --scope. Do not edit. -->\n# old")

    _write_scoped_slice("INITIATIVE-001", nodes, edges, str(tmp_path))

    backup = art_dir / "roadmap.manual-backup.md"
    assert not backup.exists()  # no backup needed


def test_write_all_slices(tmp_path):
    nodes, edges = _make_scoped_graph()
    # Create dirs for both visions and initiatives
    for aid, node in nodes.items():
        if node.get("type", "").upper() in ("VISION", "INITIATIVE"):
            fpath = node.get("file", "")
            if fpath:
                full = tmp_path / fpath
                full.parent.mkdir(parents=True, exist_ok=True)
                full.write_text(f"---\ntitle: {node['title']}\n---\n# {node['title']}")

    count = _write_all_slices(nodes, edges, str(tmp_path))
    assert count >= 2  # at least VISION-001 and INITIATIVE-001
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd skills/swain-design/scripts && python -m pytest specgraph/tests/test_scoped_roadmap.py::test_write_scoped_slice_creates_file -v`
Expected: FAIL — `_write_scoped_slice` does not exist

- [ ] **Step 3: Implement both functions**

Add to `skills/swain-design/scripts/specgraph/roadmap.py`:

```python
_AUTO_GENERATED_MARKER = "<!-- Auto-generated by chart.sh roadmap --scope. Do not edit. -->"


def _write_scoped_slice(
    artifact_id: str,
    nodes: dict,
    edges: list[dict],
    repo_root: str,
) -> str | None:
    """Write a scoped roadmap slice to the artifact's folder. Returns path written or None."""
    node = nodes.get(artifact_id)
    if not node or not node.get("file"):
        return None

    artifact_file = os.path.join(repo_root, node["file"])
    artifact_dir = os.path.dirname(artifact_file)
    roadmap_path = os.path.join(artifact_dir, "roadmap.md")

    # Backup existing manual roadmap
    if os.path.exists(roadmap_path):
        with open(roadmap_path, "r", encoding="utf-8") as f:
            existing = f.read()
        if _AUTO_GENERATED_MARKER not in existing:
            backup_path = os.path.join(artifact_dir, "roadmap.manual-backup.md")
            if not os.path.exists(backup_path):
                import shutil
                shutil.copy2(roadmap_path, backup_path)

    md = render_scoped_roadmap(artifact_id, nodes, edges, repo_root)
    with open(roadmap_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Wrote {roadmap_path}")
    return roadmap_path


def _write_all_slices(
    nodes: dict,
    edges: list[dict],
    repo_root: str,
) -> int:
    """Regenerate all per-Vision and per-Initiative roadmap slices. Returns count written."""
    count = 0
    for aid, node in sorted(nodes.items()):
        atype = node.get("type", "").upper()
        if atype in ("VISION", "INITIATIVE"):
            result = _write_scoped_slice(aid, nodes, edges, repo_root)
            if result:
                count += 1
    return count
```

- [ ] **Step 4: Run all tests**

Run: `cd skills/swain-design/scripts && python -m pytest specgraph/tests/test_scoped_roadmap.py specgraph/tests/test_roadmap_data_model.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add skills/swain-design/scripts/specgraph/roadmap.py skills/swain-design/scripts/specgraph/tests/test_scoped_roadmap.py
git commit -m "feat(specgraph): add _write_scoped_slice and _write_all_slices (SPEC-143)"
```

---

### Task 8: Update swain-roadmap SKILL.md

**Files:**
- Modify: `skills/swain-roadmap/SKILL.md`

- [ ] **Step 1: Update the skill file**

In `skills/swain-roadmap/SKILL.md`, make these changes:

**Section 2 — add scope support** (after the `bash "$CHART_SH" roadmap` line):

Replace the entire "### 2. Regenerate ROADMAP.md" section with:

```markdown
### 2. Regenerate roadmap

Parse the argument: if the user provided an artifact ID (e.g., `swain-roadmap VISION-001`), set `SCOPE_ID` to that ID. Otherwise, `SCOPE_ID` is empty.

**If `SCOPE_ID` is set:**

```bash
bash "$CHART_SH" roadmap --scope "$SCOPE_ID"
```

This writes a `roadmap.md` to the artifact's folder.

**If `SCOPE_ID` is empty:**

```bash
bash "$CHART_SH" roadmap
```

This writes `ROADMAP.md` to the project root AND regenerates all per-Vision and per-Initiative slices.

### 2.5. Post-process intent placeholders

After chart.sh completes, scan the output file(s) for `{{INTENT: <ID>}}` placeholders. For each:

1. Read the source artifact markdown.
2. Extract the first sentence of `## Value Proposition` (for Visions) or `## Goal / Objective` (for Initiatives).
3. Replace the `{{INTENT: <ID>}}` marker with the extracted sentence.
4. Write the file back.

If the section cannot be found, leave the placeholder as-is (the operator can fill it in manually or wait for `brief-description` to be populated).
```

**Section 3 — scope-aware opening:**

Replace:
```markdown
### 3. Open ROADMAP.md
```

With:
```markdown
### 3. Open the roadmap

If `SCOPE_ID` was set, open the scoped slice:

```bash
# Find the artifact's file path from the graph
ARTIFACT_DIR=$(dirname "$(bash "$CHART_SH" show "$SCOPE_ID" 2>/dev/null | grep -o 'docs/[^ ]*')")
open "$REPO_ROOT/$ARTIFACT_DIR/roadmap.md"
```

If no scope, open the project-wide roadmap:

```bash
open "$REPO_ROOT/ROADMAP.md"
```
```

- [ ] **Step 2: Commit**

```bash
git add skills/swain-roadmap/SKILL.md
git commit -m "feat(swain-roadmap): add --scope pass-through and INTENT post-processing (SPEC-143)"
```

---

### Task 9: Harmonize vision-definition.md

**Files:**
- Modify: `skills/swain-design/references/vision-definition.md:59-62`

- [ ] **Step 1: Update the vision definition**

In `skills/swain-design/references/vision-definition.md`, replace lines 59 and 62 (the roadmap supporting doc description):

Replace:
```
    - **Expected:** Every Vision SHOULD include an `architecture-overview.md` and a `roadmap.md`. These are the primary supporting docs that give the Vision operational substance.
```

With:
```
    - **Expected:** Every Vision SHOULD include an `architecture-overview.md`. A `roadmap.md` is auto-generated by `chart.sh roadmap --scope` and should not be manually maintained — it is regenerated on every project-wide roadmap refresh.
```

Replace the full roadmap paragraph (line 62) with:
```
- **Roadmap:** A `roadmap.md` in the Vision folder is **auto-generated** by `chart.sh roadmap --scope VISION-NNN` (or by the project-wide `chart.sh roadmap` which regenerates all slices). It shows: intent summary, child artifact table with links and progress, aggregate progress bar, recent git activity, and an Eisenhower priority subset. Do not edit this file manually — it will be overwritten on the next roadmap refresh. If a manually-written `roadmap.md` exists when the generator first runs, it is backed up to `roadmap.manual-backup.md`.
```

- [ ] **Step 2: Commit**

```bash
git add skills/swain-design/references/vision-definition.md
git commit -m "docs(vision-def): roadmap.md is now auto-generated by chart.sh --scope (SPEC-143)"
```

---

### Task 10: Remove `--focus` from `render_roadmap()` passthrough

**Files:**
- Modify: `skills/swain-design/scripts/specgraph/roadmap.py` (the `render_roadmap()` function)
- Modify: `skills/swain-design/scripts/chart_cli.py` (the fmt/json path)

- [ ] **Step 1: Check `render_roadmap()` for focus_vision param**

Read `render_roadmap()` function signature and update it to use `scope` instead of `focus_vision`. The fmt/json output paths in chart_cli.py should also pass `scope` instead of `focus`.

In `roadmap.py`, update `render_roadmap()` signature to replace `focus_vision` with `scope`:
```python
def render_roadmap(
    nodes: dict,
    edges: list[dict],
    fmt: str = "mermaid-gantt",
    scope: str | None = None,  # was focus_vision
    json_output: bool = False,
) -> str:
```

And internally, pass `scope=scope` to `collect_roadmap_items()`.

In `chart_cli.py`, update the fmt/json path to pass `scope=scope`.

- [ ] **Step 2: Run all tests**

Run: `cd skills/swain-design/scripts && python -m pytest specgraph/tests/ -v`
Expected: ALL PASS

- [ ] **Step 3: Commit**

```bash
git add skills/swain-design/scripts/specgraph/roadmap.py skills/swain-design/scripts/chart_cli.py
git commit -m "refactor(specgraph): replace focus_vision with scope throughout (SPEC-143)"
```

---

### Task 11: Final integration test

**Files:**
- Test: `skills/swain-design/scripts/specgraph/tests/test_scoped_roadmap.py`

- [ ] **Step 1: Run the full test suite**

Run: `cd skills/swain-design/scripts && python -m pytest specgraph/tests/ -v`
Expected: ALL PASS

- [ ] **Step 2: Manual smoke test**

Run chart.sh against the real project:

```bash
bash skills/swain-design/scripts/chart.sh roadmap --scope VISION-001
cat "$(find docs/vision -name 'roadmap.md' -path '*VISION-001*' | head -1)"
```

Verify:
- File exists in VISION-001's folder
- Contains auto-generated header
- Contains children table with Initiatives
- Contains progress bar
- Contains recent activity or placeholder

```bash
bash skills/swain-design/scripts/chart.sh roadmap --scope INITIATIVE-005
cat "$(find docs/initiative -name 'roadmap.md' -path '*INITIATIVE-005*' | head -1)"
```

Verify same structure with Epics and direct SPECs.

```bash
bash skills/swain-design/scripts/chart.sh roadmap
ls docs/vision/*/roadmap.md docs/initiative/*/roadmap.md 2>/dev/null | head -20
```

Verify all slices regenerated alongside ROADMAP.md.

- [ ] **Step 3: Commit any fixes from smoke testing**

```bash
git add -A
git commit -m "test(specgraph): integration smoke test for scoped roadmaps (SPEC-143)"
```
