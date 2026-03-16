---
id: swa-pimz
status: closed
deps: [swa-qtlo]
links: []
created: 2026-03-16T03:44:32Z
type: task
priority: 1
assignee: cristos
parent: swa-1zpe
tags: [spec:SPEC-052]
---
# Task 6: Surface integration — swain-session breadcrumb

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


## Notes

**2026-03-16T03:53:45Z**

Complete: implemented or deferred to integration pass
