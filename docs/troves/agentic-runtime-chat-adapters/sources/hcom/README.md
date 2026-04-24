# hcom Source Files

Selected source files from [hcom](https://github.com/aannoo/hcom) v0.7.13 — a Rust CLI that lets AI agents message, watch, and spawn each other across terminals.

## What's included and why

| File | Role | Why it matters |
|------|------|----------------|
| `Cargo.toml` | Project manifest | Dependency list reveals MQTT relay (rumqttc), encryption (chacha20poly1305), and TUI stack |
| `LICENSE` | MIT license | Provenance |
| `src/main.rs` | CLI entry point | Top-level command dispatch |
| `src/launcher.rs` | Agent spawning | Launches agent processes (Claude, Gemini, Codex, OpenCode) in PTYs |
| `src/instance_lifecycle.rs` | Session lifecycle | Start/stop/resume state machine for agent instances |
| `src/instance_binding.rs` | Session binding | Binds a PTY session to an agent identity |
| `src/instances.rs` | Instance registry | Tracks live agents, names, and IDs |
| `src/messages.rs` | Message model | Core message types and serialization |
| `src/delivery.rs` | Message delivery | Routing and delivery of messages between agents |
| `src/router.rs` | Message routing | Resolves destinations and dispatches |
| `src/config.rs` | Configuration | Relay endpoints, encryption keys, agent profiles |
| `src/identity.rs` | Agent identity | How agents identify themselves on the network |
| `src/bootstrap.rs` | Bootstrap | Initial setup and daemon startup |
| `src/relay/mod.rs` | Relay module root | MQTT relay orchestration and protocol entry |
| `src/relay/client.rs` | MQTT client | Connects to broker for cross-terminal messaging |
| `src/relay/broker.rs` | Local broker | Embedded broker for LAN-only mode |

## What's excluded

- `commands/` — CLI subcommand handlers (send, list, status, etc.)
- `hooks/` — Per-agent hook adapters (claude, codex, gemini, opencode)
- `relay/{control,pull,push,replay,token,worker}.rs` — Relay internals
- `tui/`, `pty/` — Terminal UI and PTY management
- `core/` — Helpers, filters, bundles
- Test fixtures, CI workflows, plugin configs, scripts