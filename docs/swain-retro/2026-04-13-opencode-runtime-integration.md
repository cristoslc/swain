---
title: "Retro: opencode runtime integration"
artifact: RETRO-2026-04-13-opencode-runtime-integration
track: standing
status: Active
created: 2026-04-13
last-updated: 2026-04-13
scope: "opencode runtime support in bin/swain — crash fix, headless→TUI session chaining"
period: "2026-04-13"
linked-artifacts:
  - EPIC-045
  - EPIC-048
---

# Retro: opencode runtime integration

## Summary

Fixed a crash in `bin/swain` when launching with `--runtime opencode` (invalid `--yolo`
flag), then extended the integration to deliver the initial swain prompt via a headless
session before resuming in the TUI. The session ID is captured from the first JSON event
of `opencode run --format json`, which avoids any race condition with `opencode session
list`.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| `bin/swain` | opencode launch fix | Shipped on trunk |
| Research | opencode session chaining | Confirmed via web search + live test |

## Reflection

### What went well

- Diagnosis was immediate — one read of `build_launch_cmd` surfaced `--yolo` as the
  invalid flag.
- Web research before implementing paid off. Knowing the session ID appears in the very
  first JSON event (even on error responses) made Option A obviously correct and safe.
- The `--dry-run` smoke test gave full confidence: the output showed a real session ID in
  the resolved command string, not a placeholder.
- Direction changes were low-friction. Each iteration was small and verifiable.

### What was surprising

- The `--yolo` flag was cargo-culted from other runtimes (`copilot`, `crush`) without
  opencode having it. A simple typo in the feature commit caused a silent crash at launch
  time — the tmux pane closes with no output.
- The session ID appears in the first JSON event regardless of whether the model call
  succeeds or errors. The parse is robust across all opencode outcomes, not just happy
  path.
- opencode has no hook system at all. There is no equivalent to Claude Code's pre-tool
  or post-stop hooks, which means swain's lifecycle signals (lockfile, session close) have
  no native attachment point in opencode.

### What would change

- The intermediate `_swain_opencode_launch` helper function was a false start. It looked
  clean in isolation but broke the `tmux new-session` path because bash functions don't
  survive shell boundaries (and the user's default shell is zsh, so `export -f` was not
  an option). Earlier recognition of this constraint would have saved one design iteration.
- The quoting-hell detour with `bash -c '...'` inlining was a signal that the abstraction
  was wrong — that signal should have triggered a redesign sooner rather than an attempt
  to fix the escaping.

### Patterns observed

- `build_launch_cmd` returns a command string that is safe for `eval` and `tmux
  new-session`. This contract works for single-command runtimes but is the wrong
  abstraction for multi-step launches (headless init → TUI resume). The right fix was to
  run the headless step *before* the tmux branching, in the current process, so the result
  is a plain string by the time tmux sees it.
- This pattern will recur for any future runtime that needs an init-then-interactive
  sequence. The current solution (an early opencode block in `phase3_launch_runtime`) is
  a one-off; a more general "pre-launch hook" slot in the phase 3 flow would handle it
  without special-casing.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| `build_launch_cmd` string contract breaks for multi-step runtimes | SPEC candidate | A pre-launch hook slot in `phase3_launch_runtime` would generalize opencode's pattern |
| New runtime additions should be smoke-tested with `--dry-run` before merging | SPEC candidate | Add `--dry-run` assertions to swain-test's runtime coverage |
| opencode has no hook system | Memory | Documented in session; swain lifecycle signals can't attach to opencode natively |
