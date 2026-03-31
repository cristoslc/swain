---
title: "swain-doctor parallel check cascade failure"
artifact: SPEC-192
track: implementable
status: Complete
author: cristos
created: 2026-03-29
last-updated: 2026-03-29
priority-weight: high
type: bug
parent-epic: ""
parent-initiative: INITIATIVE-003
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# swain-doctor parallel check cascade failure

## Problem Statement

When swain-doctor runs its health checks during swain-init, it fires all checks as parallel Bash tool calls. If the first check errors (e.g., the governance grep finds no matching files and returns exit code 1), the Claude Code runtime cancels all sibling parallel tool calls. This causes the entire doctor run to produce zero useful results — every check shows "Cancelled: parallel tool call Bash(…) errored."

## Desired Outcomes

swain-doctor health checks complete reliably regardless of individual check failures. Operators see actionable results from every check category, not a wall of cancellation messages.

## External Behavior

**Before:** A single check error cascades to cancel all parallel sibling checks. The operator sees ~8 cancelled checks and no diagnostic output.

**After:** Each check runs independently. A failure in one check does not prevent other checks from completing and reporting their status.

## Acceptance Criteria

- AC1: Given a project where the governance grep returns no matches, when swain-doctor runs, then all other checks still execute and report results.
- AC2: Given any single check that exits non-zero, when swain-doctor runs checks, then the remaining checks are not cancelled.
- AC3: The doctor summary table includes results from all check categories, marking failed checks individually rather than cancelling the batch.

## Reproduction Steps

1. Run `swain-init` (or `/swain-doctor`) in a project where the governance block is not yet installed.
2. Observe that the first Bash call (`grep -l "swain governance" CLAUDE.md AGENTS.md .cursor/rules/swain-governance.mdc 2>/dev/null`) returns exit code 1 (no files match).
3. All subsequent parallel Bash calls are cancelled by the runtime.

## Severity

high — swain-doctor produces no useful output when any single check fails, defeating its purpose as a health check tool.

## Expected vs. Actual Behavior

**Expected:** Each health check runs independently. If governance grep fails, the tool availability check, tickets validation, skill detection, and all other checks still complete and report their findings.

**Actual:** All parallel sibling Bash calls are cancelled when any one errors. The operator sees a wall of red "Cancelled" messages and gets no diagnostic information.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1: governance grep no-match doesn't cascade | swain-doctor.sh ran 17/17 checks; governance=warning, all others completed | PASS |
| AC2: non-zero exit doesn't cancel siblings | All checks run under set +e in single script; each reports independently | PASS |
| AC3: summary includes all categories | JSON summary: {"total": 17, "ok": 13, "warning": 4, "advisory": 0} | PASS |

## Scope & Constraints

- The fix is in the swain-doctor skill file (`skills/swain-doctor/SKILL.md`), not in the Claude Code runtime — we cannot change how the runtime handles parallel tool call errors.
- The solution must work within Claude Code's tool-call model: either sequentialize checks, or ensure each parallel check guards against non-zero exits (e.g., `command || true` patterns in the skill instructions, or consolidating checks into a single script that handles errors internally).
- Consolidating into a shell script (like `swain-preflight.sh` already does for a subset of checks) is the preferred approach — it moves error handling into bash where `set +e` works naturally and avoids the parallel-cancellation problem entirely.

## Implementation Approach

Two viable approaches:

1. **Consolidate into a single doctor script** (`swain-doctor.sh`): Move all check logic into a bash script that runs checks sequentially with `set +e`, captures per-check pass/fail/warn status, and emits a structured JSON summary. The skill file becomes a thin orchestrator that calls the script once and presents results. This mirrors the pattern already established by `swain-preflight.sh` and `swain-session-bootstrap.sh`.

2. **Guard each parallel call**: Ensure every parallel Bash invocation in the skill instructions uses `|| true` or equivalent so no call returns non-zero. Less clean — it's a band-aid that doesn't address the root cause of too many parallel tool calls.

Approach 1 is strongly preferred — it reduces token usage (one tool call vs. many), eliminates the cascade failure class entirely, and makes the checks testable as a standalone script.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-29 | — | Initial creation — bug observed during swain-init run |
| Complete | 2026-03-30 | — | Retroactive verification — script on trunk, all ACs pass |
