# Stale Worktree Detection

Enumerate all linked worktrees and classify their health. **Skip if the repo has no linked worktrees** (i.e., `git worktree list --porcelain` returns only the main worktree entry) — this check produces no output in a clean repo.

## Detection

```bash
git worktree list --porcelain
```

Parse each linked worktree (exclude the main worktree — the first entry in the output):

```bash
git worktree list --porcelain | awk '
  /^worktree / { path=$2 }
  /^branch /   { branch=$2 }
  /^$/         { if (path != "") print path, branch; path=""; branch="" }
' | tail -n +2
```

For each linked worktree:

1. **Orphaned** — directory does not exist on disk (`[ ! -d "$path" ]`):
   - WARN: "Orphaned worktree: `<path>` (directory missing). Clean up with: `git worktree prune`"

2. **Stale (merged)** — directory exists and branch is fully merged into `trunk`:
   ```bash
   git merge-base --is-ancestor "$branch" origin/trunk
   ```
   - WARN: "Stale worktree: `<path>` (branch `<branch>` already merged into trunk). Safe to remove:
     `git worktree remove <path> && git branch -d <branch>`"

3. **Active (unmerged)** — directory exists and branch has commits not in `trunk`:
   - INFO: "Active worktree: `<path>` (branch `<branch>`, N commits ahead of trunk). Do not remove — work in progress."

Do not remove any worktree automatically. All output is advisory.

## Status values

- **ok** — no linked worktrees, or all are active
- **warning** — one or more stale or orphaned worktrees found (provide cleanup commands per item)
