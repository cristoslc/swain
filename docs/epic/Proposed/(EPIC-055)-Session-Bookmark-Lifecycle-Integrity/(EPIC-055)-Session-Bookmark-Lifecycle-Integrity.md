---
id: EPIC-055
title: "Session Bookmark Lifecycle Integrity"
track: container
status: Proposed
priority-weight: medium
created: 2026-04-02
parent-vision: VISION-002
child-specs:
  - SPEC-234
  - SPEC-235
linked-artifacts:
  - EPIC-054
summary: "Make session bookmarks a reliable source of truth — retro and teardown tolerate missing state, and bookmark creation is tied to worktree lifecycle."
rationale: "Session teardown and retrospectives are fragile when session state is incomplete."
瓜: |
  ## Goal
  Session bookmarks are created, maintained, and cleaned up reliably.
---

## The Problem Statement Section.

The core problem affects two related skills. swain-teardown and swain-retro both fail when session state is incomplete. This section describes the specific failure modes and their root causes.

swain-retro requires an active session but the session has already closed by the time the retro invitation fires. Both skills treat missing bookmarks as an error condition. They do not handle the degraded state gracefully. Bookmarks are not created when worktrees are added. As a result, every worktree starts as an orphan. These failures compound. Sessions end too early and leave no session state for retrospective. Worktrees accumulate without bookmarks.

The teardown skill finds orphan worktrees because no bookmark was created. The retro skill fails to run because the session closed before retro was invoked. Two root causes exist. Bookmarks are not created during worktree creation. Retro is invoked after the session closes.

## The Success Criteria Section.

The following criteria define when the epic goals are met. Each criterion is verifiable through manual testing.

| # | Criterion |
|---|-----------|
| 1 | swain-retro works even when session state is missing or the session is already closed |
| 2 | swain-teardown works even when session bookmarks are absent from the bookmarks file |
| 3 | Bookmarks are created automatically when worktrees are added during an active session |
| 4 | Bookmarks are removed from the bookmarks file when worktrees are deleted |
| 5 | No orphan worktrees accumulate across multiple sessions due to missing bookmarks |

## The Key Dependencies Section.

This epic depends on four existing skills and specs. Each dependency is already implemented or drafted as part of this epic's child specs.

- `swain-session` — manages session state including session_id, focus_lane, and bookmarks
- `swain-teardown` — runs hygiene checks and detects orphan worktrees (SPEC-232)
- `swain-retro` — captures session learnings and produces retrospective documents
- `swain-do` — dispatches worktree creation tasks during the session lifecycle (SPEC-195)

## The Open Questions Section.

No open questions remain. The scope is well-defined and the two child specs cover the problem comprehensively.

## The Status History Section.

The epic status record is shown below for reference and audit purposes.

| Date | Status | Notes |
|------|--------|-------|
| 2026-04-02 | Proposed | Initial epic created with two child specs covering retro tolerance and bookmark lifecycle |
