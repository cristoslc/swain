---
title: "Fix swain-init Session Purpose Text Drop"
artifact: SPEC-297
track: implementable
status: Complete
author: "gemma4:31b-cloud"
created: 2026-04-07
last-updated: 2026-04-13
priority-weight: high
type: bug
parent-vision: VISION-006
linked-artifacts:
- [VISION-006](../../vision/Active/(VISION-006)-Untethered-Operator/(VISION-006)-Untethered-Operator.md)
swain-do: required
---

# Fix swain-init Session Purpose Text Drop

## Problem Statement

When `/swain-init` is invoked with a "Session purpose: <text>" prompt, the purpose text is currently ignored or dropped during the session startup sequence, failing to seed the session bookmark or provide a purpose summary to the operator.

## Desired Outcomes

- The operator's initial intent (passed via the launcher or prompt) is captured and preserved.
- The session bookmark is automatically updated with the purpose text.
- The purpose text is displayed prominently during the greeting to confirm the session's objective.

## External Behavior

- **Input:** `/swain-init Session purpose: <text>`
- **Output:**
    1. The string `<text>` is passed to `swain-bookmark.sh`.
    2. The greeting output includes `**Session purpose:** <text>`.

## Acceptance Criteria

- **Given** the operator launches with `Session purpose: Fix the login bug`, **When** the session starts, **Then** the session bookmark should reflect "Fix the login bug".
- **Given** a session is initialized with purpose text, **When** the greeting is displayed, **Then** the purpose text is visible in the CLI output.

## Reproduction Steps

1. Start a session with `/swain-init Session purpose: Test purpose capture`.
2. Observe that the purpose text does not appear in the greeting.
3. Check `.agents/session.json` or use a bookmark command to see that the purpose was not recorded.

## Severity

high

## Expected vs. Actual Behavior

**Expected:** The purpose text is extracted from the prompt and used to set the session bookmark and the greeting.

**Actual:** The purpose text is ignored by the current startup logic.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Bookmark updated from `SWAIN_PURPOSE` | `tests/test_session_purpose.sh` T1: `SWAIN_PURPOSE writes session.json bookmark.note` | Pass (commit `f33ad99a`) |
| Greeting JSON exposes `purpose` field | `tests/test_session_purpose.sh` T2 | Pass (commit `f33ad99a`) |
| Existing bookmark not clobbered | `tests/test_session_purpose.sh` T3 | Pass |
| Human-readable output shows `Purpose:` line | `tests/test_session_purpose.sh` T4 | Pass |
| No mutation when `SWAIN_PURPOSE` unset | `tests/test_session_purpose.sh` T5 | Pass |
| Launcher always exports `SWAIN_PURPOSE` | `skills/swain/scripts/swain` lines 673-681; 12 Tier-1 templates updated | Reviewed |

## Scope & Constraints

Focus on the `swain-init` skill logic and the `swain-session-greeting.sh` / `swain-session-bootstrap.sh` pipeline.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-07 | | Initial creation |
| Needs Manual Test | 2026-04-13 | f33ad99a | Greeting captures `SWAIN_PURPOSE` deterministically; launcher always exports env var; agent reads `.purpose` from greeting JSON. 9/9 automated tests pass. |
| Complete | 2026-04-13 | ad2b33c0 | All acceptance criteria verified. 9/9 automated tests pass. Manual smoke test confirmed by operator. |
