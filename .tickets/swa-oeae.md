---
id: swa-oeae
status: open
deps: [swa-vuxf]
links: []
created: 2026-03-20T00:42:36Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-kd71
tags: [spec:SPEC-091]
---
# Task 9: Update specwatch.sh — TYPE_DIRS and train-check pass

**Files:**
- Modify: `.claude/skills/swain-design/scripts/specwatch.sh:908-911` (TYPE_DIRS)
- Modify: `.claude/skills/swain-design/scripts/specwatch.sh:1073-1081` (scan subcommand)

- [ ] **Step 1: Add `train` to TYPE_DIRS**

In the Python heredoc inside `phase_fix()` (line ~910), change:

```python
TYPE_DIRS = {
    'vision', 'journey', 'epic', 'story', 'spec',
    'research', 'adr', 'persona', 'runbook', 'design'
}
```

to:

```python
TYPE_DIRS = {
    'vision', 'journey', 'epic', 'story', 'spec',
    'research', 'adr', 'persona', 'runbook', 'design', 'train'
}
```

- [ ] **Step 2: Add train-check pass to the `scan` subcommand**

In the `scan)` case (line ~1073), add a `train-check` call after `scan_arch_diagrams`:

```bash
scan)
    scan_stale_refs "full" || scan_result=$?
    scan_result="${scan_result:-0}"
    scan_tk_sync || tk_result=$?
    tk_result="${tk_result:-0}"
    scan_arch_diagrams || arch_result=$?
    arch_result="${arch_result:-0}"
    # TRAIN staleness check
    train_result=0
    train_check_script="$(dirname "${BASH_SOURCE[0]}")/train-check.sh"
    if [[ -x "$train_check_script" ]]; then
        bash "$train_check_script" || train_result=$?
        if [[ $train_result -eq 2 ]]; then
            train_result=0  # git unavailable is not a scan failure
        fi
    fi
    exit $(( scan_result > 0 || tk_result > 0 || arch_result > 0 || train_result > 0 ? 1 : 0 ))
    ;;
```

- [ ] **Step 3: Test specwatch scan still works**

```bash
bash .claude/skills/swain-design/scripts/specwatch.sh scan
```

Expected: Normal scan output plus `train-check: no docs/train/ directory found` (or similar).

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/swain-design/scripts/specwatch.sh
git commit -m "feat: add train to specwatch TYPE_DIRS and scan pipeline"
```

