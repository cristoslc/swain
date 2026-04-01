---
title: "Operator Bin Symlink Auto-Repair"
artifact: SPEC-214
track: implementable
status: Complete
author: cristos
created: 2026-03-31
last-updated: 2026-03-31
priority-weight: high
type: bug
parent-epic: ""
parent-initiative: ""
linked-artifacts:
  - SPEC-180
  - SPEC-181
  - SPEC-186
  - ADR-019
  - EPIC-046
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Operator Bin Symlink Auto-Repair

## Problem Statement

After `swain-update` installs skills into a consumer project, the operator-facing scripts (`swain`, `swain-box`) exist inside the skill tree at `skills/swain/scripts/` but never get `bin/` symlinks. swain-doctor Check 19 (`bin/swain`) and Check 15 (`bin/swain-box`) detect the missing symlinks but only warn — they do not auto-repair. Check 20 (`.agents/bin/`) auto-repairs agent-facing symlinks using the same scan-and-link pattern, but explicitly excludes operator scripts via a hardcoded list. The result: consumer projects never get a working `bin/swain` without manual intervention.

A secondary problem is that the operator-script list is hardcoded in Check 20's exclusion filter (`local operator_scripts="swain swain-box"`). Adding a new operator-facing script requires editing doctor code in two places — the exclusion list and a new dedicated check — instead of declaring the script once.

## Desired Outcomes

Consumer projects that run `swain-update` followed by `swain-doctor` (or `swain-init` on first run) get working `bin/` symlinks for all operator-facing scripts. Adding a new operator script to the skill tree requires zero doctor code changes.

## External Behavior

**Manifest directory:** A new directory `skills/swain/usr/bin/` contains symlinks to operator-facing scripts. Each symlink's name is the command the operator types; each target points to the canonical script location in `scripts/`. This directory is the single source of truth for which scripts belong in `bin/`.

Example layout:
```
skills/swain/usr/bin/
  swain -> ../../scripts/swain
  swain-box -> ../../scripts/swain-box
```

**Doctor behavior (Check 15 + 19 consolidated):** Replace the two warn-only checks with a single scan-and-repair check that:
1. Finds the installed `usr/bin/` manifest by scanning `$SKILLS_ROOT/*/usr/bin/`
2. For each symlink in the manifest, ensures a corresponding `bin/<name>` symlink exists in the project root, pointing at the resolved script
3. Auto-repairs missing or stale symlinks (same pattern as Check 20)
4. Reports repairs in the check output

**Check 20 update:** Remove the hardcoded `operator_scripts` exclusion list. Instead, build the exclusion set dynamically by reading names from all `*/usr/bin/` directories found under `$SKILLS_ROOT`.

**swain-init behavior:** During first-run onboarding, after skills are installed, run the same scan-and-repair logic so `bin/` symlinks exist before the first session.

## Acceptance Criteria

1. **Given** a consumer project with `skills/swain/scripts/swain` present and no `bin/swain` symlink, **when** swain-doctor runs, **then** `bin/swain` is created as a relative symlink resolving to the script.

2. **Given** a consumer project with `skills/swain/scripts/swain-box` present and no `bin/swain-box` symlink, **when** swain-doctor runs, **then** `bin/swain-box` is created as a relative symlink resolving to the script.

3. **Given** a stale `bin/swain` symlink (pointing at an old path), **when** swain-doctor runs, **then** the symlink is replaced with the correct relative target.

4. **Given** a `bin/swain` that is a real file (not a symlink), **when** swain-doctor runs, **then** a conflict warning is emitted and the file is not overwritten.

5. **Given** a new operator script added to `skills/swain/usr/bin/` in a future release, **when** swain-doctor runs in a consumer project after update, **then** the new script gets a `bin/` symlink without any doctor code changes.

6. **Given** Check 20 runs after the consolidated operator-bin check, **when** it scans `skills/*/scripts/`, **then** operator scripts from `*/usr/bin/` are excluded dynamically (no hardcoded list).

7. **Given** swain-init runs on a fresh consumer project, **when** skills are installed, **then** `bin/` symlinks for all operator scripts exist before the session starts.

## Reproduction Steps

1. Create a fresh project, run `swain-init` (installs skills)
2. Observe: `skills/swain/scripts/swain` exists, `bin/swain` does not
3. Run `swain-doctor` — Check 19 warns but does not create the symlink
4. Operator must manually `mkdir -p bin && ln -sf ../skills/swain/scripts/swain bin/swain`

## Severity

high — blocks the primary entry point for consumer projects

## Expected vs. Actual Behavior

**Expected:** `swain-update` + `swain-doctor` produces a working `bin/swain` symlink in consumer projects, matching the auto-repair pattern already used for `.agents/bin/`.

**Actual:** Doctor warns about the missing symlink but never creates it. Consumer projects cannot use `bin/swain` without manual setup.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1: missing bin/swain auto-repaired | test-operator-bin-symlinks.sh Test 2 | PASS |
| AC2: missing bin/swain-box auto-repaired | test-operator-bin-symlinks.sh Test 3 | PASS |
| AC3: stale symlink repaired | test-operator-bin-symlinks.sh Test 4 | PASS |
| AC4: real file conflict not overwritten | test-operator-bin-symlinks.sh Test 5 | PASS |
| AC5: new script gets bin/ symlink | test-operator-bin-symlinks.sh Test 6 | PASS |
| AC6: Check 20 dynamic exclusion | test-operator-bin-symlinks.sh Test 7 | PASS |
| AC7: swain-init creates symlinks | swain-init SKILL.md Step 2.4 updated | PASS |

## Scope & Constraints

**In scope:**
- `skills/swain/usr/bin/` manifest directory with symlinks
- Consolidated doctor check replacing Checks 15 and 19
- Check 20 dynamic exclusion from `usr/bin/` manifest
- swain-init integration
- Tests for all auto-repair scenarios

**Out of scope:**
- Changing the swain-update distribution mechanism (`npx skills add`)
- Adding new operator scripts (this spec enables that; future specs do it)
- Modifying the shell function templates ([SPEC-181](../../Complete/(SPEC-181)-Swain-Shell-Function-Refactor/(SPEC-181)-Swain-Shell-Function-Refactor.md) scope)

## Implementation Approach

1. Create `skills/swain/usr/bin/` with symlinks to `../scripts/swain` and `../scripts/swain-box`
2. Write a consolidated `check_operator_bin_symlinks()` function in `swain-doctor.sh` that scans `$SKILLS_ROOT/*/usr/bin/` and auto-repairs `$REPO_ROOT/bin/` symlinks
3. Remove `check_swain_box()` (Check 15) and `check_swain_symlink()` (Check 19), replace with the new function
4. Update Check 20 to build its exclusion set from `*/usr/bin/` instead of hardcoding
5. Add the same scan-and-repair call to swain-init's onboarding flow
6. Add tests covering all 7 ACs

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | | Initial creation |
| Complete | 2026-03-31 | b7ce151 | All 7 ACs verified, 20/20 tests pass |
