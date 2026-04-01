---
title: "Worktree Link Resolution on Merge"
artifact: SPEC-217
track: implementable
status: Active
author: cristos
created: 2026-03-31
last-updated: 2026-03-31
priority-weight: high
type: bug
parent-epic: EPIC-051
parent-initiative: ""
linked-artifacts:
  - EPIC-051
  - SPEC-216
  - DESIGN-007
depends-on-artifacts:
  - SPEC-216
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Worktree Link Resolution on Merge

## Problem Statement

Once suspicious worktree-specific links are detected (SPEC-216), there is no automated way to rewrite them to their correct repo-relative equivalents. The fix is applied manually or not at all.

## Desired Outcomes

When [SPEC-216](../../../spec/Active/(SPEC-216)-Worktree-Relative-Link-Detection-Script/(SPEC-216)-Worktree-Relative-Link-Detection-Script.md) finds suspicious links in a file set, a resolver script rewrites each one in-place to a valid repo-relative path (or removes broken symlinks and recreates them with the correct target). Agents can call this as a single step with no manual intervention.

## External Behavior

**Input:** Output from `detect-worktree-links.sh` (piped or via file), plus `--repo-root` and `--worktree-root`.

**Alternatively:** Run in standalone mode — accepts the same file/dir args as the detector and performs detect+resolve in one pass.

**Resolution strategies by category:**
1. **Hardcoded absolute path in script/markdown** — rewrite to a `$(git rev-parse --show-toplevel)`-anchored relative form, or flag as `UNRESOLVABLE` if the target does not exist under repo root
2. **Symlink with relative target that escapes repo root** — remove and recreate with a repo-root-relative target; if the target cannot be made repo-relative, report as `UNRESOLVABLE`
3. **Markdown link that resolves to a non-existent file from repo root** — rewrite `../` prefix depth to a depth that matches the file's position in the repo; if no valid resolution exists, report as `UNRESOLVABLE`

**Output:** For each link, one line: `<file>:<line>: FIXED <old> -> <new>` or `<file>:<line>: UNRESOLVABLE <old>`.

Exit 0 if all fixed or no issues. Exit 1 if any UNRESOLVABLE remain.

## Acceptance Criteria

- Given a markdown file with a link that has one too many `../` hops (worktree was deeper than repo root), when the resolver runs, then it rewrites the link to the correct depth and the file validates clean under the detector
- Given a symlink that escapes the repo root, when the resolver runs, then it removes and recreates the symlink with a repo-relative target
- Given a hardcoded `.claude/worktrees/branch/` path in a shell script, when the resolver runs, then it rewrites to a `$(git rev-parse --show-toplevel)`-relative path
- Given a link the resolver cannot fix (target does not exist in the repo), when it runs, then it reports UNRESOLVABLE and exits 1
- Given detector output piped to the resolver, it resolves only the flagged links (not the whole file set) — targeted rewrite only
- The resolver is idempotent: running it twice on already-fixed files produces no changes

## Reproduction Steps

Follows from SPEC-216 reproduction steps — apply the detection output to the resolver.

## Severity

medium

## Expected vs. Actual Behavior

**Expected:** Detected worktree-specific links are rewritten in-place to valid repo-relative paths.

**Actual:** No rewrite tool exists — detected issues require manual fix.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Markdown depth rewrite | | |
| Symlink recreated repo-relative | | |
| Script path rewritten with git-root anchor | | |
| UNRESOLVABLE exits 1 | | |
| Targeted rewrite from piped detector output | | |
| Idempotent | | |

## Scope & Constraints

- Script lives at `.agents/bin/resolve-worktree-links.sh`
- Must be non-interactive
- Only rewrites files with confirmed suspicious links — does not touch clean files
- UNRESOLVABLE items are always reported; the caller decides whether to block or warn

## Implementation Approach

1. Accept piped detector output OR standalone file/dir args (run detector internally)
2. Group findings by file
3. Per file: apply rewrites in reverse line-number order (to avoid offset drift)
4. For symlinks: use `ln -sf` with computed relative target
5. Verify each rewrite by running the detector on the patched file; if it still flags, mark UNRESOLVABLE
6. Print summary, exit 0 or 1

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | — | Initial creation |
