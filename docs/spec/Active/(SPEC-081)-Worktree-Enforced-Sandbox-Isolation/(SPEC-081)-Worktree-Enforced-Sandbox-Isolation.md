---
title: "Worktree-Enforced Sandbox Isolation"
artifact: SPEC-081
track: implementable
status: Active
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
type: feature
parent-epic: ""
parent-initiative: INITIATIVE-013
parent-vision: VISION-002
linked-artifacts:
  - EPIC-036
  - EPIC-037
  - INITIATIVE-017
  - SPEC-067
  - SPEC-068
  - SPEC-071
  - SPEC-100
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Worktree-Enforced Sandbox Isolation

## Problem Statement

Worktrees are recommended but not enforced. An agent launched via `swain-box` or `claude-sandbox` runs in the project root on the main branch. In a multi-agent scenario, two agents writing to the same directory on the same branch will clobber each other's files. The sandbox launchers control what gets mounted — they can create and mount a per-agent worktree so that branch scoping and filesystem isolation are enforced mechanically, not by convention.

## External Behavior

### swain-box (Docker Sandboxes)

Before launching `docker sandbox run`, swain-box:

1. Creates a worktree at `.sandboxes/<sandbox-name>` on branch `agent/<sandbox-name>`:
   ```
   git worktree add .sandboxes/<sandbox-name> -b agent/<sandbox-name> 2>/dev/null || \
   git worktree add .sandboxes/<sandbox-name> agent/<sandbox-name>
   ```
2. Mounts the worktree path instead of the project root:
   ```
   exec docker sandbox run "$SELECTED_RUNTIME" "$WORKTREE_PATH" ...
   ```
3. The agent inside the VM sees only its worktree — it cannot write to main or another agent's worktree.

### claude-sandbox (native sandbox)

Before launching `claude --sandbox`, claude-sandbox:

1. Creates a worktree using the same pattern
2. `cd`s into the worktree
3. Launches `claude --sandbox` from there

### Opt-out

A `--no-worktree` flag on both launchers skips worktree creation and uses the project root directly (current behavior). This is for attended single-agent use where the operator wants to work on main.

### Cleanup

When the sandbox exits, the worktree is NOT automatically removed — the operator reviews and merges the agent's work via the normal PR/merge flow. A `swain-box --cleanup <sandbox-name>` command removes the worktree and branch after merge.

## Acceptance Criteria

- Given `swain-box /path/to/project` (no --no-worktree), when the sandbox launches, then the mounted directory is a worktree on branch `agent/<sandbox-name>`, not the project root
- Given `claude-sandbox` (no --no-worktree), when claude launches, then the working directory is a worktree on branch `agent/<name>`
- Given two concurrent `swain-box` invocations with different paths/names, then each gets a separate worktree and branch with no filesystem overlap
- Given `--no-worktree`, then current behavior is preserved (project root mounted directly)
- Given a worktree already exists for the sandbox name, then it is reused (not recreated)
- Given `swain-box --cleanup <name>`, then the worktree and branch are removed

## Scope & Constraints

- POSIX sh only (no bash)
- Worktree directory is `.sandboxes/` in the project root (gitignored)
- Branch naming: `agent/<sandbox-name>` — predictable and greppable
- Does not implement merge/PR workflow — that's the operator's responsibility
- Does not modify agent behavior inside the sandbox — just what directory they see

## Implementation Approach

1. Add worktree creation function shared between both launchers
2. Add `.sandboxes/` to `.gitignore` if not present
3. Modify swain-box to create worktree and mount it
4. Modify claude-sandbox to create worktree and cd into it
5. Add `--no-worktree` flag to both
6. Add `--cleanup` subcommand to swain-box

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | — | Mechanically enforces worktree isolation at sandbox boundary |
