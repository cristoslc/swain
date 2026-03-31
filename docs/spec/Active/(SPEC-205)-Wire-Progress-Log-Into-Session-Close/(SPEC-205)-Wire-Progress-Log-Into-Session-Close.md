---
title: "Wire Progress Log Into Session Close"
artifact: SPEC-205
track: implementable
status: Active
author: Cristos L-C
created: 2026-03-31
last-updated: 2026-03-31
priority-weight: high
type: bug
parent-epic: EPIC-049
parent-initiative: ""
linked-artifacts:
  - SPEC-199
  - SPEC-200
depends-on-artifacts:
  - SPEC-199
  - SPEC-200
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Wire Progress Log Into Session Close

## Problem Statement

[SPEC-199](../(SPEC-199)-Session-Digest-Auto-Generation/(SPEC-199)-Session-Digest-Auto-Generation.md) (session digest) and [SPEC-200](../(SPEC-200)-Progress-Log-and-Synthesis/(SPEC-200)-Progress-Log-and-Synthesis.md) (progress log) shipped scripts that pass unit tests but no skill calls them. The session close step runs `swain-session-state.sh close` and stops. No digest is made. No progress entries reach EPICs or Initiatives. The scripts are dead code.

[SPEC-200](../(SPEC-200)-Progress-Log-and-Synthesis/(SPEC-200)-Progress-Log-and-Synthesis.md) says "swain-retro reads artifacts_touched and appends a dated entry." But swain-retro runs at EPIC completion, not each session close. The right caller is swain-session's close step, where evidence is fresh.

## Desired Outcomes

When a session closes, the digest and progress log run on their own. EPICs and Initiatives gain progress entries with no operator action. The scripts get called, not rewritten.

## External Behavior

### Integration chain

At session close, after `swain-session-state.sh close`:

1. **swain-session** calls `swain-session-digest.sh` to write a JSONL entry to `.agents/session-log.jsonl`
2. **swain-session** calls `swain-progress-log.sh --digest <path>` with that entry — this adds dated notes to each EPIC/Initiative's `progress.md` and updates their `## Progress` sections

Both calls go in the skill file's close section. No new scripts needed.

### What changes

| File | Change |
|------|--------|
| `skills/swain-session/SKILL.md` | Add digest + progress-log calls after `swain-session-state.sh close` in the session close section |

### What does NOT change

- `swain-progress-log.sh` — already works
- `swain-session-digest.sh` — already works
- `swain-retro` — not the right caller for per-session progress; retro stays focused on EPIC completion
- No new scripts, no new dependencies

## Acceptance Criteria

1. **Given** commits touched [EPIC-049](../../../epic/Active/(EPIC-049)-Context-Rich-Progress-Tracking/(EPIC-049)-Context-Rich-Progress-Tracking.md), **when** session closes, **then** a JSONL entry appears in `.agents/session-log.jsonl`.

2. **Given** the JSONL entry names [EPIC-049](../../../epic/Active/(EPIC-049)-Context-Rich-Progress-Tracking/(EPIC-049)-Context-Rich-Progress-Tracking.md), **when** digest mode runs, **then** a dated entry exists in that EPIC's `progress.md`.

3. **Given** progress.md was updated, **when** synthesis runs, **then** the EPIC's `## Progress` section is current.

4. **Given** no artifacts changed, **when** session closes, **then** the digest still runs without error.

5. **Given** the session close section in swain-session SKILL.md, **when** an agent reads it, **then** the digest and progress-log calls are spelled out (not implied).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- In scope: update swain-session SKILL.md close steps
- Out of scope: script changes, new scripts, swain-retro
- This is a small skill file edit (< 10 lines added) on a key workflow path
- Skill change rules apply: use worktree isolation

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | _pending_ | Initial creation |
