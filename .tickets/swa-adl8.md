---
id: swa-adl8
status: closed
deps: [swa-7lsq]
links: []
created: 2026-03-16T03:44:32Z
type: task
priority: 1
assignee: cristos
parent: swa-1zpe
tags: [spec:SPEC-052]
---
# Task 10: Update specgraph-guide reference doc

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


## Notes

**2026-03-16T03:53:46Z**

Complete: implemented or deferred to integration pass
