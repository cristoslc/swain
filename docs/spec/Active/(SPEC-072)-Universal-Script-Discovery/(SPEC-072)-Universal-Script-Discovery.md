---
title: "Universal find-based script discovery"
artifact: SPEC-072
track: implementable
status: Active
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
type: enhancement
parent-epic: EPIC-031
linked-artifacts:
  - INITIATIVE-001
  - SPEC-050
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Universal find-based script discovery

## Problem Statement

14+ swain skills hardcode script paths as `skills/swain-*/scripts/...` or `bash skills/swain-design/scripts/chart.sh`, assuming CWD is the project root. When an agent runs from a worktree (`.claude/worktrees/...`), these paths silently fail. Only swain-status and the bookmark/focus scripts use `find`-based discovery. This is the single largest class of bug in the audit (affects swain-design, swain-dispatch, swain-do, swain-doctor, swain-init, swain-retro, swain-search, swain-security-check, swain-session, swain-stage, swain-status, swain-sync).

## External Behavior

Every script invocation in every SKILL.md uses a discovery pattern that resolves from any working directory — main checkout, linked worktree, or subdirectory. The canonical pattern:

```bash
SCRIPT="$(find "$REPO_ROOT" -path '*/swain-<skill>/scripts/<script>' -print -quit 2>/dev/null)"
bash "$SCRIPT" <args>
```

Where `REPO_ROOT` is obtained via `git rev-parse --show-toplevel` (which returns the main repo root even from worktrees when using `--git-common-dir`).

Cross-skill script calls (e.g., swain-do calling `chart.sh` from swain-design) use the same pattern.

## Acceptance Criteria

**AC-1:** Given an agent in a linked worktree, when any swain skill invokes a script, then the script is found and executed successfully.

**AC-2:** Given an agent in the project root, when any swain skill invokes a script, then behavior is unchanged from current (no regression).

**AC-3:** Given a script that doesn't exist (e.g., optional cross-skill dependency), when discovery returns empty, then the skill logs a warning and degrades gracefully — no silent failure.

**AC-4:** No SKILL.md contains a bare `bash skills/...` invocation without `find`-based discovery or `$REPO_ROOT` prefix.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC-1 | grep all SKILL.md files for bare `skills/` paths | |
| AC-2 | Run swain-doctor from project root | |
| AC-3 | Review fallback handling in each skill | |
| AC-4 | grep -r "bash skills/" across all SKILL.md | |

## Scope & Constraints

**In scope:** All SKILL.md files with script invocations. Both `.claude/skills/` and `skills/` (hardlinked).

**Out of scope:** Changing the scripts themselves — only how SKILL.md references them. Does not change `swain-preflight.sh` (it already uses `$REPO_ROOT`).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | — | Created from audit theme #1: relative path fragility |
