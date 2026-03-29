---
title: "ADR-019 Script Convention Implementation"
artifact: EPIC-047
track: implementation
status: Complete
author: cristos
created: 2026-03-28
last-updated: 2026-03-29
parent-initiative: INITIATIVE-019
linked-artifacts:
  - ADR-019
  - EPIC-029
  - SPEC-136
  - SPEC-137
depends-on-artifacts: []
---

# ADR-019 Script Convention Implementation

## Goal

Implement the two-tier script convention defined in ADR-019 across the swain toolchain. Operator-facing scripts get `bin/` symlinks; agent-facing scripts get `.agents/bin/` symlinks. swain-doctor auto-repairs both, and swain-init bootstraps them on onboarding.

## Context

ADR-019 defines the convention but nothing implements the symlink lifecycle in consumer projects. SPEC-136/137/147 (EPIC-029) updated the paths that skills *reference*, but consumer projects have no mechanism to create or repair the symlinks. The Homelab project's doctor correctly reports `.agents/bin/swain-trunk.sh` as missing — because nothing creates it.

## Child Specs

| Spec | Title | Priority |
|------|-------|----------|
| SPEC-186 | Doctor `.agents/bin/` auto-repair | high |
| SPEC-187 | Init `.agents/bin/` bootstrap | medium |
| SPEC-188 | Doctor `bin/` auto-repair | medium |
| SPEC-189 | Migrate swain-box to `bin/` | low |
| SPEC-190 | Migrate all skills to `.agents/bin/` resolution | medium |

SPEC-186 is the minimum viable fix — it unblocks the release by making doctor self-heal the missing symlinks. SPEC-187 ensures new projects get them on first run. SPEC-188/189 extend the convention to operator-facing scripts. SPEC-190 completes the migration by replacing all `find`-based script lookups (~55 across 14 skills) with direct `.agents/bin/` resolution.

## Retrospective

**Terminal state:** Complete
**Period:** 2026-03-28 — 2026-03-29
**Related artifacts:** [SPEC-186](../../spec/Complete/(SPEC-186)-Doctor-Agents-Bin-Auto-Repair/SPEC-186.md), [SPEC-187](../../spec/Complete/(SPEC-187)-Init-Agents-Bin-Bootstrap/SPEC-187.md), [SPEC-188](../../spec/Complete/(SPEC-188)-Doctor-Bin-Auto-Repair/SPEC-188.md), [SPEC-189](../../spec/Complete/(SPEC-189)-Migrate-Swain-Box-To-Bin/SPEC-189.md), [SPEC-190](../../spec/Complete/(SPEC-190)-Migrate-Skills-To-Agents-Bin-Resolution/SPEC-190.md), [ADR-019](../../adr/Proposed/(ADR-019)-Project-Root-Script-Convention/(ADR-019)-Project-Root-Script-Convention.md)
**Standalone retro:** [RETRO-2026-03-29-adr-019-script-convention](../../swain-retro/2026-03-29-adr-019-script-convention.md)

### Summary

Bug-to-release in two sessions. A Homelab doctor report ("swain-trunk.sh missing") exposed a distribution gap: ADR-019 defined a convention but nothing created the symlinks in consumer projects. Session 1 escalated from diagnosis through ADR extension, EPIC creation, full implementation of 5 specs, skill-wide migration (55 find patterns → 64 .agents/bin/ references across 11 skills), and release (v0.22.0-alpha). Session 2 verified all 5 specs with live AC tests, found and fixed a `set -e` glob failure in preflight (`.claude/skills/*/scripts/` glob non-match killed the script before reaching the auto-repair section), updated doc references from `./swain-box` to `bin/swain-box`, and transitioned all artifacts.

### Reflection

**What went well:** The bug-to-release arc was fast — two sessions from discovery to fully closed EPIC. The layered spec decomposition (186→187/188→189, 190) correctly identified the critical path. Preflight self-healing meant consumer projects get the fix without manual intervention.

**What was surprising:** The `set -e` interaction with glob non-match was subtle — the find command's stderr was suppressed with `2>/dev/null` but its non-zero exit code still killed the script under `set -e`. This only manifested in worktrees (no `.claude/skills/` directory) and silently prevented the entire `.agents/bin/` auto-repair section from running. The prior session's "all tests pass" claim was from the swain source repo where the glob matched.

**Patterns observed:** Verification in a different context (worktree vs source repo) catches environment-dependent bugs. The existing standalone retro (RETRO-2026-03-29) was written during the implementation session before formal verification — a gap that this session's live AC testing filled. SPEC-190's estimate of ~55 find patterns was accurate; the migration was already complete from session 1.

### Learnings captured

| Item | Type | Summary |
|------|------|---------|
| `set -e` + glob non-match = silent script death | Bugfix (applied) | Added `\|\| true` to find command in preflight; pattern to watch for in all `set -e` scripts |
| Verify in worktree context, not just source repo | Process pattern | Environment-dependent bugs hide when tests run only in the source repo |

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-28 | — | Created to implement ADR-019 distribution layer |
| Complete | 2026-03-29 | — | All 5 child specs verified and completed; preflight set -e bugfix included |
