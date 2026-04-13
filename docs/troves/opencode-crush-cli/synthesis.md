---
trove: opencode-crush-cli
synthesized: 2026-04-08
sources: 8
---

# OpenCode & Crush CLI Server Modes — Synthesis

## Key finding: two separate projects, both now support server mode

"opencode" and "Crush" are distinct projects often confused due to naming history. Both now offer server mode capabilities, but with different maturity levels.

| | opencode (anomalyco) | Crush (charmbracelet) |
|---|---|---|
| Repo | `github.com/anomalyco/opencode` | `github.com/charmbracelet/crush` |
| Team | SST / Anomaly (terminal.shop) | Charm (Bubble Tea, Lipgloss) |
| Language | TypeScript + Rust | Go |
| Server mode | Mature (`opencode serve`) | Experimental (`crush server`, `CRUSH_CLIENT_SERVER=1`) |
| ACP support | Yes (`opencode acp`) | Planned (issue #2091) |
| Stars | 138k | 22.7k |

---

## Theme 1 — Server mode: the defining architectural difference

### OpenCode: mature client/server architecture

When you run `opencode`, it starts **two things**: a TUI client and an HTTP server. The TUI is just one client of many.

**Server commands:**

- `opencode serve` — headless HTTP server (port 4096 by default)
- `opencode web` — server + browser UI
- `opencode attach <url>` — TUI connects to remote server
- `opencode acp` — ACP server for editor integration (stdin/stdout ndjson)

**API surface:** OpenAPI 3.1 spec at `/doc`, full REST API including:
- Sessions, messages, files, tools
- `/tui/*` endpoints for programmatic TUI control
- `/experimental/tool` for tool discovery
- Server-sent events stream at `/event`

### Crush: experimental server mode

Crush has **two** server-related features:

**1. `crush server` (v0.34.0+):**
- Headless server mode (TCP or Unix socket)
- `--host` flag supports both: `127.0.0.1:4096` or `unix:///tmp/crush-501.sock`
- Default is Unix socket on macOS/Linux
- Use `crush --host <url>` to connect TUI to running server

**2. `CRUSH_CLIENT_SERVER=1` (v0.55.0, experimental):**
- Enables client-server architecture within Crush itself
- TUI becomes client of RPC server
- Swagger docs generated and served
- Not default yet — known bugs exist

The DeepWiki source stating "No HTTP server" is **outdated** (pre-v0.34.0).

---

## Theme 2 — ACP (Agent Client Protocol) support

### OpenCode: full ACP implementation

`opencode acp` starts an ACP-compatible subprocess:

- **Transport**: stdin/stdout ndjson (no network)
- **Use case**: Editor integration (Zed, JetBrains, Neovim)
- **Protocol**: JSON-RPC over ndjson streams
- **Mapping**: ACP bridges to OpenCode's internal HTTP server

Editors configure OpenCode as an ACP agent:
```json
{ "agent_servers": { "OpenCode": { "command": "opencode", "args": ["acp"] } } }
```

ACP enables **any ACP-compatible editor** to drive OpenCode sessions without custom plugin code.

### Crush: ACP client planned (not yet ACP server)

From issue #2091, Crush is considering acting as an **ACP client** to drive other agents (like Claude Code). ACP server support for Crush is tracked but not yet implemented.

---

## Theme 3 — Config surface comparison

| Aspect | OpenCode | Crush |
|--------|----------|-------|
| Config file | `opencode.json` (server/runtime) + `tui.json` (TUI client) | `crush.json` (single file) |
| Config split | Yes (server vs. TUI separation) | No (unified config) |
| Claude Code compat | Reads `.claude/skills` and `CLAUDE.md` by default | Own skill system (`~/.config/crush/skills/`), no `.claude` by default |
| Provider config | Environment vars + `opencode.json` | Environment vars + `crush.json` + Catwalk registry |
| Model switching | In-session, context preserved | In-session, context preserved |

OpenCode's config split reflects its client/server architecture: server config (providers, agents, permissions) is separate from TUI client config (themes, keybinds, scroll settings).

---

## Theme 4 — Non-interactive modes

Both tools support headless execution:

| Command | Purpose |
|---------|---------|
| `opencode run "prompt"` | Non-interactive execution |
| `opencode run --attach http://localhost:4096 "prompt"` | Reuse existing server (avoids MCP cold-boot) |
| `crush run "prompt"` | Non-interactive execution |
| `crush server` | Headless server for remote access or CI |

Crush's `--yolo` flag auto-accepts all permissions (danger mode for CI).

---

## Theme 5 — HTTP API comparison

### OpenCode HTTP API (mature, documented)

Full REST API with 50+ endpoints:

- `/global/*` — health, events
- `/project/*` — project metadata
- `/session/*` — session CRUD, messaging, TODO, diff, share, summarize
- `/file/*` — file system operations, search
- `/tui/*` — programmatic TUI control (append-prompt, submit-prompt, execute-command)
- `/experimental/tool/*` — tool discovery with JSON schemas
- `/doc` — OpenAPI 3.1 spec

Authentication: `OPENCODE_SERVER_PASSWORD` for HTTP Basic auth.

### Crush HTTP API (experimental)

From v0.55.0, Crush generates Swagger docs and serves them. The RPC server is gated behind `CRUSH_CLIENT_SERVER=1` and not yet documented. The `crush server` command exposes an HTTP endpoint, but the API surface is not publicly documented (as of Apr 2026).

---

## Points of agreement

- Both are Go-based CLI tools with TUI built on Charm's Bubble Tea framework
- Both support multi-provider AI (not tied to Anthropic)
- Both support MCP servers for tool extensibility
- Both support LSP integration
- Both store session history locally (OpenCode in its own format, Crush in SQLite)
- Both support in-session model switching with context preservation

---

## Points of disagreement (corrected from prior version)

- ~~Server mode~~: **Both now support server mode** — OpenCode mature, Crush experimental
- **ACP**: OpenCode has full ACP support (`opencode acp`); Crush has ACP client planned but not yet implemented
- **API maturity**: OpenCode's HTTP API is mature and documented; Crush's is experimental and not yet documented
- **Architecture maturity**: OpenCode's client/server is production-ready; Crush's is opt-in experimental
- **Scale**: OpenCode 138k stars vs Crush 22.7k stars (Apr 2026)

---

## Gaps addressed

Prior synthesis stated "Crush has no server mode" — this was incorrect. Crush has `crush server` since v0.34.0 and client-server architecture since v0.55.0 (opt-in). The DeepWiki source was outdated.

Remaining gaps:
- Crush HTTP API spec not publicly documented (only mentions "generated swagger docs")
- No detailed docs on `crush server` API surface beyond `--host` flag
- Permission model comparison not covered (both have them, but details differ)