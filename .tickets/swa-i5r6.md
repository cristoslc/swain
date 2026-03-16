---
id: swa-i5r6
status: closed
deps: [swa-2hqc]
links: []
created: 2026-03-16T03:44:32Z
type: task
priority: 1
assignee: cristos
parent: swa-1zpe
tags: [spec:SPEC-052]
---
# Task 4: `chart.sh` shell wrapper and CLI entry point

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


## Notes

**2026-03-16T03:52:23Z**

Complete: chart.sh + chart_cli.py working, all lenses functional
