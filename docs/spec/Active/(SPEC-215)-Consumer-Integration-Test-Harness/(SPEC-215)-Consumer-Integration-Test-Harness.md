---
title: "Consumer integration test harness"
artifact: SPEC-215
track: implementable
status: Active
author: operator
created: 2026-03-31
last-updated: 2026-03-31
priority-weight: medium
type: enhancement
parent-epic: ""
parent-initiative: ""
linked-artifacts:
  - SPEC-213
depends-on-artifacts:
  - SPEC-213
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Consumer integration test harness

## Problem Statement

Swain has no test that runs scripts from a consumer install layout. All existing tests run from the source repo where skills live at `skills/`. [SPEC-213](../../Active/(SPEC-213)-Portable-Skill-Path-Resolution/(SPEC-213)-Portable-Skill-Path-Resolution.md) fixed ~20 hardcoded path references that broke in consumer projects (where skills install to `.agents/skills/`), but nothing prevents the same bug class from returning. A new contributor adding a cross-skill reference will naturally write `skills/swain-foo/...` because that's what works locally.

## Desired Outcomes

Regressions to SPEC-213's portable path fix are caught before release. Developers get a fast signal when a script or doc reference breaks the consumer layout, without needing access to a separate consumer project.

## External Behavior

**Input:** `bash skills/swain-doctor/tests/test-consumer-layout.sh` (or via `.agents/bin/` symlink)

**Output:** TAP-style pass/fail per check, exit 0 on all pass, exit 1 on any failure.

**Preconditions:** Run from the swain source repo. Requires `git`, `bash`, `jq`.

**Constraints:**
- Must not require `npx`, `node`, or network access — pure local simulation.
- Must clean up temp directories on exit (trap-based cleanup).
- Must complete in under 10 seconds.

## Acceptance Criteria

1. **Given** a temp git repo with skills copied to `.agents/skills/`, **when** `swain-doctor.sh` runs, **then** it produces valid JSON with all checks at status `ok` or `warning` (no script errors, no "not found" messages caused by path resolution).

2. **Given** the same consumer layout, **when** `swain-preflight.sh` runs, **then** it exits 0 or 1 (not 2+) and does not emit "file not found" or "No such file" errors to stderr.

3. **Given** the consumer layout, **when** doctor runs, **then** the `governance`, `tk_health`, `ssh_readiness`, and `crash_debris` checks do not report "not found (skipped)" due to missing script/reference paths. They may report actual findings, but not path-resolution failures.

4. **Given** a `.agents/bin/` symlink that points to `.agents/skills/swain-doctor/scripts/swain-doctor.sh`, **when** doctor is invoked via that symlink, **then** path resolution works identically to a direct invocation.

5. **Given** the test harness, **when** run from the source repo on trunk, **then** all assertions pass (the harness itself is green on the current codebase).

6. **Given** a CI or pre-release check, **when** the harness is included in the test suite, **then** it runs without manual setup and produces machine-readable output.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

**In scope:**
- A single test script (`test-consumer-layout.sh`) in `skills/swain-doctor/tests/`
- Simulates the consumer layout: temp git repo + `.agents/skills/` + `.agents/bin/` symlinks
- Tests `swain-doctor.sh` and `swain-preflight.sh` from the consumer layout
- Tests symlink-through-invocation (`.agents/bin/` → `.agents/skills/.../scripts/`)

**Out of scope:**
- Testing `npx skills add` itself (that's the skills CLI's job)
- Testing non-doctor/non-preflight scripts (specwatch, status, etc.) — can be added later
- Testing on actual consumer projects (this is a simulation)
- Cross-platform testing (macOS only for now, Linux is a nice-to-have)

## Implementation Approach

1. **Setup function:** Create a temp dir, `git init`, copy `skills/swain-doctor/` and `skills/swain-do/` into `.agents/skills/`, create `.agents/bin/` symlinks mirroring the source repo pattern but pointing to `.agents/skills/...`.

2. **Doctor JSON validation:** Run `swain-doctor.sh` from the consumer layout, parse JSON output with `jq`, assert no check has `"status":"error"` or contains path-resolution failure strings (`"not found"`, `"No such file"`).

3. **Preflight exit code:** Run `swain-preflight.sh`, capture stderr, assert no path-resolution errors.

4. **Symlink invocation:** Run doctor via the `.agents/bin/` symlink, compare output structure to direct invocation.

5. **Cleanup:** `trap` removes temp dir on exit.

```bash
# Skeleton
setup_consumer_layout() {
  CONSUMER_DIR="$(mktemp -d)"
  cd "$CONSUMER_DIR"
  git init -q
  mkdir -p .agents/skills .agents/bin
  # Copy skills that doctor depends on
  cp -R "$SOURCE_REPO/skills/swain-doctor" .agents/skills/
  cp -R "$SOURCE_REPO/skills/swain-do" .agents/skills/
  # Create .agents/bin/ symlinks (matching ADR-019 convention)
  for script in .agents/skills/swain-doctor/scripts/*.sh; do
    [[ "$(basename "$script")" == test-* ]] && continue
    ln -sf "../../.agents/skills/swain-doctor/scripts/$(basename "$script")" \
      ".agents/bin/$(basename "$script")"
  done
}
```

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | — | Initial creation |
