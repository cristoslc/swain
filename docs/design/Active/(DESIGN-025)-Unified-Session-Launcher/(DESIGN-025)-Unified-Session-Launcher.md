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

### Runtime in tmux — the "untethered" model

The runtime (claude, opencode, etc.) does NOT run as a subprocess of the project bridge. It runs in a **tmux session** that is independent of any chat surface. This is the core "untethered" concept:

- The chat adapter relays messages to/from the tmux pane via `tmux send-keys` and `tmux capture-pane`.
- The operator can also `tmux attach` and interact with the runtime directly in a terminal.
- Multiple surfaces (Zulip, local terminal) can connect to the same running session.
- If the bridge crashes, the runtime keeps running. The operator can still attach locally.
- If the operator disconnects from Zulip, the runtime keeps running. They can come back later.

This means the project bridge's role is:
1. **Launch**: Create a tmux session, run `bin/swain` (or the runtime directly) inside it.
2. **Relay inbound**: Translate chat commands into `tmux send-keys` to the pane.
3. **Relay outbound**: Periodically `tmux capture-pane` (or tail a log) to detect new output and emit events.
4. **Lifecycle**: Detect when the tmux pane exits (session died).

The runtime adapter is NOT a subprocess pipe adapter. It is a **tmux pane adapter**.

### Sequence: Zulip control topic

```
Operator (control)      Chat Plugin       Kernel        Project Bridge      tmux pane
    |                       |               |                |                 |
    |-- "What should I      |               |                |                 |
    |    work on?"          |               |                |                 |
    |                       |--control_msg-->|--control_msg-->|                 |
    |                       |               |                |--spawn launcher->|
    |                       |               |                |                 |
    |                       |<--text_output--|<--text_output--|<--capture-pane---|
    |<--post to control-----|               |                |                 |
    |                       |               |                |                 |
    |-- "Work on SPEC-142"  |               |                |                 |
    |                       |--control_msg-->|--control_msg-->|--send-keys----->|
    |                       |               |                |                 |
    |                       |               |                |<--capture-pane---|
    |                       |               |                |--create worktree-|
    |                       |<--promoted-----|<--promoted-----|                 |
    |<--"Moved to SPEC-142"-|               |                |                 |
    |                       |               |                |                 |
    |   (now in SPEC-142    |               |                |                 |
    |    topic thread)      |  Operator attaches locally:    |                 |
    |                       |  tmux attach -t swain-spec142  |                 |
    |                       |               |                |                 |
```

### Sequence: Terminal (`bin/swain`)

No change to the operator's experience. `bin/swain` creates the tmux session and launches the runtime inside it. The operator interacts directly. The project bridge (if running) detects the tmux session and begins relaying events to Zulip.

### Outbound relay strategies

The project bridge needs to detect runtime output without owning the process. Options:

1. **Periodic `tmux capture-pane` diff.** Poll the pane contents, diff against last capture, emit new lines as `text_output` events. Simple but lossy for fast output.
2. **Runtime log tailing.** If the runtime writes a log file (e.g., Claude Code's `~/.claude/projects/.../session.jsonl`), tail the log and translate entries to events. More reliable, runtime-specific.
3. **Shared pipe.** `bin/swain` runs the runtime with `script` or `tee` to duplicate output to a pipe that the project bridge reads. Universal but adds complexity.

Strategy 2 (log tailing) is preferred where available. Strategy 1 (capture-pane) is the universal fallback.

### Inbound relay

The project bridge translates commands to tmux input:

- `send_prompt` → `tmux send-keys -t <pane> "the prompt text" Enter`
- `approve` → `tmux send-keys -t <pane> "y" Enter` (or the appropriate key sequence)
- `cancel` → `tmux send-keys -t <pane> C-c` (SIGINT)

For runtimes with structured input (Claude Code `--input-format stream-json`), the bridge could write to a named pipe instead.

## Migration

### Phase A (current state)

`control_message` spawns a mock response. `/work` triggers the launcher NDJSON flow. `session_promoted` creates threads. All tested but runtime is not in tmux.

### Phase B (tmux adapter)

1. Replace `ClaudeCodeAdapter` / `OpenCodeAdapter` subprocess model with `TmuxPaneAdapter`.
2. `TmuxPaneAdapter.start()` creates a tmux session and runs the runtime inside it.
3. `TmuxPaneAdapter` polls `capture-pane` for output, emits events.
4. `TmuxPaneAdapter` translates commands to `send-keys`.
5. `bin/swain` (terminal path) continues to create tmux sessions as before — the bridge can adopt them.

### Phase C (future)

- Query triage: control-origin sessions that answer a question and die without binding an artifact never create a thread.
- Multi-project: control topic can route to different project bridges based on context.
- Session adoption: bridge discovers existing tmux sessions (from `bin/swain` terminal launches) and begins relaying.

## Decisions

1. **`--non-interactive` flag on `bin/swain`**, not a separate script. Keeps the control surface in sync between terminal and non-terminal interactions.
2. **NDJSON** for launcher-to-bridge communication. Consistent with the rest of the plugin protocol (DESIGN-024).
3. **No timeout.** Interview sessions persist in control until the operator cancels or completes them. The operator can leave and come back. This matches the Zulip model where topics are durable.
4. **Runtime in tmux, not subprocess pipes.** The runtime is untethered from the bridge process. The operator can attach locally. The chat adapter relays via tmux.

## Open Questions

1. Which outbound relay strategy to use for the MVP? `capture-pane` polling is universal but lossy. Log tailing is reliable but runtime-specific.
2. How does `approve` translate to tmux input for different runtimes? Claude Code has `--input-format stream-json` but others may need literal keystrokes.
3. How frequently should `capture-pane` poll? Too fast wastes CPU, too slow misses rapid output.
