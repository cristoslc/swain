---
source-id: "crush-deepwiki-architecture"
title: "charmbracelet/crush — DeepWiki Architecture Overview"
type: web
url: "https://deepwiki.com/charmbracelet/crush"
fetched: 2026-04-07T01:57:51Z
hash: "4a7978c926a93b34870aa68451f7edcf054259f837411c0230316880eb4fcba0"
---

# charmbracelet/crush — Architecture Overview

**Source:** DeepWiki (indexed 24 March 2026 at commit 96f51ca5)

Crush is a terminal-based AI coding assistant built in Go by Charm (the team behind Bubble Tea, Lipgloss, Gum). It provides a TUI backed by a multi-provider AI integration layer and an extensive tool system.

## What is Crush?

Crush combines:

- A rich TUI built with Bubble Tea v2.
- Multi-provider AI integration through the `fantasy` abstraction layer.
- An extensive tool system for file manipulation, shell execution, LSP queries, and MCP resource access.
- Local SQLite storage for conversation history.
- Both interactive (TUI) and non-interactive (`crush run`) modes.

## System architecture

Crush follows a layered architecture with clear separation of concerns:

```
CLI entry (cobra / main.go)
  └── ConfigStore + app.App orchestrator
        ├── agent.Coordinator (manages session agents and model updates)
        │     └── agent.SessionAgent (runs the prompt/tool loop per session)
        ├── session.Service (SQLite persistence)
        ├── lsp.Manager (multiple language server lifecycles)
        ├── MCP server layer
        ├── shell.Shell (POSIX shell via mvdan.cc/sh)
        └── ui.New (Bubble Tea root program)
              └── subscribes to app.events channel (real-time updates)
```

The TUI subscribes to service events for real-time updates via `internal/app/app.go:108-119`.

**No HTTP server:** Unlike opencode, Crush does not expose an HTTP server API. It is a monolithic process. There is no `serve` mode or external client attachment.

## Core components

| Component | Type | Location | Purpose |
| --- | --- | --- | --- |
| `app.App` | Orchestrator | `internal/app/app.go` | Central coordinator for services and application lifecycle |
| `config.ConfigStore` | Configuration | `internal/config/` | Manages hierarchical configuration and persistence |
| `agent.Coordinator` | Agent manager | `internal/agent/coordinator.go` | Orchestrates session agents and model updates |
| `agent.SessionAgent` | Execution engine | `internal/agent/agent.go` | Handles the prompt/tool loop for a specific session |
| `ui.New` | TUI root | `internal/ui/model/` | Initializes the Bubble Tea program root |
| `session.Service` | Data access | `internal/session/session.go` | Manages session persistence and state |
| `shell.Shell` | Shell executor | `internal/shell/` | POSIX-compliant shell emulation |
| `lsp.Manager` | LSP client | `internal/lsp/` | Manages lifecycle of multiple language servers |

## Data flow

User input → TUI → `AgentCoordinator.Run` → `SessionAgent` → `fantasy.NewAgent` (LLM provider) → tool calls (BashTool, EditTool, etc.) → tool results fed back → final response → broadcast via `App.events` → TUI update.

## External dependencies

| Package | Purpose |
| --- | --- |
| `charm.land/bubbletea/v2` | TUI framework (Bubble Tea v2) |
| `charm.land/fantasy` | AI provider abstraction — unified interface to LLM providers and tools |
| `charm.land/catwalk` | Community-maintained provider and model capability registry |
| `mvdan.cc/sh/v3` | POSIX shell parsing for the bash tool |
| `modernc.org/sqlite` | CGO-free SQLite driver for persistence |
| `github.com/spf13/cobra` | CLI framework |

## Key design choices

- **Catwalk registry:** Default model listing managed at `github.com/charmbracelet/catwalk`. Community-contributed; Crush auto-fetches the latest list on startup (can be disabled).
- **fantasy abstraction:** Unified interface lets the agent run against any provider without code changes.
- **SQLite persistence:** All session history stored locally. No cloud sync by default.
- **LSP integration built-in:** Language server support is a first-class feature, not a plugin.
- **In-session model switching:** Supports switching between LLMs within the same session while preserving context.
- **Skills system:** Supports agent skills loaded from `~/.config/crush/skills/`.

## CLI modes

- **Interactive (TUI):** `crush` — starts the Bubble Tea TUI.
- **Non-interactive:** `crush run "prompt"` — runs a prompt headlessly and exits.
- No server mode or attach mode.

## Provenance

Crush was originally `opencode-ai/opencode` (early AI coding CLI). The repository was transferred to the Charm team (`charmbracelet/crush`) on July 29, 2025. The New Stack reviewed it in August 2025 as "Crush (Ex-OpenCode Al)". The anomalyco/opencode project (138k stars, SST team) is a separate, unrelated project that subsequently took the `opencode` name.
