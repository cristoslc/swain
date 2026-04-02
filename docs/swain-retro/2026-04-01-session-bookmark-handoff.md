---
title: "Retro: Session Bookmark Handoff"
artifact: RETRO-2026-04-01-session-bookmark-handoff
track: standing
status: Active
created: 2026-04-01
last-updated: 2026-04-01
scope: "launcher and session-start bookmark ownership"
period: "2026-04-01"
linked-artifacts:
  - INITIATIVE-013
  - EPIC-016
---

# Retro: Session Bookmark Handoff

## Summary

New sessions started from trunk could overwrite the trunk bookmark before a worktree was created. That broke the basic safety rule behind concurrent session work: shared state should stay with the checkout that owns the work. The fix moved session-purpose handoff behind worktree creation and taught worktree starts to respect an existing bookmark instead of silently replacing it.

## Reflection

### What went well

The bug was clear once the launch path was traced from the shell wrapper into `skills/swain/scripts/swain`. The real problem was not in bookmark writing itself. It was in when the prompt and checkout were chosen.

The repair stayed narrow. The launcher now picks the checkout first, then hands off the session purpose. Template launchers now prefer `bin/swain`, so one fix covers the supported runtimes instead of leaving each wrapper to drift.

The regression tests covered the risky cases directly. One test proves a fresh purpose from trunk launches inside a new worktree and leaves the trunk bookmark alone. Another proves a worktree with an existing bookmark is treated as active context, not free space.

### What was surprising

The direct bug lived in the pre-runtime script, but the generated launcher templates were also part of the failure path. They could bypass the script and inject `Session purpose` straight into the runtime. Fixing only `bin/swain` would have left a second entry point open.

The release surface was broader than the code surface. The session skill text also needed to say that bookmark ownership belongs to the checkout chosen by the launcher. Without that, the next refactor could reintroduce the same bug from prose drift alone.

### What would change

Launcher templates should default to the canonical entry point earlier in the design. A wrapper that can bypass the main runtime script is a maintenance liability. The more copies of the startup contract that exist, the more likely they are to drift.

Concurrent-session bugs deserve tests at the launcher boundary, not only in the lower-level scripts. The failure happened before the session skill started, so the most valuable test lived at that boundary too.

### Patterns observed

This is another case where worktree safety failed at a handoff boundary. The low-level script did what it was told, but the caller chose the wrong context first. Swain's isolation bugs keep clustering around these transition points: trunk to worktree, wrapper to canonical script, plan to execution.

The safest repair path was to collapse entry points rather than add more rules. Pointing runtime templates at `bin/swain` reduced behavioral duplication and made the fix harder to bypass.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| Checkout choice must happen before session-purpose handoff | Process | Shared session state belongs to the checkout that will own the work, not the checkout that launched the runtime |
| Wrapper scripts should prefer the canonical launcher | Process | Startup contract duplication makes concurrent-session bugs easier to reintroduce |
| Concurrency tests belong at handoff boundaries | Testing | The most valuable regression checks were in the pre-runtime launcher, not only in session helpers |

## SPEC candidates

None. The concrete bug and the obvious drift path were both fixed in this session.
