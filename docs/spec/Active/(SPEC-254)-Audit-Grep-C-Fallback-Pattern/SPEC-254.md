---
title: "Audit grep -c || echo fallback pattern across swain scripts"
artifact: SPEC-254
track: implementable
status: Active
author: Cristos L-C
created: 2026-04-03
last-updated: 2026-04-03
type: bug
parent-epic: ""
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
source-issue: ""
swain-do: required
---

# Audit grep -c || echo fallback pattern across swain scripts

## Problem Statement

The pattern `found_count=$(grep -c 'pattern' ... || echo "0")` produces `"0\n0"` when grep finds no matches. `grep -c` outputs `0` to stdout and exits with status 1 (no matches). The `||` fallback then appends a second `0` via `echo`. Downstream arithmetic comparisons (`[[ "$found_count" -eq 0 ]]`) fail with a syntax error.

This was found and fixed in `swain-doctor.sh:705` (crash debris check). The same anti-pattern may exist in other scripts.

## Desired Outcomes

All swain scripts use safe grep-count patterns. No silent arithmetic failures from double-output command substitutions.

## External Behavior

Scripts that count grep matches handle the zero-match case without producing multi-line values in numeric variables.

## Acceptance Criteria

- AC1: Given a scan of `skills/*/scripts/*.sh` and `.agents/bin/*.sh`, when any file contains the pattern `grep -c` followed by `|| echo` inside a `$(...)` substitution, then those instances are identified and fixed.
- AC2: Given the fix is applied, when each fixed script runs with zero grep matches, then the count variable holds exactly `0` (single line, no trailing newline).

## Reproduction Steps

1. Run `swain-doctor.sh` on a repo with no crash debris.
2. Observe the shell error: `[[: 0\n0: syntax error in expression`.

## Severity

low

## Expected vs. Actual Behavior

**Expected:** `found_count` is `0`, arithmetic comparison succeeds silently.

**Actual:** `found_count` is `0\n0`, arithmetic comparison fails with a syntax error.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Only audit `.sh` files under `skills/*/scripts/` and `.agents/bin/`.
- The fix pattern is `result=$(grep -c ...) || result=0` (assignment outside the subshell).
- Do not refactor unrelated code in matched files.

## Implementation Approach

1. Grep for the anti-pattern: `grep -rn 'grep -c.*||.*echo' skills/*/scripts/*.sh .agents/bin/*.sh`
2. For each match, apply the same fix used in `swain-doctor.sh:705`.
3. Verify each fixed script with a zero-match input.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-03 | | Initial creation — fast-path bug from retro |
