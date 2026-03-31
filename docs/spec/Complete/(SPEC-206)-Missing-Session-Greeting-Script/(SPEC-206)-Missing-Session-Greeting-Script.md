---
title: "Missing session greeting script"
artifact: SPEC-206
track: implementable
status: Complete
author: operator
created: 2026-03-31
last-updated: 2026-03-31T13:22:00Z
priority-weight: ""
type: bug
parent-epic: ""
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Missing session greeting script

## Problem Statement

The swain-session skill references `swain-session-greeting.sh` as its Step 1 fast greeting mechanism, but the script does not exist in `.agents/bin/` or `skills/swain-session/scripts/`. Session startup falls back to multiple sequential manual calls instead of a single fast-path invocation.

## Desired Outcomes

Session startup completes in a single script call (~500ms), returning structured JSON with branch, dirty state, bookmark, focus lane, tab name, and preflight warnings. Operators get a consistent, fast greeting regardless of which agent runtime hosts swain.

## External Behavior

**Input:** `swain-session-greeting.sh [--json] [--path <dir>]`

**Output (JSON mode):**
```json
{
  "greeting": true,
  "branch": "trunk",
  "dirty": false,
  "isolated": false,
  "bookmark": "Left off implementing the bootstrap script",
  "focus": "VISION-001",
  "tab": "project @ branch",
  "warnings": []
}
```

**Preconditions:** git available, `.agents/session.json` may or may not exist.

**Postconditions:** Tab name set via `swain-tab-name.sh`. JSON emitted to stdout.

## Acceptance Criteria

1. Given `.agents/bin/swain-session-greeting.sh` exists and is executable, when invoked with `--json`, then it exits 0 and emits valid JSON with all required keys (`greeting`, `branch`, `dirty`, `isolated`, `bookmark`, `focus`, `tab`, `warnings`).
2. Given a dirty working tree, when the script runs, then `dirty` is `true`.
3. Given a session bookmark exists in `session.json`, when the script runs, then `bookmark` contains the note text.
4. Given a focus lane is set, when the script runs, then `focus` contains the artifact ID.
5. Given the script is run inside a worktree, when the script runs, then `isolated` is `true`.
6. Given `--path <dir>` is passed, when the script runs, then branch and tab name reflect that directory's git state.

## Reproduction Steps

1. Start a new swain session (`/swain-session`)
2. The skill invokes `bash "$REPO_ROOT/.agents/bin/swain-session-greeting.sh" --json`
3. Bash returns exit code 127: `No such file or directory`
4. Session falls back to multiple individual script calls

## Severity

medium

## Expected vs. Actual Behavior

**Expected:** `swain-session-greeting.sh` exists, runs, and returns structured JSON for the session greeting.

**Actual:** Script does not exist. Session startup requires 4-5 separate tool calls to gather the same information.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1: Script exists, exits 0, emits valid JSON with all keys | `test-session-greeting.sh` tests 0a, 2 | Pass |
| AC2: Dirty working tree → `dirty: true` | `test-session-greeting.sh` test 7 | Pass |
| AC3: Bookmark in session.json → `bookmark` populated | `test-session-greeting.sh` test 3 | Pass |
| AC4: Focus lane set → `focus` populated | `test-session-greeting.sh` test 4 | Pass |
| AC5: Worktree → `isolated: true` | Script logic lines 46-48; verified in-session | Pass |
| AC6: `--path` → branch/tab reflect that dir | Script arg parsing lines 33-34; manual verification | Pass |

## Scope & Constraints

- The script consolidates calls already made by the swain-session skill (tab name, focus, bookmark, branch, dirty state). No new data sources.
- Must not call specgraph, GitHub API, or the full status dashboard — fast path only.
- Should symlink into `.agents/bin/` from `skills/swain-session/scripts/`.

## Implementation Approach

1. Create `skills/swain-session/scripts/swain-session-greeting.sh` that:
   - Reads git branch and dirty state
   - Reads `.agents/session.json` for bookmark and focus lane (via jq)
   - Calls `swain-tab-name.sh` for tab naming
   - Detects worktree via `git rev-parse --show-toplevel` comparison
   - Emits JSON to stdout
2. Symlink into `.agents/bin/`
3. Test each AC

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | — | Initial creation |
| Complete | 2026-03-31 | af41336 | Symlinks added, doctor check, test coverage |
