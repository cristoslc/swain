---
trove: opencode-crush-cli
synthesized: 2026-04-07
sources: 5
---

# opencode server/TUI modes and Crush CLI — Synthesis

## Key finding: two separate projects share a confusing lineage

"opencode" and "Crush" are easy to conflate but are distinct projects. The original `opencode-ai/opencode` was renamed Crush when transferred to the Charm team on July 29, 2025. The dominant `anomalyco/opencode` project (138k stars, SST team) is a separate project built by the creators of terminal.shop.

| | opencode (anomalyco) | Crush (charmbracelet) |
|---|---|---|
| Repo | `github.com/anomalyco/opencode` | `github.com/charmbracelet/crush` |
| Team | SST / Anomaly (terminal.shop) | Charm (Bubble Tea, Lipgloss) |
| Language | TypeScript + Rust | Go |
| Architecture | Client/server (HTTP) | Event-driven monolith |
| Server mode | Yes (`opencode serve`) | No |
| TUI attach | Yes (`opencode attach <url>`) | No |
| Provenance | Independent project | Fork of original `opencode-ai/opencode` |

---

## Theme 1 — opencode's client/server architecture is its core differentiator

When you run `opencode`, it starts **two things**: a TUI client and an HTTP server. The TUI is just one client; the server is always present.

This has practical consequences:

- **`opencode serve`** starts the server without any TUI. Useful for CI, scripts, or remote control.
- **`opencode web`** starts the server and opens a browser-based UI instead of the TUI.
- **`opencode attach <url>`** starts a TUI that connects to a running server on another host. This is the remote-control model — run the server on a dev box, drive it from a phone or a different terminal.
- **`opencode run --attach http://localhost:4096 "prompt"`** avoids MCP cold-boot costs by reusing an existing server.

The OpenAPI 3.1 spec at `/doc` is the single source of truth for all server capabilities.

---

## Theme 2 — opencode's config is split by concern

opencode deliberately separates server concerns from TUI concerns:

- **`opencode.json`** — server/runtime behavior: providers, models, permissions, agents, MCP servers, formatters.
- **`tui.json`** — TUI behavior: theme, keybinds, scroll speed, diff style, mouse capture.

This split is intentional. The TUI is a client; it can have its own preferences independent of what the server does.

---

## Theme 3 — opencode's `/tui` endpoint enables programmatic TUI control

The server exposes a `/tui` family of endpoints used by IDE plugins:

- `/tui/append-prompt` — inject text into the prompt box.
- `/tui/submit-prompt` — trigger submission.
- `/tui/execute-command` — run a slash command.
- `/tui/control/next` + `/tui/control/response` — implement a request/response loop to handle interactive TUI prompts from an external driver.

This is how the VS Code / IDE plugins work. They talk to the running opencode server rather than spawning a new process.

---

## Theme 4 — Crush is a monolith with a polished TUI; no server exposure

Crush uses a layered event-driven architecture with no HTTP surface:

```
CLI entry → app.App orchestrator
  ├── agent.Coordinator → agent.SessionAgent → fantasy (LLM abstraction)
  ├── session.Service (SQLite)
  ├── lsp.Manager
  ├── MCP layer
  └── ui.New (Bubble Tea v2) ← subscribes to app.events channel
```

All updates flow through an internal events channel. The TUI is not a client of an HTTP server — it's an event subscriber.

Crush's `fantasy` abstraction layer provides a unified interface to multiple providers (Anthropic, OpenAI, Gemini, Bedrock, Copilot, Vercel, more). The `catwalk` registry is a community-maintained list of supported models; Crush fetches the latest on startup.

Key UX differentiator: in-session model switching with context preserved. You can start on GPT-4, switch to Claude, then switch to a local model — without losing conversation history.

---

## Theme 5 — Both tools read Claude Code artifacts by default

opencode reads `.claude/skills` and `CLAUDE.md` from the project by default (controlled by `OPENCODE_DISABLE_CLAUDE_CODE` and friends). This means swain skills are available in opencode sessions without any extra configuration.

Crush has its own config format (`crush.json`) and skill system (`~/.config/crush/skills/`), but it does not read `.claude` files by default.

---

## Points of agreement

- Both are Go-based CLI tools with a TUI as the primary interface.
- Both support multi-provider AI (not tied to Anthropic).
- Both support MCP servers for tool extensibility.
- Both support LSP integration.
- Both have a non-interactive run mode for scripting (`opencode run`, `crush run`).
- Both store session history locally (opencode in its own format, Crush in SQLite).

---

## Points of disagreement

- **Server mode:** opencode exposes a full HTTP API with sessions, messages, files, and TUI control. Crush has no server mode.
- **Architecture:** opencode is explicitly client/server. Crush is a monolith with internal event bus.
- **Remote control:** opencode supports `attach` for a TUI to connect to a remote server. Crush has no equivalent.
- **Config surface:** opencode has a split config (server vs. TUI). Crush has a single `crush.json`.
- **Scale:** opencode is 138k stars and 844 contributors as of Apr 2026. Crush is newer and smaller.
- **Claude Code compat:** opencode reads `.claude` by default. Crush does not.

---

## Gaps

- No source covers opencode's ACP (`opencode acp`) mode in depth. The ACP server runs via stdin/stdout nd-JSON, which may be relevant for agent-to-agent integration.
- Crush's `crush run` non-interactive mode lacks detailed documentation in collected sources.
- Neither source covers permission models (what actions require confirmation, how to configure auto-approval).
- The TNS review article (Aug 2025) was paywalled and not fully collected.
