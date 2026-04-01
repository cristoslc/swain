---
title: "Retro: SPEC-222 Doctor Warn-Only Check Auto-Repair Audit"
artifact: RETRO-2026-03-31-spec-222-doctor-auto-repair
track: standing
status: Active
created: 2026-03-31
last-updated: 2026-03-31
scope: "SPEC-222 — promotion of 5 warn-only checks to auto-repair in swain-doctor.sh"
period: "2026-03-31 — 2026-03-31"
linked-artifacts:
  - SPEC-222
  - SPEC-214
---

# Retro: SPEC-222 Doctor Warn-Only Check Auto-Repair Audit

## Summary

SPEC-222 promoted 5 warn-only checks to auto-repair in `swain-doctor.sh`: `memory_directory`,
`script_permissions`, `commit_signing`, `governance` stale block, and `crash_debris` git lock.
All 5 follow the pattern from SPEC-214 — attempt repair, report `advisory` on success, `warning`
on conflict. 25/25 tests pass. Work completed in one session.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| [SPEC-222](../spec/Complete/(SPEC-222)-Doctor-Warn-Only-Check-Auto-Repair-Audit/(SPEC-222)-Doctor-Warn-Only-Check-Auto-Repair-Audit.md) | Doctor Warn-Only Check Auto-Repair Audit | Complete |

## Reflection

### What went well

- The repair-safety rubric (idempotent, non-destructive, no network, reversible, no masking)
  gave clear criteria. Ruling candidates in/out was fast — no debate.
- TDD caught the awk `-v` multi-line bug before it shipped. The `governance` repair silently
  dropped block content when passing multi-line strings via `awk -v`; a failing test exposed it
  before any code review was needed.
- The worktree isolation pattern worked as intended — changes stayed clean and the main branch
  was never touched.

### What was surprising

- **Ambient crash debris**: stale tk claim locks (`stale_tk_locks`) are always present when
  tasks are claimed in this environment. The crash_debris test assumed only the git lock would
  appear, but stale_tk_locks created `other_lines`, blocking the `advisory` path. The fix was
  to auto-remove git locks regardless of other debris, not to assume a clean environment.
- **awk `-v` multi-line limitation**: bash awk's `-v` flag interprets escape sequences and
  silently truncates multi-line content. Passing governance block content via `-v` produced
  empty output instead of an error. The workaround (write content to temp file, use `getline`)
  is non-obvious and not documented anywhere in the skill.

### What would change

- **Test environment assumptions**: tests that create specific debris conditions (git lock,
  script permissions) should first audit ambient state and adapt assertions accordingly, rather
  than assuming a clean environment.
- **Commit non-interactivity**: the `mv` and `cp` commands in test teardown were interactive
  on this system (prompted y/n). Using `-f` everywhere should be the standard, not something
  to discover mid-test.

### Patterns observed

- **Warn-by-default is a tax that compounds**: each warn-only check that *could* auto-repair
  creates repeated manual toil. SPEC-214 surfaced this; SPEC-222 acted on it. The rubric now
  exists so future checks don't default to warn without a reason.
- **Multi-line awk `-v` is a recurring footgun**: this is the second time a multi-line string
  passed via `-v` has silently misbehaved in swain scripts. A shared pattern (temp file +
  getline) should be documented where shell scripts handle multi-line content.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| Document awk getline pattern for multi-line content | SPEC candidate | Shared scripting pattern or ADR to prevent recurring silent failures |
| Tests should detect ambient state before asserting | SPEC candidate | Test helper or convention for swain-doctor tests running in dirty environments |

## SPEC candidates

1. **Scripting conventions: multi-line content in awk** — document the temp-file + `getline`
   pattern as the canonical way to pass multi-line bash variables to awk in swain scripts.
   The `-v` limitation is non-obvious and has bitten governance repair twice now. Could be an
   ADR or a scripting-conventions reference file in the skill. Low priority, high payoff for
   future script authors.

2. **swain-doctor test harness: ambient state detection** — the test file assumes a clean
   environment for debris/permissions/signing tests. A small preamble that records ambient
   state and adapts assertions (or skips when state makes the condition un-testable) would make
   the suite more robust across environments. Particularly relevant for `crash_debris` and
   `commit_signing` tests.
