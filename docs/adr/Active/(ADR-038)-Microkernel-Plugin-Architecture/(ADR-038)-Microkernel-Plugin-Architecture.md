---
title: "Microkernel Plugin Architecture"
artifact: ADR-038
track: standing
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
linked-artifacts:
  - VISION-006
  - INITIATIVE-018
depends-on-artifacts: []
evidence-pool: "agentic-runtime-chat-adapters"
---

# Microkernel Plugin Architecture

## Context

VISION-006 needs chat adapters (Zulip, Slack, Telegram, etc.) and runtime adapters (Claude Code, OpenCode, Gemini CLI, etc.). The operator should be able to choose their preferred platform without waiting for us to ship an adapter. The community should be able to contribute adapters in any language.

## Decision

The system uses a microkernel architecture with two plugin boundaries:

1. **Host bridge** is the microkernel for **chat adapter plugins.** It spawns one shared chat adapter per security domain and routes all events through it.
2. **Project bridge** is the microkernel for **runtime adapter plugins.** It spawns one per runtime session.

Plugins are subprocess executables that speak NDJSON over stdio. The kernel spawns the plugin as a child process, passes config on the first stdin line, then streams events and commands as newline-delimited JSON. This is language-agnostic — plugins can be written in Python, Go, Rust, Node, or shell.

Plugin security:
- Absolute paths in config, not bare command names.
- SHA-256 content hash pinning — kernel checks before spawning.
- Config file is owner-readable only (chmod 600) — kernel refuses to start if permissions are too open.
- Scoped config — each plugin receives only its own credentials.

Plugin distribution is package-manager-agnostic: `brew install`, `cargo install`, `uv tool install`, `npx`, or a local script.

## Alternatives Considered

- **Python base class plugins (in-process).** Simpler to implement but locks plugins to Python. Rejected because the operator community may prefer Go or Rust for chat adapters, and the runtime ecosystem is polyglot.
- **MCP as plugin protocol.** Powerful (capability negotiation, tool schemas) but heavier than needed for v1. The NDJSON protocol is simpler and sufficient. MCP is a viable future upgrade path — same stdio transport, richer protocol.
- **HTTP/WebSocket plugins.** Opens a network port, adds TLS complexity, and creates an attack surface. Stdio between parent and child is the most secure IPC available.

## Consequences

- Operators can write plugins in any language — lower barrier to community contributions.
- We ship reference plugins (Zulip chat, Claude Code runtime) but the architecture invites extension.
- What protocol a plugin uses internally (ACP, native CLI streaming, regex parsing) is the plugin's concern, not the kernel's. This decouples the kernel from runtime protocol evolution.
- Plugin subprocess management adds complexity to the host bridge (process lifecycle, crash recovery, stdio buffer management).
- SHA-256 pinning means plugin updates require config changes — intentional friction for security.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | -- | Decided during VISION-006 brainstorming. Informed by agentic-runtime-chat-adapters trove. |
