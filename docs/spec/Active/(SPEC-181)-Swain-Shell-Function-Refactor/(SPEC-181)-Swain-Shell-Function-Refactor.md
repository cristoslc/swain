---
title: "Swain Shell Function Refactor"
artifact: SPEC-181
track: implementable
status: Active
author: cristos
created: 2026-03-28
last-updated: 2026-03-28
priority-weight: high
type: enhancement
parent-epic: EPIC-046
parent-initiative: ""
linked-artifacts:
  - SPEC-180
  - EPIC-045
depends-on-artifacts:
  - SPEC-180
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Swain Shell Function Refactor

## Problem Statement

The `swain` shell function (installed by swain-init into user dotfiles, EPIC-045) currently handles runtime detection, flag selection, and invocation. SPEC-180 moves all of this into a project-root script that also handles crash recovery. The shell function must become a thin wrapper that finds and runs the script, with graceful fallback for projects that haven't adopted it.

## Desired Outcomes

The operator's experience is unchanged — they type `swain` and get a session. But internally, the function delegates everything to the project-root script when present, gaining crash recovery and runtime preference resolution for free.

## External Behavior

**Inputs:** CLI arguments from the operator (e.g., `--fresh`, `--runtime gemini`)

**Behavior:**
1. Look for the `swain` script at: `./swain`, `./.agents/bin/swain`
2. If found: `exec` it, passing through all CLI arguments. Done.
3. If not found: fall back to the current behavior (detect runtimes, invoke with `/swain-init`) — graceful degradation for projects without the script.

**Postconditions:** Either the script is running (and handles everything), or the runtime is launched directly (legacy path).

## Acceptance Criteria

1. **Given** a project with the `swain` script at `.agents/bin/swain`, **when** the operator runs `swain`, **then** the script is executed (not the function's built-in logic).
2. **Given** a project without the script, **when** the operator runs `swain`, **then** the function falls back to direct runtime invocation (current behavior preserved).
3. **Given** CLI arguments (e.g., `swain --fresh --runtime gemini`), **when** the function runs the script, **then** all arguments are forwarded.
4. **Given** the function source, **when** reviewed, **then** it is under 20 lines of shell (thin wrapper contract).

## Scope & Constraints

- Must work in bash and zsh (the two shells swain-init supports)
- Must not break existing installations — the fallback path preserves current behavior exactly
- No crash detection, no debris cleanup, no session selection in the function — all that lives in the script
- The function is installed once by swain-init and rarely changes; the script is versioned with the project and evolves freely

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-28 | — | Initial creation from SPIKE-051 |
