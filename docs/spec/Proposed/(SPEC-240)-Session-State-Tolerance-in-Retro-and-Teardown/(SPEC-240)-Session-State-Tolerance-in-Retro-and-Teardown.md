---
title: "Session-State Tolerance in Retro and Teardown"
artifact: SPEC-240
track: implementable
status: Proposed
author: cristos
created: 2026-04-02
priority-weight: medium
type: enhancement
parent-epic: EPIC-055
swain-do: required
---

# Session-State Tolerance in Retro and Teardown

## The Problem Statement Section.

This section describes the current failure modes and why they matter for session hygiene and learning capture.

swain-retro and swain-teardown both treat missing session state as a blocking error. swain-retro requires an active session and refuses to run without one. swain-teardown skips ticket sync when no session is active. The session-chain mode closes the session before teardown runs, so teardown finds no active session. Retro then fails because the session is closed. Both skills report failure instead of handling degraded state gracefully. This prevents retrospective capture and teardown summaries from being written even when work was done.

## The Desired Outcomes Section.

This section describes what should happen after the spec is implemented.

swain-retro runs even when no active session exists. It uses git log and recent artifact changes as evidence of what happened. swain-teardown runs in all contexts. It handles missing bookmarks, missing session state, and closed sessions as normal degraded conditions rather than errors. Both skills produce meaningful output regardless of session state completeness. The session-chain retro invocation works correctly because swain-session invokes retro before closing the session.

## The External Behavior Section.

This section describes the current behavior and the proposed changes for each skill affected by this spec.

### The Retro Failure Mode Sub-section.

The current session-chain path has a sequencing problem. swain-session close handler runs first. Then session state is cleared. Then swain-teardown is invoked with --session-chain. Then teardown invokes swain-retro. Then swain-retro checks session state and fails because the session is already closed. This path cannot work because the session is gone by the time retro runs.

### The Proposed Retro Invocation Sub-section.

The proposed fix changes the order of operations in the close handler. swain-session invokes swain-retro before clearing session state. The session is still active when retro runs. Retro captures session state. Then the session closes. Then teardown runs. Retro output is independent of whether the session remains open after retro completes.

The new invocation order is: swain-session close handler starts. Then swain-retro is invoked while the session is still active. Retro captures session state and produces output. Then session state is cleared. Then swain-teardown is invoked with --session-chain. Then teardown completes. Then session close completes. The session remains active until after retro finishes.

### The Teardown Tolerance Sub-section.

swain-teardown currently skips ticket sync when no active session exists. The --session-chain flag skips the session-active check. Both behaviors are correct but incomplete. The teardown should proceed with all available checks regardless of session state. Missing bookmarks, missing session state, and absent session-state.json are degraded conditions. They are not blocking errors. The teardown report should note degraded conditions but continue with remaining checks.

### The Graceful Degradation Sub-section.

| Condition | Current behavior | Desired behavior |
|-----------|-----------------|------------------|
| No active session | Retro fails; teardown skips ticket sync | Retro uses git log and artifact changes as evidence; teardown runs all checks and notes degraded state |
| Missing session-state.json | Session-active check passes with null values | Same — proceed with null values |
| Missing bookmarks.txt | Orphan check finds all worktrees as orphans | Same — flag as orphans |
| Session already closed | Retro fails; teardown runs but notes no session | Retro runs with recent git log; teardown notes degraded state |

## The Acceptance Criteria Section.

AC1 establishes that swain-retro uses git log evidence when no session is active. When swain-retro is invoked and the session check returns non-active status, it falls back to git log --oneline to gather evidence of recent work. Retro output is produced from git log and any recently modified artifacts.

AC2 establishes that swain-session invokes retro before clearing session state. The close handler calls swain-retro while the session is still active. The session state is cleared only after retro completes. Retro captures the session_id, focus_lane, purpose, and bookmarks from the still-active session state.

AC3 establishes that swain-teardown proceeds with all checks regardless of session state. When --session-chain is passed, teardown skips the session-active check but runs all hygiene checks (worktree orphan, git dirty state, ticket sync prompt, retro invitation, handoff summary). Each check handles its own degraded conditions gracefully.

AC4 establishes that missing bookmarks are noted but do not block teardown. When bookmarks.txt does not exist or is empty, teardown notes "no bookmarks found" in the findings and proceeds. All worktrees without bookmarks are reported as orphans with their safety assessment.

AC5 establishes that the teardown summary reports degraded conditions clearly. The summary distinguishes between "clean" (all checks passed), "degraded" (some checks skipped due to missing state), and "error" (a check failed with a critical error). Degraded conditions are reported in the findings section of SESSION-ROADMAP.md.

## The Verification Section.

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1 | Manual: invoke swain-retro with no active session, verify git log evidence is used | |
| AC2 | Manual: run swain-session close, verify retro captures session state before session clears | |
| AC3 | Manual: run swain-teardown with --session-chain and no active session, verify all checks run | |
| AC4 | Manual: remove bookmarks.txt, run teardown, verify orphans are reported without blocking | |
| AC5 | Manual: run teardown in degraded state, verify summary distinguishes degraded from clean | |

## The Scope and Constraints Section.

### The In Scope Items Sub-section.

| Item | Description |
|------|-------------|
| Retro fallback evidence | Use git log when session state is unavailable |
| Session-chain retro invocation | Move retro call before session-clear in swain-session |
| Teardown graceful degradation | All checks run regardless of session state completeness |
| Summary degradation labels | Distinguish clean, degraded, and error states |

### The Out of Scope Items Sub-section.

| Item | Rationale |
|------|-----------|
| Session state auto-repair | Missing state is a configuration problem, not a runtime one |
| Session state persistence | Session state is intentionally cleared on close |
| Retro quality scoring | Out of scope for this spec |

## The Implementation Approach Section.

### The Retro Fallback Evidence Sub-section.

Modify swain-retro to gather git log evidence when session check fails. The session check at the top of swain-retro should catch non-active status and fall back to recent git log. The fallback does not produce an embedded retro (since there is no EPIC or session artifact to attach to) but instead produces a standalone retro document in docs/swain-retro/ using git log evidence.

```bash
session_check=$(bash "$REPO_ROOT/.agents/bin/swain-session-check.sh" 2>/dev/null)
session_status=$(echo "$session_check" | jq -r '.status // "none"')

if [ "$session_status" != "active" ]; then
  # Fallback: use git log evidence
  git_evidence=$(git log --oneline -20 2>/dev/null)
  echo "No active session. Using git log evidence:"
  echo "$git_evidence"
  # Proceed to manual retro flow with git evidence as context
fi
```

### The Session-Chain Retro Invocation Sub-section.

Modify swain-session close handler in skills/swain-session/SKILL.md. Move the swain-retro invocation before the session-state.sh close call. The new order is: progress-log.sh → swain-retro (session still active) → session-state.sh close → swain-teardown --session-chain → commit SESSION-ROADMAP.md.

The session-state.json is still available when retro runs. Retro reads session_id, focus_lane, purpose, and bookmarks from the file. After retro completes, session-state.sh close is called to clear the state.

```bash
# Invoke retro while session is still active
SWAIN_RETRO_SKILL="$REPO_ROOT/.claude/skills/swain-retro/SKILL.md"
Skill("$SWAIN_RETRO_SKILL", "Session close — session is closing. Run /swain-retro to capture session learnings before the session state is cleared.")

# Clear session state
bash "$REPO_ROOT/.agents/bin/session-state.sh" close

# Run teardown (session is now closed)
Skill("$SWAIN_TEARDOWN_SKILL", "Session teardown — --session-chain flag passed from swain-session close handler.")
```

### The Teardown Graceful Degradation Sub-section.

Modify swain-teardown step 1 and step 3 to handle missing state gracefully. The --session-chain flag already skips the session-active check. Extend step 3 (ticket sync prompt) to run even without an active session but note the degraded condition.

```bash
# Step 3: Ticket sync — always run, note degraded state if no session
session_check=$(bash "$REPO_ROOT/.agents/bin/swain-session-check.sh" 2>/dev/null)
session_status=$(echo "$session_check" | jq -r '.status // "none"')

if [ "$session_status" = "active" ]; then
  echo "> Before closing, verify that tickets match what was done. Run \`tk issue list\`."
else
  echo "> No active session — ticket sync unavailable. Consider running \`tk issue list\` manually."
fi
```

## The Lifecycle Section.

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-02 | | Initial spec |
