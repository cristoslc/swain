---
title: "Retro: Deprecate swain-session (ADR-030)"
artifact: RETRO-2026-04-04-deprecate-swain-session
track: standing
status: Active
created: 2026-04-04
last-updated: 2026-04-04
scope: "ADR-030 implementation — split swain-session into swain-init (startup) and swain-teardown (shutdown), distribute mid-session features"
period: "2026-04-04"
linked-artifacts:
  - ADR-030
  - SPEC-259
---

# Retro: Deprecate swain-session (ADR-030)

## Summary

Deprecated swain-session by splitting its responsibilities across five skills. Teardown was rewritten from a passive hygiene checker into a full 6-step shutdown sequence (digest, retro, merge, cleanup, close, commit). Init absorbed session startup (greeting, focus lane, session state). Roadmap absorbed the status dashboard. swain-do absorbed bookmarks, decisions, and progress log. README reconciliation went to retro, sync, and release. 15 files changed across the skill tree. 66 BDD structural tests validate the migration.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| ADR-030 | Deprecate swain-session | Created (Active) |
| swain-teardown v3.0.0 | Full shutdown sequence | Rewritten |
| swain-init Phase 7 | Session start absorption | Expanded |
| swain-roadmap v2.0.0 | Status dashboard absorption | Expanded |
| swain-do v4.0.0 | Bookmarks, decisions, progress log | Expanded |
| swain meta-router | Session triggers rerouted | Updated |

## Reflection

### What went well

The feature distribution was clean. Each swain-session responsibility had one obvious new home — no ambiguity about where status dashboard, bookmarks, or focus lane belonged. The operator gave clear direction upfront (teardown should do everything, session splits into init + teardown, focus is an init concern, reconciliation is retro/sync/release). This eliminated design thrash.

The BDD test suite (66 assertions, 9 acceptance criteria) passed on the first run. Structural grep-based tests are fast to write and effective for migration validation — they verify that routing tables, section headers, script invocations, and cross-references all landed correctly without needing to spin up the full skill runtime.

### What was surprising

The cross-reference surface was larger than expected. Six skill preambles, two AGENTS files, tool-availability.md, runtime-checks.md, and README.md all contained `/swain-session` references that would send operators to a deprecated skill. A grep sweep at the end caught them, but the sheer count (30+ matches across the tree) shows how deeply a "central" skill gets wired into everything.

The old teardown had no merge step at all. Worktrees could never be "safe to remove" because their branches were never merged — the teardown just flagged them as "branch not fully merged" and moved on. This was the root cause of the operator's complaint: teardown was structurally incapable of doing its job.

### What would change

The swain-session skill directory was left in place rather than removed. This was deliberate (validate first), but it means a follow-up is needed to actually delete it and clean up its scripts directory. The scripts themselves (`swain-session-check.sh`, `swain-session-state.sh`, etc.) are utilities used by other skills and should stay — they just need to not live under a deprecated skill directory.

The session skill should never have accumulated this many responsibilities. Startup, shutdown, status dashboard, focus lane, bookmarks, decision recording, progress log, and README reconciliation all ended up in one skill because "session" was a convenient bucket. A naming convention that forced single-responsibility (like the current split: init, teardown, roadmap) would have prevented the accumulation.

### Patterns observed

**Lifecycle skills accumulate unrelated features.** "Session" became a dumping ground because it touched both startup and shutdown — any feature that needed "session context" got bolted on. The fix is to name skills by their verb (init, teardown, sync) not their noun (session).

**Cross-skill references are a migration tax.** Every skill preamble that says "start one with `/swain-session`" is a coupling point that must be updated when routing changes. The `swain-session-check.sh` script abstraction was right (scripts survived the migration unchanged), but the prose references were brittle.

**Passive skills get ignored.** The old teardown only reported problems without fixing them. The operator stopped invoking it because it never actually did anything useful. Skills that only observe and report get abandoned; skills that take action get used.

**Structural BDD tests are underused.** Grep-based tests that validate skill content (routing tables, section ordering, script references) are trivial to write and catch the exact class of bugs this migration could introduce. The project should use more of these for cross-skill invariants.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| SPEC-264: Remove swain-session skill directory | SPEC | Delete `skills/swain-session/`, relocate scripts to surviving skill directories |
| SPEC-265: Structural cross-skill invariant tests | SPEC | Grep-based test suite validating routing, preamble, and reference consistency across all skills |
| ADR-031: Skill naming convention — verbs not nouns | ADR | Name skills by their action (init, teardown, sync) not their domain noun (session, project) |

## Session 2: Collision resolution and SPEC-259

**Period:** 2026-04-04 (continuation session)

### Summary

Merged trunk into the worktree, resolved 13 artifact number collisions introduced by concurrent worktree work, and wrote SPEC-259 (swain-sync preflight script). The collision fix renumbered artifacts across SPECs, EPICs, and ADRs — including ADR-023→ADR-030 (the main deliverable of this worktree). BDD tests were updated to track the renumber and re-verified at 66/66 pass.

### Reflection

#### What went well

SPEC-259 was fast to scope. The operator identified the optimization (extract Steps 1–3.9 to a script), the preflight/subagent split was obvious, and the JSON output contract fell out naturally. The feedback memory about script placement (`skills/<name>/bin/`, not `.agents/bin/`) prevented a structural mistake before it happened.

The collision tooling handled the bulk of renumbering automatically — 13 artifacts across 9 collision groups, with cross-reference rewrites touching 40+ files. Without `fix-collisions.sh` and `renumber-artifact.sh`, this would have been a multi-hour manual job.

#### What was surprising

`fix-collisions.sh` hit a stale `index.lock` mid-run on the 6th of 9 renumbers. The manual retry with `renumber-artifact.sh` then picked the wrong artifact (alphabetically first match) instead of the intended one. This created a duplicate (two artifacts both numbered SPEC-265 pointing to "Improve-swain-search-snapshots") that required manual cleanup: `git rm` the wrong one, re-run with `--source-dir` to target the correct artifact. The collision script's lack of atomicity (partial failure leaves staged-but-incomplete state) made recovery harder than it needed to be.

A second round of `fix-collisions.sh` was needed because the first round only renumbered the "newer" artifact in each collision group, but some groups had three-way collisions (trunk Proposed + trunk Complete + worktree Proposed). The second round caught the remaining 4.

#### What would change

`renumber-artifact.sh` should refuse to run when multiple directories match the source ID unless `--source-dir` is provided. The current behavior (pick first match, emit a warning) is too dangerous — it silently renumbers the wrong artifact. A hard error would have prevented the SPEC-265 mess.

`fix-collisions.sh` should handle `index.lock` gracefully — either wait-and-retry or clean up its own staged state before exiting. Partial completion with "commit when ready" leaves the tree in a state where the next run may pick different renumber targets.

#### Patterns observed

**Collision resolution is worktree merge tax.** Every worktree that creates artifacts risks ID collisions when merging back. The `next-artifact-id.sh` cross-branch scan (SPEC-193) prevents collisions within a single session, but can't prevent two concurrent sessions from picking the same IDs. This is an inherent cost of worktree isolation.

**Multi-match tooling needs explicit targeting.** When a tool finds multiple candidates, "pick the first one" is almost never right. Hard-fail with disambiguation is safer than soft-warn with a guess. This applies beyond `renumber-artifact.sh` — any script that resolves artifact IDs from partial input should follow this pattern.

### Learnings captured

| Item | Type | Summary |
|------|------|---------|
| SPEC-259: Swain-sync preflight script | SPEC | Extract Steps 1–3.9 into `skills/swain-sync/bin/swain-sync-preflight.sh` to reduce subagent token spend |
| renumber-artifact.sh should hard-fail on ambiguous source | SPEC candidate | Refuse to proceed when multiple directories match; require `--source-dir` |
| fix-collisions.sh needs atomicity or rollback | SPEC candidate | Handle index.lock, ensure partial failures don't corrupt subsequent runs |
