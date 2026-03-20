---
id: swa-vrtp
status: open
deps: [swa-i7ij]
links: []
created: 2026-03-20T00:42:36Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-kd71
tags: [spec:SPEC-091]
---
# Task 7: Update `extract_list_ids` to handle dict entries

**Files:**
- Modify: `.claude/skills/swain-design/scripts/specgraph/parser.py:158-168`

- [ ] **Step 1: Update extract_list_ids**

Replace lines 158-168:

```python
def extract_list_ids(fields: dict, key: str) -> list[str]:
    """Extract artifact IDs (TYPE-NNN) from a frontmatter list field.

    Handles both plain string entries and enriched dict entries
    (where the artifact ID is in the 'artifact' key).
    """
    val = fields.get(key, [])
    if isinstance(val, str):
        return _ARTIFACT_ID_RE.findall(val)
    if isinstance(val, list):
        ids = []
        for item in val:
            if isinstance(item, dict):
                artifact_val = item.get("artifact", "")
                ids.extend(_ARTIFACT_ID_RE.findall(str(artifact_val)))
            else:
                ids.extend(_ARTIFACT_ID_RE.findall(str(item)))
        return ids
    return []
```

- [ ] **Step 2: Run all tests**

```bash
cd .claude/skills/swain-design/scripts/specgraph
uv run python3 -m pytest tests/test_parser_enriched.py -v
```

Expected: All tests PASS (including `test_enriched_entry_extract_list_ids`).

- [ ] **Step 3: Run chart.sh build to verify no regression**

```bash
bash .claude/skills/swain-design/scripts/chart.sh build
```

Expected: Graph builds successfully with same node/edge counts as before (no TRAIN artifacts exist yet, so no change).

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/swain-design/scripts/specgraph/parser.py
git commit -m "feat: extract_list_ids handles enriched dict entries"
```

---

## Chunk 3: train-check.sh

