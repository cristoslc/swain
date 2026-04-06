---
title: "Non-Interactive Launcher Mode"
artifact: SPEC-291
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
parent-initiative: INITIATIVE-018
linked-artifacts:
  - DESIGN-025
  - ADR-038
  - SPEC-180
  - SPEC-119
depends-on-artifacts:
  - DESIGN-025
sourcecode-refs:
  - bin/swain
  - src/untethered/protocol.py
  - src/untethered/bridges/project.py
  - src/untethered/plugins/zulip_chat.py
---

# Non-Interactive Launcher Mode

## Summary

Add `--non-interactive --format ndjson` mode to `bin/swain` so the Zulip control topic can drive the same session interview flow as the terminal. The project bridge spawns the launcher, relays operator messages, and promotes the session to a dedicated Zulip thread when the purpose is set.

## Acceptance Criteria

1. `bin/swain --non-interactive --format ndjson` reads NDJSON from stdin and writes NDJSON to stdout instead of using tty prompts.
2. The launcher emits structured messages: `{"type":"question","text":"..."}` when it needs operator input, `{"type":"ready","purpose":"...","worktree":"...","runtime":"..."}` when setup is complete.
3. Protocol includes `session_promoted` event with `artifact` and `topic` fields.
4. `_cmd_control_message` in project bridge spawns `bin/swain --non-interactive --format ndjson` as a subprocess, relays operator control-topic messages as `{"type":"answer","text":"..."}` on its stdin, and reads launcher output from stdout.
5. When the launcher emits `ready`, the project bridge spawns the runtime adapter in the launcher's worktree and emits `session_promoted`.
6. The Zulip chat plugin creates a dedicated thread only on `session_promoted`, not on `session_spawned` for control-origin sessions.
7. Control-origin session output (from the interview phase) posts to the control topic.
8. After promotion, all session output posts to the dedicated thread.
9. Sessions without promotion (queries answered during interview) stay in control and clean up silently on death.

## Out of Scope

- Query triage (auto-detecting questions vs work requests).
- Crash debris cleanup in non-interactive mode (Phase 1 skipped — no tty for confirmations).
- Multi-project routing from control topic.
