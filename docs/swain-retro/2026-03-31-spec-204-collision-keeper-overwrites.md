---
title: "Retro: SPEC-204 fix-collisions.sh over-rewrites keeper references"
artifact: RETRO-2026-03-31-spec-204-collision-keeper-overwrites
track: standing
status: Active
created: 2026-03-31
last-updated: 2026-03-31
scope: "Bug fix for renumber-artifact.sh rewriting keeper references during collision resolution"
period: "2026-03-31"
linked-artifacts:
  - SPEC-204
  - SPEC-193
  - SPEC-158
---

# Retro: SPEC-204 fix-collisions.sh over-rewrites keeper references

## Summary

Single-session bug fix. `renumber-artifact.sh` Step 4 did a naive global `sed` replacing all occurrences of the old ID, then Step 4.5 tried to undo damage by restoring just the keeper's `artifact:` frontmatter line. This left keeper references in other files (ADRs, EPICs, body text) silently corrupted. Replaced both steps with a git-history-aware loop that uses `git log -S` and `merge-base --is-ancestor` to classify each reference as keeper or collision before deciding whether to rewrite.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| SPEC-204 | fix-collisions.sh over-rewrites keeper references | Complete |

## Reflection

### What went well

- **TDD paid off immediately.** Writing 13 unit tests before touching the script caught a macOS-specific symlink issue (`/tmp` vs `/private/tmp`) that would have been invisible in manual testing. The test setup (temp git repos with realistic collision scenarios) was reusable and ran in under 3 seconds.
- **Git-history approach was clean.** Using `git log -S` + `merge-base --is-ancestor` to determine reference provenance avoided complex file-level diffing. The logic fits in a single helper function (~30 lines).
- **Integration test mirrored the real scenario.** Reproducing the exact SPEC-194 collision from the bug report (Flesch-Kincaid vs Fast-Path Session Greeting) gave high confidence the fix handles the production case.

### What was surprising

- **The first debugging hypothesis was wrong.** Suspected `case` pattern matching was broken by parentheses in artifact directory names. Spent a cycle proving that wasn't the issue before discovering the real cause: macOS `/tmp` → `/private/tmp` symlink made `find` output paths and `$NEW_DIR` paths diverge. Path canonicalization (`pwd -P`) fixed it.
- **Worktree branched from `release`, not `trunk`.** The SPEC-204 doc was committed to trunk after the worktree was created, requiring a cherry-pick. The subsequent merge had 6 conflicts — all from `relink.sh` touching auto-generated roadmap files. This is friction from relink's broad scope during phase transitions.

### What would change

- **Canonicalize paths from the start.** The `REPO_ROOT` and `SOURCE_DIR` variables should have used `pwd -P` from the beginning (SPEC-158 era). This class of bug is invisible on Linux and only manifests on macOS with `/tmp` or other symlinked paths.
- **Relink scope is too broad.** Running `relink.sh` during a single spec's phase transition rewrites links across the entire `docs/` tree. When merging back to trunk, this creates conflicts with any parallel work that also ran relink. A scoped relink (only files referencing the moved artifact) would reduce merge friction.

### Patterns observed

- **"Undo the damage" patterns are fragile.** Step 4.5 (restore keeper frontmatter after global replace) is the same anti-pattern as "delete then recreate" — it works for the narrow case it was designed for but misses edge cases. The correct fix was to not cause the damage in the first place (selective rewriting).
- **Recurring: macOS path normalization.** This is at least the second time symlink resolution has caused test or script failures. Any script that compares paths from different sources (user input vs `find` output vs `git` output) needs canonicalization.

## SPEC candidates

1. **Scoped relink** — `relink.sh` should accept an artifact ID and only update files that reference that artifact, rather than scanning all of `docs/`. This would reduce merge conflicts when parallel worktrees both run phase transitions.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| Scoped relink to reduce merge conflicts | SPEC candidate | relink.sh touches too many files during phase transitions |
