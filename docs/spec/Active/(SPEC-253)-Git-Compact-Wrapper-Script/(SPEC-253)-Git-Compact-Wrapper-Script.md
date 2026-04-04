---
title: "Git-Compact Wrapper Script"
artifact: SPEC-253
track: implementable
status: Active
author: Cristos L-C
created: 2026-04-03
last-updated: 2026-04-03
priority-weight: low
type: feature
parent-epic: ""
parent-initiative: INITIATIVE-002
linked-artifacts:
  - DESIGN-017
depends-on-artifacts: []
addresses: []
evidence-pool: "trove: rtk-cli-token-compression@c94bfc1"
source-issue: ""
swain-do: required
---

# Git-Compact Wrapper Script

## Problem Statement

Swain agents run many git commands during sessions — diff, log, status — that generate hundreds to thousands of tokens of output. Most of this output is boilerplate (per-file stat lines, context lines, branch metadata) that the agent does not need for its next decision. This wastes context window capacity and shortens effective session length.

RTK compresses git output by 75-94%, but its global PreToolUse hook would intercept all Bash commands, risking interference with swain's structured JSON outputs (chart.sh, session-greeting.sh, tk).

## Desired Outcomes

Agents get a compressed-output path for git commands that preserves session context capacity without any risk to swain's existing tooling. The mechanism is opt-in (agents call `git-compact` explicitly) and degrades transparently when RTK is not installed.

## External Behavior

### Input

```
.agents/bin/git-compact <subcommand> [args...]
```

Accepts any git subcommand with arguments.

### Output

- For routed subcommands (diff, log, status): RTK-compressed output when RTK is available, raw git output otherwise
- For all other subcommands: raw git output
- Exit code: passthrough from underlying command

### Routing table

| Subcommand | Compressed | Raw fallback |
|------------|-----------|-------------|
| `diff [args]` | `rtk git diff [args]` | `git diff [args]` |
| `log [args]` | `rtk git log [args]` | `git log [args]` |
| `status [args]` | `rtk git status [args]` | `git status [args]` |
| Everything else | n/a | `git <subcommand> [args]` |

## Acceptance Criteria

1. **Given** RTK is installed and on PATH, **when** `git-compact diff HEAD~1` is called, **then** output is RTK-compressed (shorter than raw `git diff HEAD~1` output)
2. **Given** RTK is NOT installed, **when** `git-compact diff HEAD~1` is called, **then** output is identical to `git diff HEAD~1`
3. **Given** RTK is installed, **when** `git-compact blame src/main.rs` is called, **then** output is identical to `git blame src/main.rs` (passthrough, no compression)
4. **Given** any invocation, **when** the underlying command exits non-zero, **then** `git-compact` exits with the same code
5. **Given** no arguments, **when** `git-compact` is called, **then** output is identical to bare `git` (help text)
6. The script is executable and located at `.agents/bin/git-compact`
7. The script is under 50 lines (simplicity constraint)

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1: RTK-compressed diff | Manual: compare output length of `git-compact diff` vs `git diff` with RTK installed | |
| AC2: Transparent fallback | Manual: rename rtk binary, verify `git-compact diff` matches `git diff` | |
| AC3: Passthrough for non-routed | Manual: `git-compact blame` matches `git blame` | |
| AC4: Exit code passthrough | Manual: `git-compact diff nonexistent; echo $?` matches `git diff nonexistent; echo $?` | |
| AC5: No-arg passthrough | Manual: `git-compact` matches `git` help output | |
| AC6: Location and permissions | `test -x .agents/bin/git-compact` | |
| AC7: Simplicity | `wc -l .agents/bin/git-compact` under 50 | |

## Scope & Constraints

- Single shell script, no dependencies beyond git and optionally RTK
- No configuration files, no state, no side effects
- Does not modify git config or install hooks
- RTK is an optional runtime dependency — the script works without it

## Implementation Approach

1. Write `.agents/bin/git-compact` as a bash script
2. Detect RTK: `command -v rtk >/dev/null 2>&1`
3. Route subcommand via case statement: diff|log|status -> rtk git, else -> git
4. Pass all arguments through verbatim
5. Run manual verification against all ACs

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-03 | -- | Initial creation |
