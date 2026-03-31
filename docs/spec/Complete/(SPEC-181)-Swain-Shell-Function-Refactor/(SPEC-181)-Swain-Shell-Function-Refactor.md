---
title: "Swain Shell Function Refactor"
artifact: SPEC-181
track: implementable
status: Complete
author: cristos
created: 2026-03-28
last-updated: 2026-03-30
priority-weight: high
type: enhancement
parent-epic: EPIC-046
parent-initiative: ""
linked-artifacts:
  - SPEC-180
  - EPIC-045
  - ADR-019
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
1. Look for the `swain` script at: `bin/swain` (per [ADR-019](../../../adr/Proposed/(ADR-019)-Project-Root-Script-Convention/(ADR-019)-Project-Root-Script-Convention.md), this is a symlink to the skill tree)
2. If found: `exec` it, passing through all CLI arguments. Done.
3. If not found: fall back to the current behavior (detect runtimes, invoke with `/swain-init`) — graceful degradation for projects without the script.

**Postconditions:** Either the script is running (and handles everything), or the runtime is launched directly (legacy path).

## Acceptance Criteria

1. **Given** a project with `bin/swain` (symlink per ADR-019), **when** the operator runs `swain`, **then** the script is executed (not the function's built-in logic).
2. **Given** a project without `bin/swain`, **when** the operator runs `swain`, **then** the function falls back to direct runtime invocation (current behavior preserved).
3. **Given** CLI arguments (e.g., `swain --fresh --runtime gemini`), **when** the function runs the script, **then** all arguments are forwarded.
4. **Given** the function source, **when** reviewed, **then** it is under 20 lines of shell (thin wrapper contract).
5. **Given** an existing old-style `swain()` function in the rc file, **when** swain-init runs the migration check, **then** the operator is shown a diff and offered replacement.
6. **Given** the operator declines migration, **when** swain-init continues, **then** the old function is preserved and a warning is logged.

## Migration: Existing Shell Functions

Operators who installed the shell launcher via EPIC-045 (swain-init Phase 4.5) have a full-bodied `swain()` function in their rc file that directly invokes the runtime. This function must be replaced with the thin wrapper.

### Detection

swain-init checks the rc file during Phase 4.5 (launcher step). The old-style function is identified by the presence of a direct runtime invocation inside the function body:

```bash
# For each supported runtime, check if the function body contains direct invocation
OLD_STYLE=false
if grep -q 'swain()' "$RC_FILE" 2>/dev/null; then
  # Extract the function body (between swain() { and the matching })
  FUNC_BODY=$(sed -n '/swain()/,/^}/p' "$RC_FILE")
  # Old-style: contains direct runtime invocation
  for pattern in \
    'claude --dangerously-skip-permissions' \
    'gemini -y' \
    'codex --full-auto' \
    'copilot --yolo' \
    'crush --yolo'; do
    if echo "$FUNC_BODY" | grep -q "$pattern"; then
      OLD_STYLE=true
      break
    fi
  done
fi
```

If `OLD_STYLE=true`, the function is a pre-SPEC-181 installation.

### Migration flow

1. Show the operator the current function and the replacement:

   > **Shell launcher migration** — Your `swain` function invokes the runtime directly. The new version delegates to a project-root script that adds crash recovery and runtime preference resolution.
   >
   > **Current** (in `<rc-file>`):
   > ```
   > <current function body>
   > ```
   >
   > **Replacement:**
   > ```
   > <new thin wrapper from template>
   > ```
   >
   > Replace? (yes/no)

2. If accepted: replace the old function in the rc file using sed — match from `swain()` to the closing `}` and substitute with the new template content.

3. If declined: warn that crash recovery features require the new function, and log "Shell launcher: migration declined". The old function continues to work (it just won't delegate to the project-root script).

### New installations

For rc files without any `swain()` function, swain-init appends the thin wrapper template directly — no migration needed. This is the existing Phase 4.5 flow.

### Doctor advisory

swain-doctor does **not** modify the user's rc file (that's swain-init's domain). However, if the `bin/swain` symlink exists but the shell function appears to be old-style (detected via `type swain 2>/dev/null` showing direct runtime invocation), doctor emits an advisory:

> **Advisory:** `swain` shell function appears to be old-style (direct runtime invocation). Run `/swain-init` to upgrade it to the thin wrapper that delegates to the project-root script.

## Scope & Constraints

- Must work in bash and zsh (the two shells swain-init supports)
- Must not break existing installations — the fallback path preserves current behavior exactly
- Migration is opt-in during swain-init; declining preserves the old function
- No crash detection, no debris cleanup, no session selection in the function — all that lives in the script
- The function is installed once by swain-init and rarely changes; the script is versioned with the project and evolves freely

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-28 | — | Initial creation from SPIKE-051 |
| Active | 2026-03-28 | — | Updated `./swain` references to `bin/swain` per ADR-019 operator-facing convention |
| Complete | 2026-03-30 | -- | 8/8 tests pass, thin wrapper + zsh templates, under 20 lines |
