---
title: "Portable skill path resolution"
artifact: SPEC-213
track: implementable
status: Active
author: operator
created: 2026-03-31
last-updated: 2026-03-31
priority-weight: high
type: bug
parent-epic: ""
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Portable skill path resolution

## Problem Statement

Swain shell scripts hardcode `skills/swain-*/...` paths when referencing their own resources and sibling skills. This works in the swain source repo (where skills live at `skills/`) but breaks in every consumer project, where `npx skills add` installs to `.agents/skills/`. The result: swain-doctor health checks, preflight, and session timing scripts silently skip checks or fail outright in consumer repos.

## Desired Outcomes

All swain shell scripts work identically whether installed at `skills/`, `.agents/skills/`, or `.claude/skills/`. Consumer projects get the same health checks, governance freshness validation, and tooling as the source repo.

## External Behavior

**Inputs:** Scripts invoked from any install location via symlink (`.agents/bin/`) or direct path.

**Outputs:** Identical behavior regardless of install root.

**Preconditions:** Scripts are bash, invoked with `bash <path>` or as executables.

**Constraints:**
- Must not break the swain source repo (where `skills/` is the canonical location).
- Symlinked `.agents/bin/` entries must resolve through to the real script location.
- No new dependencies (pure bash path resolution).

## Reproduction Steps

1. Install swain skills into a consumer project via `npx skills add --all`
2. Run `.agents/bin/swain-preflight.sh`
3. Observe: governance freshness check skips (canonical file not found), SSH readiness skips, security scanner check skips, skill change discipline check skips

## Severity

high

## Expected vs. Actual Behavior

**Expected:** Preflight and doctor scripts find their reference files and sibling skill scripts regardless of install location.

**Actual:** All `skills/swain-*/...` paths resolve relative to `$REPO_ROOT`, which has no `skills/` directory in consumer projects. Checks silently degrade to "skipped" status.

## Acceptance Criteria

1. **Given** a script in `skills/swain-doctor/scripts/`, **when** it references its own `references/` directory, **then** it uses a path derived from `BASH_SOURCE[0]`, not a hardcoded `skills/` prefix.

2. **Given** a script that references a sibling skill (e.g., `swain-do/bin/tk`), **when** invoked from `.agents/skills/swain-doctor/scripts/`, **then** it resolves the sibling via the same skills root (`.agents/skills/swain-do/bin/tk`).

3. **Given** a script invoked via a symlink in `.agents/bin/`, **when** `BASH_SOURCE[0]` is the symlink, **then** the script resolves through the symlink to the real script location before deriving paths.

4. **Given** all affected scripts are patched, **when** run in the swain source repo, **then** behavior is unchanged (no regression).

5. **Given** SKILL.md and reference docs contain `skills/swain-*/...` paths, **when** these are read by Claude as instructions, **then** they use relative references or describe the resolution pattern so the agent can find the files.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

**In scope:**
- Shell scripts (`*.sh`) in `swain-doctor`, `swain-session`, `swain-design` that hardcode `skills/` paths
- SKILL.md and reference `.md` files with hardcoded script/reference paths
- The `find skills` call in `check_swain_box()`

**Out of scope:**
- Test files (they run from the source repo by convention)
- The `check-skill-changes.sh` `SKILL_PATHS` variable (it already searches all three locations)
- Python scripts in `swain-security-check` (separate skill, separate fix)

**Affected files (scripts):**

| File | Hardcoded refs | Cross-skill refs |
|------|---------------|-----------------|
| `swain-doctor/scripts/swain-doctor.sh` | 5 self-refs | 2 (swain-do tk) |
| `swain-doctor/scripts/swain-preflight.sh` | 3 self-refs | 2 (swain-security-check) |
| `swain-session/scripts/swain-preflight-timing.sh` | 3 (doctor refs) | 2 (swain-security-check) |
| `swain-session/scripts/swain-startup-timing.sh` | 1 (preflight) | 0 |
| `swain-session/scripts/swain-status.sh` | 0 | 1 (swain-do ticket-query) |
| `swain-design/scripts/specwatch.sh` | 0 | 1 (swain-do ticket-query) |

**Fix pattern:**
```bash
# At top of each script, after REPO_ROOT:
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}" 2>/dev/null || echo "${BASH_SOURCE[0]}")")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"        # .../swain-doctor
SKILLS_ROOT="$(dirname "$SKILL_DIR")"       # skills/ or .agents/skills/
```

Then replace:
- `skills/swain-doctor/references/...` with `$SKILL_DIR/references/...`
- `skills/swain-doctor/scripts/...` with `$SCRIPT_DIR/...`
- `skills/swain-do/bin/tk` with `$SKILLS_ROOT/swain-do/bin/tk`
- `find skills -name ...` with `find "$SKILLS_ROOT" -name ...`

## Implementation Approach

1. Add the three-line path resolution preamble to each affected script
2. Replace all hardcoded `skills/` references with the derived variables
3. Update SKILL.md and reference docs to use relative paths or describe the resolution
4. Test in source repo (regression) and a temp consumer-like layout (fix validation)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | — | Initial creation |
