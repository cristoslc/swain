---
title: "swain-box: Agent Runtime Detection & Selection Menu"
artifact: SPEC-068
track: implementable
status: Proposed
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
type: feature
parent-epic: EPIC-030
parent-initiative: ""
linked-artifacts:
  - SPEC-067
  - DESIGN-002
depends-on-artifacts:
  - SPEC-067
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# swain-box: Agent Runtime Detection & Selection Menu

## Problem Statement

swain-box unconditionally runs `docker sandbox run claude`. Operators who have Copilot or Codex sandbox images installed cannot select an alternative without forking the script. The selection should be automatic when only one runtime is available, and interactive otherwise.

## External Behavior

### Runtime detection

On startup (before credential handling), swain-box probes for each known runtime name in the Docker Sandboxes registry:

```
KNOWN_RUNTIMES="claude copilot codex"
```

For each name, probe availability:
```sh
docker sandbox run <name> --version >/dev/null 2>&1
```
Collect the names that exit 0 into `AVAILABLE_RUNTIMES`.

### Selection logic

- **0 runtimes detected**: exit with error — "No supported agent runtimes found in Docker Sandboxes. Ensure at least one of: claude, copilot, codex is installed."
- **1 runtime detected**: auto-select it, print `swain-box: using <name>` to stderr, proceed.
- **2+ runtimes detected**: present a numbered selection menu to stdout (not stderr — must be interactive):

```
swain-box: Multiple agent runtimes available. Select one:
  1) claude
  2) copilot
  3) codex
Choice [1]: _
```

Default is 1 (first detected). Invalid input re-prompts once, then exits non-zero.

The selected runtime name is stored in `SELECTED_RUNTIME` for downstream use in the launch command.

### Launch command

Replace the hardcoded `claude` in the exec call with `$SELECTED_RUNTIME`:
```sh
exec docker sandbox run "$SELECTED_RUNTIME" "$ABSOLUTE_PATH" [flags]
```

### Non-interactive mode

When stdin is not a TTY (e.g., CI or script invocation), the selection menu is suppressed. If multiple runtimes are detected in non-interactive mode, swain-box selects the first available runtime and prints a warning to stderr:
```
swain-box: WARNING: multiple runtimes available; auto-selected <name> (non-interactive mode). Use --runtime=<name> to specify.
```

### `--runtime=<name>` flag

Add a `--runtime=<name>` flag to bypass detection and selection entirely:
```
./swain-box --runtime=claude /path/to/project
```
If the specified runtime is not in `AVAILABLE_RUNTIMES`, exit with error.

## Acceptance Criteria

**AC-1: No runtimes available**
- Given no known runtime images are installed in Docker Sandboxes
- When swain-box is invoked
- Then it exits non-zero with an actionable error listing the supported runtime names

**AC-2: Single runtime auto-selected**
- Given exactly one known runtime is available
- When swain-box is invoked without `--runtime`
- Then it proceeds without prompting and prints the selected runtime name to stderr

**AC-3: Multi-runtime selection menu**
- Given two or more known runtimes are available and stdin is a TTY
- When swain-box is invoked without `--runtime`
- Then a numbered menu is printed and the user can select a runtime by number

**AC-4: Default selection**
- Given the selection menu is shown
- When the user presses Enter without typing a number
- Then runtime 1 (the first detected) is selected

**AC-5: Invalid input re-prompt**
- Given the selection menu is shown
- When the user enters a non-numeric or out-of-range value
- Then the menu re-prompts once, then exits non-zero on second failure

**AC-6: Non-interactive auto-select**
- Given multiple runtimes are available and stdin is not a TTY
- When swain-box is invoked
- Then the first runtime is selected automatically with a warning to stderr

**AC-7: `--runtime` flag bypasses detection**
- Given `--runtime=copilot` is passed
- When copilot is in the available runtimes
- Then the menu is skipped and copilot is used

**AC-8: `--runtime` flag validates availability**
- Given `--runtime=codex` is passed
- When codex is not available in Docker Sandboxes
- Then swain-box exits non-zero with a clear error

**AC-9: Downstream launch uses selected runtime**
- Given a runtime is selected (by any path)
- When the docker sandbox exec fires
- Then `docker sandbox run $SELECTED_RUNTIME <path>` is called (not hardcoded `claude`)

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC-1 through AC-9 | test-swain-box-selection.sh | — |

## Scope & Constraints

**In scope:** Detection loop, menu UX, `--runtime` flag, non-interactive fallback.
**Out of scope:** Per-runtime credential handling (SPEC-069, SPEC-070 own those). Detection does not reach into sandbox image internals — only probes `--version` availability.

**Constraints:**
- POSIX sh only (no bash arrays, no `select` builtin) — swain-box targets `/bin/sh`
- Menu output goes to stdout so terminal interaction works; status/warnings go to stderr
- Detection probe must complete in <2s total (parallel probing acceptable)

## Implementation Approach

TDD cycles:
1. Mock `docker` binary → test detection returns correct `AVAILABLE_RUNTIMES` list
2. Test menu rendering and numeric input parsing with simulated TTY
3. Test non-interactive auto-select path with `stdin=/dev/null`
4. Test `--runtime` validation against mock available list
5. Integration: test full exec path with each selection method

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-18 | — | Initial creation; detection + selection UX for EPIC-030 |
