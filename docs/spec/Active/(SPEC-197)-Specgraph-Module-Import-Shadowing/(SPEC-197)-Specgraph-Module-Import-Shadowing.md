---
title: "Specgraph Module Import Shadowing"
artifact: SPEC-197
track: implementable
status: Active
author: cristos
created: 2026-03-30
last-updated: 2026-03-30
priority-weight: high
type: bug
parent-epic: ""
parent-initiative: INITIATIVE-003
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# SPEC-197: Specgraph Module Import Shadowing

## Problem Statement

Running any `chart.sh` subcommand (e.g., `bash .agents/bin/chart.sh build`) fails with a `ModuleNotFoundError` because a standalone script file shadows the `specgraph` Python package.

The root cause is a naming collision in `.agents/bin/`:

- `.agents/bin/specgraph.py` -- a symlink to `skills/swain-design/scripts/specgraph.py` (a standalone entry-point script)
- `skills/swain-design/scripts/specgraph/` -- the actual `specgraph` Python package directory (containing `__init__.py`, `graph.py`, `cli.py`, `lenses.py`, etc.)

When `chart_cli.py` (line 14-15) inserts `.agents/bin/` into `sys.path` and then attempts `from specgraph.graph import ...` (line 17), Python resolves `specgraph` to the `.agents/bin/specgraph.py` file rather than the `specgraph/` package directory. Since `specgraph.py` is a plain module (not a package), the import fails:

```
ModuleNotFoundError: No module named 'specgraph.cli'; 'specgraph' is not a package
```

The same shadowing issue exists in the canonical source location (`skills/swain-design/scripts/`), where `specgraph.py` and `specgraph/` coexist. However, `specgraph.py` itself works around this by resolving its own parent directory and inserting it into `sys.path` -- but this only works when `specgraph.py` is the entry point, not when another script (like `chart_cli.py`) adds the same directory to `sys.path` and imports the package.

## Reproduction Steps

1. From the repository root, run:
   ```bash
   bash .agents/bin/chart.sh build
   ```
2. Observe the traceback ending in:
   ```
   ModuleNotFoundError: No module named 'specgraph.cli'; 'specgraph' is not a package
   ```

Any `chart.sh` subcommand triggers the same failure (e.g., `chart.sh tree`, `chart.sh roadmap`).

## Expected Behavior

`chart.sh build` (and all other subcommands) should execute successfully, importing the `specgraph` package and its submodules without error.

## Actual Behavior

All `chart.sh` subcommands fail immediately with a `ModuleNotFoundError` at import time. The specgraph CLI and chart system are completely unusable.

## Severity

**High** -- This blocks all specgraph and chart operations, which are used for artifact graph analysis, roadmap generation, and session intelligence features.

## Acceptance Criteria

- [ ] `bash .agents/bin/chart.sh build` completes without import errors
- [ ] `bash .agents/bin/chart.sh tree` completes without import errors
- [ ] `bash .agents/bin/specgraph.sh` continues to work as before
- [ ] The `specgraph.py` standalone script no longer shadows the `specgraph/` package when other scripts in the same directory import the package
- [ ] No regressions in any existing specgraph or chart functionality
