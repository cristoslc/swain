---
title: "Retro: v0.28.0-alpha Release — Teardown/Rewrite/Release"
artifact: RETRO-2026-04-01-teardown-rewrite-release
track: standing
status: Active
created: 2026-04-01
last-updated: 2026-04-01
scope: "SPEC-261 orphan removal, SPEC-262 session-state tolerance, SPEC-263 worktree bookmark lifecycle, v0.28.0-alpha release"
period: "2026-04-01"
linked-artifacts:
  - [SPEC-261](../spec/Complete/(SPEC-261)-Specgraph-Hierarchy-Projection-Output/(SPEC-261)-Specgraph-Hierarchy-Projection-Output.md)
  - [SPEC-262](../spec/Complete/(SPEC-262)-Lifecycle-Scoped-Materialized-Child-Views/(SPEC-262)-Lifecycle-Scoped-Materialized-Child-Views.md)
  - [SPEC-263](../spec/Complete/(SPEC-263)-Automatic-Hierarchy-Reconciliation/(SPEC-263)-Automatic-Hierarchy-Reconciliation.md)
  - [EPIC-060](../epic/Complete/(EPIC-060)-Materialized-Artifact-Parenting-View/(EPIC-060)-Materialized-Artifact-Parenting-View.md)
  - SPEC-232
---

# Retro: v0.28.0-alpha Release — Teardown/Rewrite/Release

## Summary

Three specs closed in one session, each building on the previous: session-state tolerance in retro (SPEC-262 AC1), close handler reordering so retro runs before session close (SPEC-262 AC2), then a complete rewrite of swain-teardown covering orphan removal (SPEC-261), session-chain integration (SPEC-262 AC3-5), and worktree bookmark lifecycle (SPEC-263). The release followed, with changelog anti-patterns refined through multiple user feedback rounds.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| [SPEC-261](../spec/Complete/(SPEC-261)-Specgraph-Hierarchy-Projection-Output/(SPEC-261)-Specgraph-Hierarchy-Projection-Output.md) | Orphan Worktree Removal | Implemented in swain-teardown |
| [SPEC-262](../spec/Complete/(SPEC-262)-Lifecycle-Scoped-Materialized-Child-Views/(SPEC-262)-Lifecycle-Scoped-Materialized-Child-Views.md) | Session-State Tolerance in Retro/Teardown | AC1-AC5 all implemented |
| [SPEC-263](../spec/Complete/(SPEC-263)-Automatic-Hierarchy-Reconciliation/(SPEC-263)-Automatic-Hierarchy-Reconciliation.md) | Worktree Bookmark Lifecycle via session.json | Implemented via swain-bookmark.sh |
| [EPIC-060](../epic/Complete/(EPIC-060)-Materialized-Artifact-Parenting-View/(EPIC-060)-Materialized-Artifact-Parenting-View.md) | Session Bookmark Lifecycle Integrity | All children complete |
| v0.28.0-alpha | Release | Pushed |

## Reflection

### What went well

**Three specs addressed in one coherent pass.** The teardown rewrite was planned as three separate specs but they were deeply coupled — the orphan removal needed the bookmark lifecycle, and both needed session-chain integration. Rather than three half-ships, one session closed all three with a unified implementation.

**Changelog feedback loop produced real improvements.** The user rejected the initial changelog as including development process ("close handler reordered" was in Supporting). That pushback was correct — it surfaced that the swain-release skill lacked explicit rules about what Supporting means. The anti-pattern additions to the skill (bucket exclusivity, explicit exclusions for development process and artifact transitions) were a direct result of that feedback. The final changelog was cleaner.

**Close handler reordering was surgical.** The previous teardown retro had identified the problem clearly: retro was invoked after the session was closed, so it couldn't read session state. The fix — move swain-retro invocation before session-state.sh close — was a three-line change in the right place. No ambiguity about what needed changing.

**Retro git-log fallback is the right abstraction.** Rather than a session-chain flag or pending-retro marker, swain-retro now falls back to `git log` when no session is active. This makes retro independently useful and removes a lifecycle dependency that was creating edge cases.

### What was surprising

**Bookmark fragmentation was deeper than expected.** Three separate storage locations existed simultaneously: `session-bookmark.sh` (broken symlink), `.agents/bookmarks.txt` (stale), and the `bookmark` key in `session.json` (active for context notes). The broken symlink had existed since the session-bookmark.sh rename in an earlier session — it was never cleaned up because no single skill owned the full lifecycle of that file.

**Changelog quality failures were classification failures, not stylistic ones.** The initial changelog wasn't poorly written — it was misclassified. "close handler reordered" was Supporting because it was a development process change. But Supporting is for infrastructure (deps, CI, internal refactors) — not for development process. The rule "Supporting is mutually exclusive with Features and Roadmap" should have caught this; the skill just didn't say it explicitly.

**Stale state accumulates silently.** The `.agents/bookmarks.txt` file had a single stale entry from 2026-04-03 — a worktree that no longer existed. It wasn't causing any error, but it was wrong. No process catches this kind of drift.

### What would change

**Add new skills to the README skills table during implementation, not after.** swain-teardown shipped in v0.28.0-alpha but wasn't in the skills table. This is a completeness check that should be part of the SPEC-263 acceptance criteria: "skill is listed in README.md skills table." Retroactively fixing it is easy; the gap shouldn't exist in the first place.

**Automate stale bookmark cleanup earlier.** The `worktree prune` subcommand in swain-bookmark.sh existed but wasn't run automatically. Running it during session start (in swain-doctor or swain-session) would prevent stale entries from accumulating to the point where they're a manual cleanup task.

**Add changelog dry-run to release preflight.** The release was revised four times because the changelog kept including development process or artifact transitions. A pre-release dry-run flag that shows exactly what would go in each bucket — with the anti-pattern rules applied — would catch misclassification before the user sees it.

### Patterns observed

**"tested but not wired" family keeps reproducing in different forms.** The release-skill-deletion incident (2026-03-28) was "skill not invoked." The dead-code-in-release retro (2026-03-31) was "script not wired." This session's initial changelog was "development process not excluded from changelog." All three are the same root cause: a rule that exists in documentation but isn't enforced by a check. The anti-pattern additions to swain-release are the fix for this instance.

**Handoff boundary failures continue to cluster around session transitions.** Previous retros have flagged bookmark ownership (2026-04-01 session-bookmark-handoff), concurrent-session bugs, and launcher boundary failures. This session added the retro invocation ordering and the stale bookmarks.txt. The session lifecycle is a high-risk surface for silent failures — nothing errors, but state is wrong.

**User feedback on changelog quality is a signal worth acting on strongly.** The user pushed back on changelog quality four times. Each pushback revealed a deeper gap in the skill's rules. The anti-pattern additions were not obvious from first principles — they emerged from repeated user criticism of the same shape of output.

## Learnings captured

<!-- The swain repo routes artifact-implying learnings to candidates, not memory. -->

## SPEC candidates

None. Each gap identified maps to work already completed in this session or work that can be done as a low-overhead addition to existing specs:

1. **swain-teardown in README skills table** — This is a one-line addition. Not worth a spec — just fix it as part of the next skill change.
2. **swain-bookmark.sh worktree prune at session start** — Already implemented. The `prune` subcommand exists. If it's not being called, add it to swain-doctor's orphan check loop or swain-session's start sequence. Not worth a new spec.
3. **swain-release changelog dry-run** — This would improve the release ceremony. Can be added to the existing swain-release skill as a `--dry-run` flag that shows the buckets without tagging. Small enough to handle as a note in the release skill, not a new spec.

## README drift

**New feature not in README:** swain-teardown is absent from the Skills table in README.md. The v0.28.0-alpha release shipped it as a feature but the table was not updated. This is a concrete fix — add a row for swain-teardown.

Suggested addition to the Skills table:

```
| **swain-teardown** | Session hygiene — orphan worktree detection, git dirty-state guard, bookmark cleanup |
```

**Deferred:** Decide whether EPIC-060 (session bookmark lifecycle integrity) warrants a mention in the README overview. The README currently says swain-session handles bookmarks but doesn't mention teardown. A brief mention of end-of-session hygiene would align with the shipped behavior.
