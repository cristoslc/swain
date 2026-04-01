---
title: "Worktree-Relative Link Detection Script"
artifact: SPEC-216
track: implementable
status: Active
author: cristos
created: 2026-03-31
last-updated: 2026-03-31
priority-weight: high
type: bug
parent-epic: EPIC-051
parent-initiative: ""
linked-artifacts:
  - EPIC-051
  - DESIGN-007
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Worktree-Relative Link Detection Script

## Problem Statement

There is no tool to deterministically find relative path links in committed files that are specific to a worktree's location. Without detection, broken links land silently on trunk after a worktree merge.

## Desired Outcomes

Agents and operators can run a single script against any file set and get a clear list of suspicious links — no false negatives on the known failure modes, minimal false positives on clean repos.

## External Behavior

**Input:** A list of file paths (or a directory) and optionally the repo root and worktree root.

**Output:** For each suspicious link found, one line: `<file>:<line>: <link-text> -> <target> [REASON]`

Exit 0 if no suspicious links. Exit 1 if any found.

**Suspicious link categories (in priority order):**
1. **Absolute paths** — any link target starting with `/` that is not a standard system path (e.g., contains the repo root or a known worktree pattern like `/tmp/worktree-`, `.claude/worktrees/`)
2. **Symlinks with relative targets** that escape the repo root when resolved from the repo root (i.e., `readlink -f` on the symlink target from the repo root differs from `readlink -f` from the worktree root)
3. **Markdown relative links** where the resolved path does not exist when resolved from the repo root (walk `../` depth and check)

**File types scanned:**
- Markdown files (`*.md`) — extract `[text](target)` patterns
- Shell scripts (`*.sh`) — flag hardcoded absolute paths matching worktree patterns
- Symlinks — check relative target resolution from repo root

## Acceptance Criteria

- Given a markdown file with `[link](../../../outside-repo/file.md)`, when the script runs, then it reports the link as suspicious with reason `ESCAPES_REPO`
- Given a symlink `bin/foo -> ../../../../tmp/worktree-abc/scripts/foo.sh`, when the script runs, then it reports it as suspicious with reason `ABSOLUTE_ESCAPE`
- Given a shell file containing `/Users/cristos/.claude/worktrees/branch/scripts/foo.sh`, when the script runs, then it flags it with reason `HARDCODED_WORKTREE_PATH`
- Given a clean file set with only valid relative links, when the script runs, then exit 0 and no output
- Given no arguments, when the script runs, then it prints usage and exits 2
- The script accepts `--repo-root <path>` and `--worktree-root <path>` flags; both default to `$(git rev-parse --show-toplevel)`

## Reproduction Steps

1. Create a worktree at `.claude/worktrees/spec-216-test/`
2. In the worktree, add a markdown file with a link that uses `../` references that go past the repo root
3. Commit the file
4. On trunk, the link is broken — no existing tool catches this before merge

## Severity

medium

## Expected vs. Actual Behavior

**Expected:** A detection script flags worktree-specific relative links before they reach trunk.

**Actual:** No such script exists. Broken links reach trunk silently.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Detects ESCAPES_REPO | | |
| Detects ABSOLUTE_ESCAPE on symlinks | | |
| Detects HARDCODED_WORKTREE_PATH in scripts | | |
| Clean file set exits 0 | | |
| No-args prints usage, exits 2 | | |

## Scope & Constraints

- Script lives at `.agents/bin/detect-worktree-links.sh`
- Must be non-interactive (no prompts)
- Must run in under 5 seconds on a typical swain repo
- No external dependencies beyond git and standard POSIX tools

## Implementation Approach

1. Parse args (`--repo-root`, `--worktree-root`, positional file/dir list)
2. Walk each file: dispatch to the right scanner by file type
3. Markdown scanner: regex for `\[.*?\]\((.*?)\)`, check each target
4. Symlink scanner: `readlink` each symlink, test resolution from repo root
5. Script scanner: grep for patterns matching `/tmp/worktree`, `.claude/worktrees`, or the repo root absolute path
6. Collect findings, print in `file:line: target [REASON]` format, exit 0 or 1

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | — | Initial creation |
