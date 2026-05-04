# hcom Source Code Snapshot

**Repository**: https://github.com/aannoo/hcom  
**Version**: 0.7.12  
**License**: MIT  
**Language**: Rust (edition 2024)  
**Captured**: 2026-04-23  

## Project Overview

hcom is a Rust-based inter-agent communication hub for AI coding tools. It connects Claude Code, Gemini CLI, Codex, and OpenCode so agents can message, watch, and spawn each other across terminals. The binary provides a TUI dashboard, a PTY wrapper for tool hosting, CLI commands for messaging/launch/resume, and an MQTT relay for cross-device sync.

Key capabilities:
- **Launch**: `hcom 3 claude --tag api` spawns 3 Claude instances with auto-assigned names
- **Send**: `hcom send @luna -- done with the refactor` routes messages by @mention
- **Listen**: `hcom listen` blocks and streams events; hooks auto-inject received messages
- **Fork/Resume**: `hcom f luna` / `hcom r luna` fork or resume sessions
- **Relay**: MQTT-based cross-device sync so agents on different machines coordinate
- **TUI Dashboard**: Full ratatui-based UI with agent status, message history, compose, and relay management

## How Inter-Agent Messaging Works

### Architecture

The messaging layer has three planes:

1. **Event plane** (SQLite `events` table): Append-only log. Every message, status change, and lifecycle event is an immutable row. Writers use `db.log_event(type, instance, data)`; readers advance per-instance cursors (`instances.last_event_id`) to get unread messages.

2. **Notify plane** (TCP): Each PTY-hosted agent runs a `NotifyServer` on a random port. When an event is written, `notify_all_instances()` connects to every registered notify endpoint. This provides instant wake-up (sub-millisecond) without polling.

3. **Delivery plane** (PTY inject): The `delivery.rs` loop runs per-agent inside the PTY wrapper. When notified of pending messages, it evaluates a **delivery gate** (is the agent idle? is the prompt clear? is an approval dialog showing?) and injects text into the terminal when safe.

### Message Flow

```
Sender --> hcom send @luna "hello"
       --> db.log_event("message", sender, {scope, mentions, text, ...})
       --> notify_all_instances() [TCP wake]
       --> relay trigger_push() [MQTT for cross-device]

Receiver's delivery loop:
  notify.wait() wakes
  db.has_pending(name)?
  evaluate_gate() [idle? prompt clear? no approval?]
  inject_text(port, "<hcom>") into the PTY
  Wait for text to render on screen
  inject_enter() to submit
  Verify cursor advance
  Advance last_event_id cursor in instances table
```

### Scope and Routing (`messages.rs`)

- **Broadcast**: No @mentions → delivered to all active instances
- **Mentions**: `@luna @api-` prefix-matched against instance names (with tag support, e.g. `api-luna`)
- **Strict invalid mention rejection**: Unknown @targets error immediately
- **Device suffix**: `luna:BOXE` routes to luna on remote device BOXE via relay

### Hook Integration (`hooks/`)

Each tool (Claude, Gemini, Codex, OpenCode) has hooks that:
- `SessionStart`: Register instance, set status to `listening`
- `AfterAgent`: Set status to `listening` after agent finishes processing
- `AfterUser`: Set status to `active` when user starts typing
- `BeforeAgent`: Poll for pending messages and inject them into the agent's context as `<hcom>...</hcom>` XML tags
- `SessionStop`: Record lifecycle event, mark stopped

### PTY Injection (`delivery.rs`)

The delivery state machine:
```
Idle → Pending (message arrives)
Pending → evaluate gate → inject text → WaitTextRender
WaitTextRender → verify text appeared → inject Enter → WaitTextClear
WaitTextClear → verify prompt cleared → VerifyCursor
VerifyCursor → advance cursor → Idle/Pending
```

Tool-specific gate configs:
- **Claude**: require_idle=true, require_ready_prompt=false, require_prompt_empty=true (uses VT100 dim detection), block_on_approval=true
- **Gemini**: require_idle=true, require_ready_prompt=true ("Type your message" disappears on input), block_on_user_activity=true
- **Codex**: require_idle=true, require_ready_prompt=false, require_prompt_empty=true (dim `›` prompt detection), block_on_approval=true (OSC9 detection)
- **OpenCode**: All gates disabled — OpenCode's TypeScript plugin handles delivery after initial PTY bootstrap

## How Collision Detection Works

Collision detection is **not** a file-locking system. Instead, hcom uses:

1. **Instance identity binding**: Each agent process gets a unique name (e.g., `luna`, `api-nova`). The `instances` table tracks `(name, session_id, pid, parent_session_id)`. Process binding (`session_bindings` table) maps session UUIDs to instance names. Subagents use `parent_name` to link to their creator.

2. **Sequential status gating**: The delivery gate ensures only one injection happens at a time. The state machine (`Idle → Pending → WaitTextRender → WaitTextClear → VerifyCursor`) prevents concurrent injections from clobbering each other.

3. **Process binding refresh**: `refresh_binding()` in `delivery.rs` checks the process binding on every loop iteration and updates the instance name if a session resume changed it.

4. **Read receipt tracking**: `compute_read_receipts()` in `messages.rs` determines which messages have been seen by which agents, preventing re-delivery.

5. **DB cursor advancement**: Each instance tracks `last_event_id` in the `instances` table. After successful delivery, the cursor advances to mark those events as read.

For file-edit conflicts specifically, hcom tracks `tool:Write`, `tool:Edit`, etc. event types in the database (the `FILE_WRITE_CONTEXTS` constant in `db.rs` lists these). The bundling system (`hcom bundle`) lets agents attach event IDs, file paths, and transcript ranges to messages for coordination.

## Spawn/Fork/Resume Mechanics

### Launch (`hcom <N> <tool>`)

1. The `launcher` module allocates N names from a pronouncable word list (CVCV pattern via FNV-1a hash)
2. Each instance gets registered in the `instances` table with status=`launching`
3. For Claude: the PTY wrapper (`src/pty/`) wraps the tool in a pseudoterminal
4. For Gemini/Codex: similar PTY wrapping with tool-specific ready patterns
5. The SessionStart hook fires and updates the instance to status=`listening`
6. The delivery loop starts watching for messages

### Fork (`hcom f <name>`)

Fork reuses the resume path with `fork=true`:
1. Loads the stopped instance snapshot from the `life` event with `action=stopped`
2. Pre-allocates a new name for the fork child
3. Tool-specific fork args:
   - Claude: `--resume <session_id> --fork-session`
   - Codex: `fork <session_id>`
   - OpenCode: `--session <session_id> --fork`
4. Sets the cursor to the current max event ID (no replay of parent's messages)
5. An identity-reset system prompt tells the fork it is a new agent

### Resume (`hcom r <name>`)

1. Resolution chain: display name → stopped instance → session UUID → thread name → on-disk adoption
2. Loads snapshot from `life` events (tool, session_id, tag, cwd)
3. Builds tool-specific resume args (e.g., Claude: `--resume <session_id>`)
4. Merges original launch args with resume args (tool-specific arg parsers)
5. Can also adopt an existing tool session by UUID or thread name from disk

## TUI Dashboard

The TUI (`src/tui/`) is built on ratatui + crossterm:

- **`app.rs`**: Main event loop, handles keyboard input, composes/delegates to model updates and rendering
- **`model.rs`**: Data models — `AgentStatus` (Active/Listening/Blocked/Launching/Inactive), `ViewMode` (Inline/Vertical), `InputMode` (Navigate/Compose/CommandOutput/Launch/Relay), `RelayPopupState`
- **`state.rs`**: `UiState` with cursor, selection, input, search, scroll state
- **`data.rs`**: `DataSource` trait for loading instance/event data from DB
- **`render/`**: Rendering modules for agents, messages, launch, text
- **`input.rs`**: Key handling for navigate/compose/command modes
- **`commands.rs`**: Command processing (`:send`, `:kill`, `:listen`, etc.)
- **`rpc.rs`/`rpc_async.rs`**: RPC client for async operations (launch, relay toggle, kill)
- **`db.rs`**: TUI-specific DB queries (instance listings, event history, read receipts)

Key interactions:
- Arrow keys/j/k: navigate agents
- Enter: compose and send messages
- `:send @name text`: CLI-style send command
- `l`/`r`: launch/resume agents
- `R`: toggle relay popup for cross-device sync
- `q`: quit

## Relay (Cross-Device Sync)

The MQTT relay (`src/relay/`) enables agents on different machines to coordinate:

- **`broker.rs`**: Parallel TLS handshake to find the fastest public MQTT broker (EMQX, HiveMQ, Mosquitto)
- **`worker.rs`**: Long-running daemon that polls the local DB for new events and pushes them via MQTT
- **`push.rs`/`pull.rs`**: Push local events to remote devices, pull remote events into local DB
- **`crypto.rs`**: ChaCha20-Poly1305 encryption for relay messages using a shared PSK
- **`client.rs`**: MQTT client connection management with reconnection and clean session handling
- **`control.rs`**: RPC-based remote control — launch, resume, kill agents on other devices
- **`token.rs`**: Token generation/sharing for relay group setup (`hcom relay new` produces a shareable token)

Topic layout: `{relay_id}/{device_uuid}` for state, `{relay_id}/control` for commands.

## License

**MIT License** — Copyright (c) 2025 aannoo. Full text in `/tmp/hcom-sources/LICENSE`.

## Key Files for Borrowing the Messaging Layer

These are the most relevant files for understanding and potentially reusing hcom's inter-agent messaging:

| File | Purpose |
|------|---------|
| `messages.rs` | Core message routing, scope computation, @mention resolution, delivery filtering |
| `delivery.rs` | PTY injection state machine, delivery gate logic, tool-specific configs |
| `send.rs` | CLI `hcom send` — message validation, scope computation, event logging, notification |
| `db.rs` | SQLite schema, event logging, instance tracking, cursor management, read receipts |
| `listen.rs` | CLI `hcom listen` — event polling with TCP notify, SQL filters, JSON/compose output |
| `instance_lifecycle.rs` | Instance status state machine, heartbeat tracking, stale cleanup |
| `relay/mod.rs` | Relay health derivation, PSK management, MQTT topic layout |
| `relay/worker.rs` | Relay daemon lifecycle, PID file management, auto-spawn |
| `relay/broker.rs` | Parallel broker discovery |
| `relay/push.rs`/`pull.rs` | Cross-device event sync |
| `relay/crypto.rs` | ChaCha20-Poly1305 envelope encryption |
| `hooks/mod.rs` | Hook normalization — unified payload across Claude/Gemini/Codex/OpenCode |
| `hooks/claude.rs`/`gemini.rs`/`codex.rs`/`opencode.rs` | Tool-specific hook handlers |
| `notify.rs` | TCP notify server for instant wake-up |
| `commands/launch.rs` | Agent spawning with tool-specific arg merging |
| `commands/fork.rs`/`resume.rs` | Session forking and resumption |
| `config.rs` | Configuration loading from `~/.hcom/config.toml` |
| `shared/constants.rs` | Shared constants (status strings, mention patterns, limits) |
| `skills/hcom-agent-messaging/SKILL.md` | Claude skill for agent messaging patterns |

### Architecture Patterns Worth Reusing

1. **SQLite as event bus**: Append-only events table + per-instance cursors provides durable, ordered, cross-process messaging without external dependencies
2. **TCP notify for instant wake-up**: Random port per instance registered in DB; sender connects, writes, closes — no persistent connections
3. **Gate-based injection**: Tool-specific configs (idle check, prompt empty check, approval detection) prevent clobbering agent state
4. **Identity binding**: Session UUID → instance name binding with process ID tracking handles session resumes and subagent parenting
5. **Tool-agnostic hooks**: Normalized `HookPayload` structure lets any tool integrate by providing a shallow adapter
6. **Relay with PSK encryption**: Shared secret group model with MQTT pub/sub for cross-device coordination without a server