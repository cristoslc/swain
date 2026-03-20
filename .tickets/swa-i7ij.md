---
id: swa-i7ij
status: open
deps: [swa-9dqz]
links: []
created: 2026-03-20T00:42:36Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-kd71
tags: [spec:SPEC-091]
---
# Task 6: Update `parse_frontmatter` to handle enriched entries

**Files:**
- Modify: `.claude/skills/swain-design/scripts/specgraph/parser.py:68-111`

- [ ] **Step 1: Modify parse_frontmatter**

Add tracking for enriched (dict) list items. The key change: when a list item matches `key: value` pattern (like `artifact: SPEC-067`), start accumulating a dict. Subsequent indented `key: value` lines (like `rel: [documents]`) are added to that dict.

In `parse_frontmatter`, replace the loop body (lines 82-109) with:

```python
    current_list_key: Optional[str] = None
    current_item_dict: Optional[dict] = None

    for line in fm_text.splitlines():
        # Check for list item continuation
        list_match = re.match(r"^\s+-\s+(.+)$", line)
        if list_match and current_list_key is not None:
            val = list_match.group(1).strip()
            # Strip quotes
            val = re.sub(r'^["\']|["\']$', "", val)

            # Check if this list item is a YAML mapping (e.g., "artifact: SPEC-067")
            item_kv = re.match(r"^([a-z][a-z0-9-]*):\s+(.+)$", val)
            if item_kv:
                current_item_dict = {
                    item_kv.group(1): _parse_inline_value(item_kv.group(2).strip())
                }
                fields[current_list_key].append(current_item_dict)
            else:
                current_item_dict = None
                fields[current_list_key].append(val)
            continue

        # Check for enriched item continuation (indented key: value after a mapping list item)
        if current_item_dict is not None and current_list_key is not None:
            indent_kv = re.match(r"^\s+([a-z][a-z0-9-]*):\s+(.+)$", line)
            if indent_kv:
                key = indent_kv.group(1)
                val = _parse_inline_value(indent_kv.group(2).strip())
                current_item_dict[key] = val
                continue
            else:
                current_item_dict = None

        # Check for scalar field
        scalar_match = re.match(r"^([a-z][a-z0-9-]*):\s*(.*)$", line)
        if scalar_match:
            current_item_dict = None
            key = scalar_match.group(1)
            val = scalar_match.group(2).strip()
            # Strip quotes
            val = re.sub(r'^["\']|["\']$', "", val)

            if not val or val in ("[]", "~", "null"):
                fields[key] = [] if not val or val == "[]" else val
                current_list_key = key if not val or val == "[]" else None
            else:
                fields[key] = val
                current_list_key = None
        else:
            current_item_dict = None
            current_list_key = None
```

- [ ] **Step 2: Add `_parse_inline_value` helper**

Add before `parse_frontmatter` (around line 65):

```python
def _parse_inline_value(val: str) -> Any:
    """Parse an inline YAML value: [list], quoted string, or plain string."""
    val = re.sub(r'^["\']|["\']$', "", val)
    if val.startswith("[") and val.endswith("]"):
        return [v.strip() for v in val[1:-1].split(",") if v.strip()]
    return val
```

- [ ] **Step 3: Run tests to verify enriched parsing works**

```bash
cd .claude/skills/swain-design/scripts/specgraph
uv run python3 -m pytest tests/test_parser_enriched.py -v
```

Expected: All tests PASS.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/swain-design/scripts/specgraph/parser.py
git commit -m "feat: support enriched linked-artifacts entries in frontmatter parser"
```

