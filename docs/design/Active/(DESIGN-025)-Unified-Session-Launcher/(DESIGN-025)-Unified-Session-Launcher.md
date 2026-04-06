---
title: "Unified Session Launcher"
artifact: DESIGN-025
track: standing
domain: interaction
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
superseded-by: ""
linked-artifacts:
  - VISION-006
  - INITIATIVE-018
  - ADR-037
  - ADR-038
  - ADR-039
  - DESIGN-024
  - SPEC-180
  - SPEC-119
  - SPEC-245
artifact-refs: []
sourcecode-refs:
  - bin/swain
  - src/untethered/plugins/zulip_chat.py
  - src/untethered/bridges/project.py
depends-on-artifacts:
  - ADR-038
  - DESIGN-024
---

# Unified Session Launcher

## Design Intent

**Context:** There are two ways to start a session today: `bin/swain` from a terminal and natural language in the Zulip control topic. They follow different paths. The terminal launcher handles crash recovery, worktree creation, session purpose interview, and runtime selection. The Zulip path skips all of that and spawns a bare Claude Code session. This gap means the operator gets a degraded experience from chat.

### Goals

- A message in the Zulip control topic goes through the same session setup as `bin/swain`.
- The operator converses in the control topic to answer interview questions (what to work on, which worktree, resume or fresh). Only after the session purpose is set does a dedicated Zulip thread appear.
- The launcher logic runs once, in one place. Both entry points call the same code.

### Constraints

- `bin/swain` is a bash script (SPEC-180, ADR-018: structural logic lives in bash). It runs interactively in a terminal today.
- The Zulip chat adapter is a Python subprocess (ADR-038). It cannot run bash scripts interactively.
- Session state lives in `.agents/session-state.json` (SPEC-119). Both paths must write to it.
- Worktree creation requires git operations on the main checkout, not from inside a worktree.

### Non-goals

- Replacing `bin/swain` with Python. The launcher stays bash.
- Making the control topic a full terminal emulator.
- Automatic triage of queries vs work requests (separate concern, handled by the `control_message` command type).

## Problem

### Two launch paths, divergent behavior

| Capability | `bin/swain` (terminal) | Zulip control (today) |
|---|---|---|
| Crash recovery | Yes (Phase 1) | No |
| Worktree creation | Yes (Phase 2) | No |
| Session purpose interview | Yes (via `/swain-session`) | No |
| Runtime selection | Yes (`--runtime`) | Hardcoded to `claude` |
| Focus lane | Yes (from previous session) | No |
| Thread/topic creation | N/A (terminal) | Immediate (before purpose is set) |

### The thread-too-early problem

Today, `start_session` and `control_message` both create a session immediately. The Zulip chat adapter assigns a thread at `session_spawned` time. But the operator hasn't said what to work on yet. The thread gets a meaningless name like `sess-a1b2c3d4`.

The fix: delay thread creation until the session has a purpose (artifact binding).

## Proposed Design

### Two-phase session launch from control

**Phase 1: Interview (in control topic).** The control-origin session runs in the control topic. The operator and the session converse there. The session runs the same setup logic as `bin/swain`: crash recovery check, worktree selection, session purpose.

**Phase 2: Promote to thread.** When the session binds to an artifact (sets its purpose), the project bridge emits a `session_promoted` event. The chat adapter:
1. Removes the session from control-origin tracking.
2. Assigns a thread via `SessionTopicRegistry` (using the artifact name as topic).
3. Posts the announcement in control: "Session moved to topic **SPEC-142**."
4. All subsequent events for that session go to the dedicated thread.

### Launcher as a library

Extract the interview logic from `bin/swain` into a non-interactive mode that can be driven by NDJSON. The launcher accepts questions on stdin and emits answers on stdout.

```
bin/swain --non-interactive --format ndjson
```

The project bridge wraps this: it spawns `bin/swain --non-interactive` as a subprocess, relays the operator's control-topic messages as stdin, and reads launcher decisions from stdout. When the launcher completes (purpose set, worktree ready), the project bridge spawns the runtime adapter in the new worktree.

### Protocol additions

```
# New event type
session_promoted:
  session_id: str
  artifact: str
  topic: str  # suggested thread name

# New command type (already exists)
control_message:
  text: str  # operator's natural language from control topic
```

The `session_promoted` event triggers thread creation. It replaces the current behavior where `session_spawned` creates the thread.

### Sequence: Zulip control topic

```
Operator (control)      Chat Plugin       Kernel        Project Bridge      Launcher
    |                       |               |                |                 |
    |-- "What should I      |               |                |                 |
    |    work on?"          |               |                |                 |
    |                       |--control_msg-->|--control_msg-->|                 |
    |                       |               |                |--spawn launcher->|
    |                       |               |                |                 |
    |                       |<--text_output--|<--text_output--|<--"3 specs      |
    |<--post to control-----|               |                |   ready..."     |
    |                       |               |                |                 |
    |-- "Work on SPEC-142"  |               |                |                 |
    |                       |--control_msg-->|--control_msg-->|--stdin--------->|
    |                       |               |                |                 |
    |                       |               |                |<--purpose set----|
    |                       |               |                |--create worktree-|
    |                       |               |                |--spawn runtime-->|
    |                       |<--promoted-----|<--promoted-----|                 |
    |<--"Moved to SPEC-142"-|               |                |                 |
    |                       |               |                |                 |
    |   (now in SPEC-142    |               |                |                 |
    |    topic thread)      |               |                |                 |
```

### Sequence: Terminal (`bin/swain`)

No change. `bin/swain` continues to run interactively. The non-interactive mode is an addition, not a replacement.

## Migration

### Phase A (current state)

`control_message` spawns a session immediately. All output goes to control topic. No thread creation. No interview. This is the MVP committed today.

### Phase B (this design)

1. Add `--non-interactive --format ndjson` mode to `bin/swain`.
2. Project bridge spawns the launcher for `control_message` instead of directly spawning a runtime.
3. Add `session_promoted` event type to protocol.
4. Chat adapter delays thread creation until `session_promoted`.

### Phase C (future)

- Query triage: control-origin sessions that answer a question and die without binding an artifact never create a thread.
- Multi-project: control topic can route to different project bridges based on context.

## Decisions

1. **`--non-interactive` flag on `bin/swain`**, not a separate script. Keeps the control surface in sync between terminal and non-terminal interactions.
2. **NDJSON** for launcher-to-bridge communication. Consistent with the rest of the plugin protocol (DESIGN-024).
3. **No timeout.** Interview sessions persist in control until the operator cancels or completes them. The operator can leave and come back. This matches the Zulip model where topics are durable.

## Open Questions

None at this time.
