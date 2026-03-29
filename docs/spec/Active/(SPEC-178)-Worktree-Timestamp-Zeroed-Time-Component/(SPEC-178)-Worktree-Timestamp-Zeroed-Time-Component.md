---
title: "Worktree Timestamp Zeroed Time Component"
artifact: SPEC-178
track: implementable
status: Active
author: cristos
created: 2026-03-28
last-updated: 2026-03-28
priority-weight: ""
type: bug
parent-epic: ""
parent-initiative: INITIATIVE-019
linked-artifacts:
  - SPEC-174
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Worktree Timestamp Zeroed Time Component

## Problem Statement

The swain-session skill instructs agents to name worktrees using `session-YYYYMMDD-HHmmss-XXXX` format, but the time portion is consistently `000000`. For example, `session-20260328-000000-k8m2` instead of `session-20260328-143022-k8m2`. This reduces uniqueness (all sessions started on the same date share the same timestamp prefix) and makes it harder to identify when a session was created.

## Desired Outcomes

Worktree names include accurate time components, making each session identifiable by both date and time of creation.

## External Behavior

**Inputs:** Agent reads swain-session SKILL.md instructions and generates a worktree name.

**Precondition:** Session bootstrap detects `worktree.isolated == false` and triggers `EnterWorktree`.

**Expected output:** Worktree name like `session-20260328-143022-a7f3` with correct HHmmss.

**Constraint:** The name must be generated before calling `EnterWorktree`, which only accepts a string — it cannot run shell commands.

## Acceptance Criteria

- **AC-1:** Given an agent starting a new session, when the worktree name is generated, then the HHmmss portion reflects the actual current time (not `000000`).
- **AC-2:** Given the skill instructions, when an agent reads them, name generation is delegated to a script (`swain-worktree-name.sh`) — no agent-side date formatting.
- **AC-3:** The fix applies to both `skills/swain-session/SKILL.md` and `skills/swain-do/SKILL.md` wherever the naming pattern is referenced.

## Reproduction Steps

1. Start a new swain session via the `swain` shell launcher.
2. Observe the worktree name created by `EnterWorktree`.
3. The time component is `000000` regardless of actual time.

## Severity

low

## Expected vs. Actual Behavior

**Expected:** Worktree named `session-20260328-143022-a7f3` (with real time).

**Actual:** Worktree named `session-20260328-000000-k8m2` (time always zeroed).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- The root cause is that skill prose tells agents to "use `session-YYYYMMDD-HHmmss-XXXX`" but agents generate timestamps using their own date awareness, which lacks reliable time-of-day. The fix should provide a concrete shell command or script that the agent runs to produce the name string.
- The `EnterWorktree` tool accepts a name parameter (string only) — the agent must obtain the formatted name before calling it.
- Scope limited to the naming mechanism in skill instructions. No changes to `EnterWorktree` itself.

## Implementation Approach

1. Create `skills/swain-session/scripts/swain-worktree-name.sh` — a script that emits a correctly formatted worktree name to stdout. Accepts an optional context argument (default: `session`). Uses shell `date` for the timestamp and `/dev/urandom` for the 4-char random suffix. Output format: `<context>-YYYYMMDD-HHmmss-XXXX`.
2. Update `skills/swain-session/SKILL.md` to instruct agents to run the script, capture its stdout, and pass the result as the `name` parameter to `EnterWorktree`. Remove prose that tells agents to construct the name themselves.
3. Update `skills/swain-do/SKILL.md` to reference the same script wherever it instructs agents to generate worktree names.
4. Verify by starting a new session and confirming the time component is non-zero.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-28 | — | Initial creation |
