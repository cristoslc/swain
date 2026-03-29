---
title: "Session Bootstrap Script Consolidation"
artifact: SPEC-175
track: implementable
status: Complete
author: cristos
created: 2026-03-26
last-updated: 2026-03-28
priority-weight: ""
type: enhancement
parent-epic: EPIC-039
parent-initiative: ""
linked-artifacts:
  - SPIKE-048
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Session Bootstrap Script Consolidation

## Problem Statement

The swain-session startup sequence produces 3-5 visible Bash tool calls in the operator's terminal: a failed inline command (exit 127 from nested `git rev-parse` + `find` + `bash`), a retry `find` to locate the script, the actual script execution, worktree detection, and session.json loading. Each tool call renders as a separate result block with full output, creating visual noise that obscures the meaningful "Session ready" summary. The root cause is that SKILL.md instructs the agent to orchestrate individual shell commands for what is a fixed, known startup sequence.

## Desired Outcomes

The operator sees **one** tool call result during session startup instead of 3-5. The "Session ready" summary remains identical. The 45-second startup time is not increased. Operators who read the tool call output see a clean, single invocation rather than retry/fallback noise.

## External Behavior

**Input:** Agent calls `swain-session-bootstrap.sh` with flags:
- `--path <dir>` — repo root (default: auto-detect via `git rev-parse`)
- `--auto` — non-interactive mode (passed through to tab-naming)
- `--skip-worktree` — omit worktree detection (for sessions already isolated)

**Output:** JSON on stdout:
```json
{
  "tab": "project-name @ branch-name",
  "worktree": { "isolated": true, "path": "/path/to/worktree", "branch": "worktree-session-2026-03-26" },
  "session": {
    "focus": "VISION-001",
    "bookmark": "Epic decomposition design spec approved",
    "lastBranch": "trunk"
  },
  "warnings": []
}
```

**Preconditions:** tmux session active (tab-naming degrades gracefully without it), git repo detected.

**Postconditions:** Terminal tab renamed, worktree status detected, session.json loaded and `lastBranch` updated. No side effects beyond what the individual scripts already perform.

## Acceptance Criteria

1. **Given** a tmux session in a swain repo, **when** the agent invokes `swain-session-bootstrap.sh --auto`, **then** tab naming, worktree detection, and session.json loading all complete in a single Bash tool call.
2. **Given** a non-tmux terminal, **when** the agent invokes `swain-session-bootstrap.sh --auto`, **then** tab naming is skipped gracefully and the JSON output omits the `tab` field.
3. **Given** an already-isolated worktree, **when** the agent invokes `swain-session-bootstrap.sh --auto`, **then** `worktree.isolated` is `true` and no `EnterWorktree` suggestion is emitted.
4. **Given** no `.agents/session.json` exists, **when** the agent invokes the bootstrap script, **then** the session object in the JSON output has null/empty fields and no error is thrown.
5. **Given** the bootstrap script is deployed, **when** SKILL.md is updated to use it, **then** the session startup section references a single `bash .../swain-session-bootstrap.sh --auto` invocation instead of multi-step orchestration.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- The bootstrap script consolidates existing logic from `swain-tab-name.sh`, worktree detection (git commands), and `swain-bookmark.sh` / session.json reading. It does **not** replace those scripts — it orchestrates them internally.
- Worktree *creation* (`EnterWorktree` tool) remains a separate agent tool call if needed — the bootstrap script only *detects* isolation status. The agent decides whether to create a worktree based on the JSON output.
- The script must remain idempotent — safe to call multiple times in a session.
- No new dependencies beyond what swain-session already requires (bash, git, jq, tmux optional).

## Implementation Approach

1. **Red:** Write a test harness that invokes the bootstrap script and validates JSON output schema, covering all AC scenarios (tmux/no-tmux, worktree/no-worktree, session.json present/absent).
2. **Green:** Create `skills/swain-session/scripts/swain-session-bootstrap.sh` that sources/calls existing scripts internally and emits structured JSON.
3. **Green:** Update `swain-session/SKILL.md` Step 1-2 to reference the single bootstrap call.
4. **Refactor:** Extract any duplicated logic between bootstrap and the individual scripts into shared functions sourced by both.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-26 | — | Initial creation |
| Complete | 2026-03-28 | 7dc8042 | Retroactive close — bootstrap script verified, all ACs pass |
