---
title: "Retro: Deprecate swain-session (ADR-023)"
artifact: RETRO-2026-04-04-deprecate-swain-session
track: standing
status: Active
created: 2026-04-04
last-updated: 2026-04-04
scope: "ADR-023 implementation — split swain-session into swain-init (startup) and swain-teardown (shutdown), distribute mid-session features"
period: "2026-04-04"
linked-artifacts:
  - ADR-023
---

# Retro: Deprecate swain-session (ADR-023)

## Summary

Deprecated swain-session by splitting its responsibilities across five skills. Teardown was rewritten from a passive hygiene checker into a full 6-step shutdown sequence (digest, retro, merge, cleanup, close, commit). Init absorbed session startup (greeting, focus lane, session state). Roadmap absorbed the status dashboard. swain-do absorbed bookmarks, decisions, and progress log. README reconciliation went to retro, sync, and release. 15 files changed across the skill tree. 66 BDD structural tests validate the migration.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| ADR-023 | Deprecate swain-session | Created (Active) |
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
| SPEC-237: Remove swain-session skill directory | SPEC | Delete `skills/swain-session/`, relocate scripts to surviving skill directories |
| SPEC-238: Structural cross-skill invariant tests | SPEC | Grep-based test suite validating routing, preamble, and reference consistency across all skills |
| ADR-024: Skill naming convention — verbs not nouns | ADR | Name skills by their action (init, teardown, sync) not their domain noun (session, project) |
