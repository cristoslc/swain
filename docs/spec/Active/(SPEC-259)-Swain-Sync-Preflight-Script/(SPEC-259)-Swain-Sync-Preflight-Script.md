---
title: "Swain-Sync Preflight Script"
artifact: SPEC-259
track: implementable
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
priority-weight: medium
type: enhancement
parent-epic: ""
parent-initiative: ""
linked-artifacts:
  - SPEC-121
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Swain-Sync Preflight Script

## Problem Statement

swain-sync delegates all work to a subagent, but Steps 1–3.9 are purely mechanical bash — worktree detection, fetch/rebase, staging, gitignore checks, ADR compliance, design drift, collision detection. The subagent currently executes these as 15–20 sequential tool calls, each with round-trip overhead. This wastes tokens and wall-clock time on deterministic work that needs no LLM judgment.

## Desired Outcomes

The subagent receives a structured preflight summary and only needs to: read the staged diff, generate a commit message, commit, and push. Tool calls drop from ~20 to ~5. Sync operations complete faster with less token spend.

## External Behavior

A new script `skills/swain-sync/bin/swain-sync-preflight.sh` runs Steps 1–3.9 of the current swain-sync skill and emits a JSON summary to stdout.

**Input:** None (reads git state from the current working directory).

**Output (stdout):** JSON object with the following shape:

```json
{
  "status": "ready|blocked|clean",
  "in_worktree": true,
  "repo_root": "/path/to/repo",
  "trunk": "trunk",
  "branch": "worktree-foo",
  "upstream": "origin/worktree-foo",
  "staged_files": ["a.md", "b.py"],
  "secrets_excluded": [".env"],
  "warnings": [
    "ADR compliance: 1 artifact with advisory findings",
    "Design drift: DESIGN-003 has stale sourcecode-refs"
  ],
  "blockers": [
    "Gitignore missing patterns: .env, node_modules/"
  ]
}
```

**Exit codes:**
- `0` — `status: ready` or `status: clean`
- `1` — `status: blocked` (blockers array is non-empty)
- `2` — unrecoverable error (merge conflict, fetch failure requiring operator intervention)

**Postconditions:**
- When `status: ready`, all files are staged and checks have passed. The subagent can proceed directly to commit message generation.
- When `status: blocked`, nothing is committed. The `blockers` array describes what the operator must fix.
- When `status: clean`, the working tree has no changes and nothing was pushed. The subagent can skip the rest of the workflow.

**Symlink:** `swain-init` and `swain-doctor` create `.agents/bin/swain-sync-preflight.sh` → `skills/swain-sync/bin/swain-sync-preflight.sh`.

## Acceptance Criteria

1. **Given** a dirty working tree with no blockers, **when** `swain-sync-preflight.sh` runs, **then** it exits 0 with `status: ready`, all non-secret files are staged, and `staged_files` lists them.

2. **Given** a clean working tree, **when** `swain-sync-preflight.sh` runs, **then** it exits 0 with `status: clean` and an empty `staged_files` array.

3. **Given** a repo missing `.gitignore` or missing relevant patterns, **when** `swain-sync-preflight.sh` runs, **then** it exits 1 with `status: blocked` and `blockers` describes the missing patterns.

4. **Given** artifact number collisions exist, **when** `swain-sync-preflight.sh` runs, **then** it exits 1 with `status: blocked` and `blockers` describes the collision.

5. **Given** a worktree context with upstream changes, **when** `swain-sync-preflight.sh` runs, **then** it fetches and merges `origin/$TRUNK` before staging.

6. **Given** a merge conflict during fetch/merge, **when** `swain-sync-preflight.sh` runs, **then** it aborts the merge, exits 2, and reports the conflicting files in stderr.

7. **Given** secret-like files are present (`.env`, `*.pem`, etc.), **when** `swain-sync-preflight.sh` runs, **then** they are excluded from staging and listed in `secrets_excluded`.

8. **Given** ADR compliance or design drift findings exist, **when** `swain-sync-preflight.sh` runs, **then** they appear in `warnings` but do not block (exit 0, `status: ready`).

9. **Given** the script completes, **when** the subagent reads its output, **then** the subagent can generate a commit message and commit without running any preflight bash commands itself.

10. **Given** `swain-init` or `swain-doctor` runs, **then** a symlink `.agents/bin/swain-sync-preflight.sh` pointing to `skills/swain-sync/bin/swain-sync-preflight.sh` exists and is executable.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- The script must be POSIX-compatible (bash, not zsh-specific).
- The script sources no skill files — it is self-contained.
- Advisory checks (ADR compliance, design drift, README reconciliation) that depend on scripts in `.agents/bin/` should degrade gracefully if those scripts are missing.
- The swain-sync SKILL.md must be updated to call the preflight script and consume its JSON output, replacing the inline Steps 1–3.9.
- The `swain-sync-preflight.sh` skip logic for `# swain-sync: allow <pattern>` in `.gitignore` must match the current SKILL.md behavior exactly.

## Implementation Approach

1. Write `skills/swain-sync/bin/swain-sync-preflight.sh` implementing Steps 1–3.9 as a single script with JSON output.
2. Update `swain-init` and `swain-doctor` symlink manifests to include the new script.
3. Update `skills/swain-sync/SKILL.md` to call the preflight script at the start and branch on its exit code / status field, replacing the inline bash blocks for Steps 1–3.9.
4. Test each AC.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | — | Initial creation |
