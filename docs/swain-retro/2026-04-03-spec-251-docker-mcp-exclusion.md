---
title: "Retro: SPEC-251 Docker MCP Exclusion Bug Fix"
artifact: RETRO-2026-04-03-spec-251-docker-mcp-exclusion
track: standing
status: Active
created: 2026-04-03
last-updated: 2026-04-03
scope: "Bug fix for false-positive Docker MCP gateway detection in crash debris checks"
period: "2026-04-03"
linked-artifacts:
  - SPEC-251
  - SPEC-182
  - EPIC-046
---

# Retro: SPEC-251 Docker MCP Exclusion Bug Fix

## Summary

Fixed a false-positive in `check_orphaned_mcp()` where Docker MCP gateway containers were flagged as crash debris. The fix added a `grep -iv 'docker\|containerd'` filter to the process-matching pipeline. Single session, single commit.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| SPEC-251 | Exclude Docker MCP Gateway from Crash Debris Detection | Fix committed, pending merge |

## Reflection

### What went well

- Bug identification was fast — the operator already knew the root cause and the exact line.
- The fix was minimal (one grep filter added to a pipeline), low risk, and easy to verify.
- TDD cycle was clean: 4 RED tests written, fix applied, all GREEN.

### What was surprising

- The Edit tool wrote to the trunk copy of `tests/test_crash_debris.sh` instead of the worktree copy. This caused the new tests to silently not appear in test output. Root cause: the Edit tool resolved the file path to the trunk repo, not the worktree's working directory. The fix was to use absolute worktree paths (`/Users/cristos/Documents/code/swain/.claude/worktrees/spec-251-docker-mcp-exclusion/...`) for all Edit calls.
- `set -uo pipefail` in the test file caused grep failures (no match = non-zero exit) to silently abort entire test sections. The initial mock-ps approach using heredocs and function definitions was incompatible with strict mode. Simplified to source-inspection tests that worked cleanly.

### What would change

- Use absolute worktree paths from the start for all file operations, not relative paths that resolve to trunk.
- Avoid complex test scaffolding (mock executables, PATH overrides) in bash test files with `set -uo pipefail` — keep tests simple and direct.

### Patterns observed

- Worktree path resolution is a recurring friction point. The Edit/Read tools don't always resolve to the worktree's copy of a file. This has been seen before in prior sessions.

## SPEC candidates

1. **Edit tool worktree path awareness** — investigate whether the Edit/Read tools can be made worktree-aware, or document the absolute-path requirement as a convention in AGENTS.md.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| Worktree path resolution friction | pattern (recurring) | Edit/Read tools may resolve to trunk — always use absolute worktree paths |
| Strict-mode bash test compatibility | pattern | Avoid mock-executable scaffolding in `set -uo pipefail` test files |
