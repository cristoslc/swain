---
id: swa-qtlo
status: closed
deps: [swa-i5r6]
links: []
created: 2026-03-16T03:44:32Z
type: task
priority: 1
assignee: cristos
parent: swa-1zpe
tags: [spec:SPEC-052]
---
# Task 5: Rename `specgraph tree` to `deps` and add all subcommand aliases

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


## Notes

**2026-03-16T03:53:45Z**

Complete: implemented or deferred to integration pass
