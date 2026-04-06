# SPEC-248: Extend Projection Schema with Relationship Fields

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `build_projection()` to include `linked_artifacts` and `depends_on_artifacts` fields extracted from graph edges.

**Architecture:** Add relationship extraction logic to `build_projection()` that queries edges for `linked-artifacts`, `artifact-refs`, and `depends-on` types. Pure addition to projection output, no breaking changes.

**Tech Stack:** Python 3.11, pytest, existing specgraph infrastructure

---

## File Structure

- Modify: `skills/swain-design/scripts/specgraph/graph.py:240-261` (build_projection function)
- Test: `skills/swain-design/scripts/tests/test_graph.py` (add relationship field tests)

---

## Task 1: Write failing tests for relationship fields

**Files:**
- Modify: `skills/swain-design/scripts/tests/test_graph.py`

- [ ] **Step 1: Write test for linked_artifacts field**

```python
def test_build_projection_includes_linked_artifacts():
    """Projection records include linked_artifacts from linked-artifacts edges."""
    nodes = {
        "EPIC-001": {"type": "EPIC", "status": "Active", "file": "docs/epic/Active/EPIC-001.md"},
        "DESIGN-001": {"type": "DESIGN", "status": "Active", "file": "docs/design/Active/DESIGN-001.md"},
    }
    edges = [
        {"from": "EPIC-001", "to": "DESIGN-001", "type": "linked-artifacts"},
    ]
    
    projection = build_projection(nodes, edges)
    epic_record = next(r for r in projection if r["artifact"] == "EPIC-001")
    
    assert epic_record["linked_artifacts"] == ["DESIGN-001"]
```

- [ ] **Step 2: Write test for artifact-refs in linked_artifacts**

```python
def test_build_projection_merges_artifact_refs_into_linked():
    """artifact-refs edges are merged into linked_artifacts field."""
    nodes = {
        "EPIC-002": {"type": "EPIC", "status": "Active", "file": "docs/epic/Active/EPIC-002.md"},
        "DESIGN-002": {"type": "DESIGN", "status": "Active", "file": "docs/design/Active/DESIGN-002.md"},
    }
    edges = [
        {"from": "EPIC-002", "to": "DESIGN-002", "type": "artifact-refs"},
    ]
    
    projection = build_projection(nodes, edges)
    epic_record = next(r for r in projection if r["artifact"] == "EPIC-002")
    
    assert epic_record["linked_artifacts"] == ["DESIGN-002"]
```

- [ ] **Step 3: Write test for depends_on_artifacts field**

```python
def test_build_projection_includes_depends_on_artifacts():
    """Projection records include depends_on_artifacts field."""
    nodes = {
        "SPEC-001": {"type": "SPEC", "status": "Proposed", "file": "docs/spec/Proposed/SPEC-001.md"},
        "SPEC-002": {"type": "SPEC", "status": "Complete", "file": "docs/spec/Complete/SPEC-002.md"},
    }
    edges = [
        {"from": "SPEC-001", "to": "SPEC-002", "type": "depends-on"},
    ]
    
    projection = build_projection(nodes, edges)
    spec_record = next(r for r in projection if r["artifact"] == "SPEC-001")
    
    assert spec_record["depends_on_artifacts"] == ["SPEC-002"]
```

- [ ] **Step 4: Write test for empty relationships**

```python
def test_build_projection_empty_relationships():
    """Artifacts with no relationships have empty lists."""
    nodes = {
        "SPEC-003": {"type": "SPEC", "status": "Proposed", "file": "docs/spec/Proposed/SPEC-003.md"},
    }
    edges = []
    
    projection = build_projection(nodes, edges)
    spec_record = next(r for r in projection if r["artifact"] == "SPEC-003")
    
    assert spec_record["linked_artifacts"] == []
    assert spec_record["depends_on_artifacts"] == []
```

- [ ] **Step 5: Write test for broken references excluded**

```python
def test_build_projection_excludes_broken_references():
    """Edges to non-existent artifacts are excluded."""
    nodes = {
        "SPEC-004": {"type": "SPEC", "status": "Proposed", "file": "docs/spec/Proposed/SPEC-004.md"},
    }
    edges = [
        {"from": "SPEC-004", "to": "MISSING-001", "type": "linked-artifacts"},
        {"from": "SPEC-004", "to": "MISSING-002", "type": "depends-on"},
    ]
    
    projection = build_projection(nodes, edges)
    spec_record = next(r for r in projection if r["artifact"] == "SPEC-004")
    
    assert spec_record["linked_artifacts"] == []
    assert spec_record["depends_on_artifacts"] == []
```

- [ ] **Step 6: Run tests to confirm they fail**

```bash
cd /Users/cristos/Documents/code/swain
python -m pytest skills/swain-design/scripts/tests/test_graph.py::test_build_projection_includes_linked_artifacts -v
python -m pytest skills/swain-design/scripts/tests/test_graph.py::test_build_projection_merges_artifact_refs_into_linked -v
python -m pytest skills/swain-design/scripts/tests/test_graph.py::test_build_projection_includes_depends_on_artifacts -v
python -m pytest skills/swain-design/scripts/tests/test_graph.py::test_build_projection_empty_relationships -v
python -m pytest skills/swain-design/scripts/tests/test_graph.py::test_build_projection_excludes_broken_references -v
```

---

## Task 2: Implement relationship field extraction

**Files:**
- Modify: `skills/swain-design/scripts/specgraph/graph.py:240-261`

- [ ] **Step 1: Add linked_artifacts extraction**

Inside the loop in `build_projection()`, after determining `placement_state`, add:

```python
# Extract relationship IDs from edges
linked = {
    e["to"] for e in edges
    if e["from"] == artifact_id
    and e["type"] in ("linked-artifacts", "artifact-refs")
    and e["to"] in nodes
}
```

- [ ] **Step 2: Add depends_on_artifacts extraction**

```python
depends = {
    e["to"] for e in edges
    if e["from"] == artifact_id
    and e["type"] == "depends-on"
    and e["to"] in nodes
}
```

- [ ] **Step 3: Add fields to projection record**

Update the `projection.append()` call to include:

```python
projection.append({
    "artifact": artifact_id,
    "type": node.get("type", ""),
    "status": node.get("status", ""),
    "canonical_file": node.get("file", ""),
    "canonical_path": _canonical_path(artifact_id, node.get("file", "")),
    "direct_parent": direct_parent,
    "placement_state": placement_state,
    # NEW fields:
    "linked_artifacts": sorted(linked),
    "depends_on_artifacts": sorted(depends),
})
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
python -m pytest skills/swain-design/scripts/tests/test_graph.py::test_build_projection_includes_linked_artifacts -v
python -m pytest skills/swain-design/scripts/tests/test_graph.py::test_build_projection_merges_artifact_refs_into_linked -v
python -m pytest skills/swain-design/scripts/tests/test_graph.py::test_build_projection_includes_depends_on_artifacts -v
python -m pytest skills/swain-design/scripts/tests/test_graph.py::test_build_projection_empty_relationships -v
python -m pytest skills/swain-design/scripts/tests/test_graph.py::test_build_projection_excludes_broken_references -v
```

- [ ] **Step 5: Run all graph tests to ensure backward compatibility**

```bash
python -m pytest skills/swain-design/scripts/tests/test_graph.py -v
```

---

## Task 3: Verify integration

- [ ] **Step 1: Run chart build to verify projection output**

```bash
cd /Users/cristos/Documents/code/swain
bash skills/swain-design/scripts/chart.sh build
```

- [ ] **Step 2: Check projection includes new fields**

```bash
python -c "
import json
from pathlib import Path
cache = Path('/tmp/agents-specgraph-043bb4889eec.json')
data = json.loads(cache.read_text())
# Find a record with linked_artifacts
for item in data.get('projection', []):
    if item.get('linked_artifacts'):
        print(f\"{item['artifact']}: linked_artifacts={item['linked_artifacts']}\")
        break
"
```

- [ ] **Step 3: Run full specgraph test suite**

```bash
python -m pytest skills/swain-design/scripts/specgraph/tests/ -v
```

---

## Task 4: Commit SPEC-248

- [ ] **Step 1: Stage changes**

```bash
git add skills/swain-design/scripts/specgraph/graph.py
git add skills/swain-design/scripts/tests/test_graph.py
```

- [ ] **Step 2: Commit with SPEC reference**

```bash
git commit -m "feat(chart): extend projection with relationship fields (SPEC-248)

Add linked_artifacts and depends_on_artifacts to projection records.
Extracts from linked-artifacts, artifact-refs, and depends-on edges.
Excludes broken references, sorts output for determinism.

💘 Generated with Crush

Assisted-by: GLM 5 (Reasoning & Agentic) via Crush <crush@charm.land>"
```