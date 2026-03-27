---
title: "Doctor Superpowers Detection Zsh Word-Split Bug"
artifact: SPEC-167
track: implementable
status: Active
author: operator
created: 2026-03-25
last-updated: 2026-03-25
priority-weight: medium
type: bug
parent-epic: ""
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Doctor Superpowers Detection Zsh Word-Split Bug

## Problem Statement

swain-doctor's superpowers detection reports all 6 skills as missing even when they are fully installed. The root cause is a zsh word-splitting difference: `for skill in $SUPERPOWERS_SKILLS` treats the entire space-delimited string as a single token in zsh, iterating once instead of six times.

## Desired Outcomes

Superpowers detection correctly identifies installed skills regardless of whether the host shell is bash or zsh. Doctor and preflight produce accurate health reports, preventing false install prompts that erode operator trust in session startup diagnostics.

## External Behavior

**Input:** swain-doctor or swain-preflight runs superpowers detection on a system where zsh is the default shell and all 6 superpowers skills are installed.

**Expected output:** `Superpowers ........ ok (6/6 skills detected)`

**Preconditions:** Skills exist at `.agents/skills/<name>/SKILL.md` or `.claude/skills/<name>/SKILL.md`.

## Acceptance Criteria

- **AC-1:** Given zsh is the shell, when swain-doctor runs superpowers detection with all 6 skills installed, then it reports `ok (6/6 skills detected)`.
- **AC-2:** Given zsh is the shell, when 3 of 6 skills are installed, then it reports `partial (3 of 6 missing)` with correct missing names.
- **AC-3:** Given bash is the shell, when all 6 skills are installed, then it reports `ok (6/6 skills detected)` (no regression).
- **AC-4:** The swain-preflight.sh script, if it contains the same pattern, is also fixed.

## Reproduction Steps

1. Open a zsh shell (default on macOS).
2. Run the detection loop:
   ```bash
   SUPERPOWERS_SKILLS="brainstorming writing-plans test-driven-development verification-before-completion subagent-driven-development executing-plans"
   found=0; missing=0; missing_names=""
   for skill in $SUPERPOWERS_SKILLS; do
     if ls .agents/skills/$skill/SKILL.md .claude/skills/$skill/SKILL.md 2>/dev/null | head -1 | grep -q .; then
       found=$((found + 1))
     else
       missing=$((missing + 1))
       missing_names="$missing_names $skill"
     fi
   done
   echo "found=$found missing=$missing"
   ```
3. Observe: `found=0 missing=1` — the loop iterates once with the entire string as a single skill name.

## Severity

medium

## Expected vs. Actual Behavior

**Expected:** The loop iterates 6 times, once per skill name, and correctly counts found/missing skills.

**Actual:** In zsh, `$SUPERPOWERS_SKILLS` is not word-split. The loop iterates once with the value `"brainstorming writing-plans test-driven-development verification-before-completion subagent-driven-development executing-plans"` as a single token. `ls` fails to find a directory matching that concatenated string, so `found=0` and `missing=1`.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Fix must be POSIX-compatible or handle both bash and zsh.
- Preferred approach: use `set -- skill1 skill2 ...` positional parameters or a `while` loop with explicit word boundary handling, avoiding zsh-specific `${=VAR}` syntax.
- The doctor SKILL.md inline code block and any `.sh` scripts must both be fixed.
- Do not change the list of checked skills — only the iteration mechanism.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-25 | — | Initial creation — bug confirmed via live reproduction |
