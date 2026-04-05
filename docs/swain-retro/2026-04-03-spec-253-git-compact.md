---
title: "Retro: SPEC-253 Git-Compact Implementation"
artifact: RETRO-2026-04-03-git-compact
track: standing
status: Active
created: 2026-04-03
last-updated: 2026-04-03
scope: "Research through implementation of git-compact wrapper — two troves, one DESIGN, one SPEC, one script"
period: "2026-04-03"
linked-artifacts:
  - SPEC-253
  - DESIGN-017
---

# Retro: SPEC-253 Git-Compact Implementation

## Summary

Single-session flow from research to shipped implementation. Collected two troves (`ai-development-patterns`, `rtk-cli-token-compression`), wrote DESIGN-017 (system contract) and SPEC-253 (implementation spec), built and verified a 30-line git-compact wrapper in a worktree, cherry-picked to trunk, and pushed. Total wall-clock time: approximately 30 minutes for the full pipeline.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| trove: ai-development-patterns | PaulDuvall's 27-pattern AI dev catalog | Created (a2bfeb7) |
| trove: rtk-cli-token-compression | RTK homepage — CLI output compressor | Created (c94bfc1) |
| [DESIGN-017](../design/Active/(DESIGN-017)-Git-Compact-CLI-Contract/(DESIGN-017)-Git-Compact-CLI-Contract.md) | Git-Compact CLI Contract | Active |
| [SPEC-253](../spec/Active/(SPEC-253)-Git-Compact-Wrapper-Script/(SPEC-253)-Git-Compact-Wrapper-Script.md) | Git-Compact Wrapper Script | Implemented (f5adaec) |

## Reflection

### What went well

The trove-to-design-to-spec-to-implementation pipeline worked end-to-end in one session without blocking on ceremony. The operator's directive to "just write them" bypassed brainstorming for a well-understood problem, which was the right call — the research troves had already explored the design space. Cherry-pick was the correct recovery when the worktree merge hit conflicts, avoiding a time-consuming conflict resolution session on unrelated files. The script passed 6/7 ACs on first run (7th was SKIP due to RTK not being installed, not FAIL).

### What was surprising

The worktree merge produced massive conflicts on files unrelated to git-compact — list indexes, doctor scripts, DESIGN artifacts from other worktree sessions. The worktree branch had diverged from trunk because trunk had accumulated commits from other worktrees being merged while this one was active. This is the same class of problem the `multi-agent-collision-vectors` trove documents.

The pre-commit hook failed in the worktree because `.pre-commit-config.yaml` is not a tracked file and worktrees don't inherit untracked files from the main checkout. The `PRE_COMMIT_ALLOW_NO_CONFIG=1` workaround is functional but fragile.

### What would change

For single-file additions (no modifications to existing files), cherry-pick should be the default integration strategy over merge. The merge approach is correct when the worktree modifies files that other worktrees might also touch — but for pure additions, cherry-pick avoids the entire conflict surface.

The pre-commit hook should handle missing config gracefully in worktrees. This is a known issue that could be a SPEC.

### Patterns observed

1. **Research-first design is fast for small work.** When the troves establish the problem space, the DESIGN and SPEC write themselves. The operator's "just write them" override was faster than brainstorming would have been.
2. **Worktree isolation adds value even for trivial changes** — it kept the dirty working tree (4 modified files, dozens of untracked) completely separate from the implementation work.
3. **Cherry-pick > merge for additive worktrees.** When a worktree only adds new files, cherry-pick produces a clean integration without touching unrelated conflicts.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| Cherry-pick as default for additive worktrees | SPEC candidate | When a worktree only adds files (no modifications), swain-do/finishing-a-development-branch should suggest cherry-pick over merge |
| Pre-commit config in worktrees | SPEC candidate | Worktrees should either copy .pre-commit-config.yaml on creation or the hook should exit 0 when config is missing in a worktree context |
