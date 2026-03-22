---
title: "Retro: Overnight autonomous artifact sweep"
artifact: RETRO-2026-03-22-overnight-autonomous-artifact-sweep
track: standing
status: Active
created: 2026-03-22
last-updated: 2026-03-22
scope: "SPEC-148 implementation, EPIC-041 creation, retroactive close of 9 implemented-but-untracked specs"
period: "2026-03-22 — 2026-03-22"
linked-artifacts:
  - EPIC-041
  - SPEC-148
  - SPEC-149
  - SPEC-057
  - SPEC-103
  - SPEC-129
  - SPEC-139
  - SPEC-052
  - SPEC-091
  - SPEC-115
  - SPEC-138
  - SPEC-142
---

# Retro: Overnight autonomous artifact sweep

## Summary

Autonomous overnight session with two workstreams: (1) new implementation work establishing worktree discipline for skill changes, and (2) a systematic sweep of Active specs that turned out to already be implemented, closing 9 of them. The session produced 1 new EPIC, 2 new SPECs (1 implemented, 1 proposed), and transitioned 9 existing specs from Active to Complete.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| EPIC-041 | Worktree Discipline | Created (Proposed) |
| SPEC-148 | Worktree Discipline for Skill Changes | Implemented (Needs Manual Test) |
| SPEC-149 | Generalize Trunk Change Detection | Created (Proposed) |
| SPEC-057 | tk close Must Release Claim Lock | Retroactive close — already at a549105 |
| SPEC-103 | Artifact Cross-Reference Hyperlinking | Retroactive close — already at b39cc54 |
| SPEC-129 | Auto-Populate specwatch-ignore on Supersession | Retroactive close — in SKILL.md + phase-transitions.md |
| SPEC-139 | Desired Outcomes Section for Shippable Artifacts | Retroactive close — already at 3a2943f |
| SPEC-052 | Vision-Rooted Chart Hierarchy | Retroactive close — chart.sh/chart_cli.py fully operational |
| SPEC-091 | TRAIN Artifact Type | Retroactive close — definition, template, train-check.sh all present |
| SPEC-115 | Roadmap Initiative Children Level-Based Filtering | Retroactive close — roadmap.py initiative_direct_children |
| SPEC-138 | iTerm Tab Name Bleed From Global set-titles | Retroactive close — client_tty isolation in swain-tab-name.sh |
| SPEC-142 | swain-do Completion/Retro Chain | Retroactive close — Plan completion handoff in SKILL.md |

## Reflection

### What went well

**Retroactive close as a high-value activity.** 9 specs worth of implemented-but-untracked work discovered in a single session. This is pure artifact debt — the code exists, the features work, but the specs were stuck in Active. Sweeping for these is cheap (grep for deliverables, verify ACs) and reduces noise in `swain chart ready` output significantly.

**Pre-plan signal scanning works.** SPEC-057 was caught as already-implemented during the pre-plan scan, avoiding a full reimplementation cycle. The 2-signal threshold (git history + deliverable files) is a reliable heuristic.

**Governance reconciliation pathway.** The operator corrected the approach of editing AGENTS.md directly — the correct path is `AGENTS.content.md` → swain-doctor reconciliation → AGENTS.md. This is now documented in SPEC-148 and was used successfully. Hash-based freshness checking confirms the canonical and installed versions match.

**TDD on the new implementation.** SPEC-148's check-skill-changes.sh was implemented with proper RED-GREEN-REFACTOR: 5 tests written first (all fail), script implemented (all pass), then preflight integration tested the same way.

### What was surprising

**SPEC-142 (Worktree Ticket Isolation) false positive.** The explore agent reported `find_tickets_dir()` parent-walk as implementation evidence, but live testing from a worktree revealed cross-worktree ticket lookup still fails. The parent-walk finds the main checkout's `.tickets/` when called from a worktree under the repo, but tickets created in a different worktree are in that worktree's `.tickets/` and remain invisible. **Lesson: pre-plan signal scanning without live AC verification can produce false positives for partially-implemented work.**

**using-git-worktrees is not locally modifiable.** The initial SPEC-148 design included updating the vendored superpowers skill. The operator flagged this — superpowers skills have no local update path that preserves changes across upgrades. The fix was to route enforcement through AGENTS.md governance instead, which is a better design anyway (behavioral rule vs. skill modification).

### What would change

**Batch retroactive closes more aggressively.** The session found 9 closeable specs across two sweeps. A periodic "artifact sweep" — perhaps monthly or at release boundaries — would prevent this debt from accumulating. This could be a swain-doctor check or a dedicated skill.

**Live-test ACs before claiming retroactive close.** The SPEC-142 false positive shows that checking deliverable files exist is necessary but not sufficient. For bug-type specs especially, running the reproduction steps to confirm the fix is critical.

### Patterns observed

**Artifact lifecycle debt accumulates silently.** Specs get implemented during focused sprints but the transition ceremony (verification table, phase move, lifecycle entry) gets skipped in the rush to the next task. This is the same pattern the earlier retro (2026-03-22-session-roadmap-infrastructure) called out with SPEC-143's retroactive close.

**Recurring theme: governance > skill modification.** Both the SPEC-148 worktree discipline and the SPEC-129 specwatch-ignore patterns work by adding behavioral rules to governance files (AGENTS.md, SKILL.md) rather than modifying tooling. This is a design principle worth reinforcing — behavioral guidance in governance files scales better than tool-level enforcement.

## Learnings captured

| Memory file | Type | Summary |
|------------|------|---------|
| feedback_retro_governance_pathway.md | feedback | Always use AGENTS.content.md → swain-doctor reconciliation for governance changes, never edit AGENTS.md directly |
| feedback_retro_live_verify.md | feedback | Pre-plan signal scanning must include live AC verification for bug-type specs — file existence alone produces false positives |
