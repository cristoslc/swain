---
source-id: "opencode-acp-mode"
title: "OpenCode ACP (Agent Client Protocol) Support"
type: web
url: "https://opencode.ai/docs/acp/"
fetched: 2026-04-08T00:00:00Z
---

# OpenCode ACP Support

OpenCode supports the Agent Client Protocol (ACP), an open standard for communication between code editors and AI coding agents.

## What is ACP?

ACP (Agent Client Protocol) is an editor-agnostic protocol for driving AI coding agents. It uses newline-delimited JSON (ndjson) over stdin/stdout as its transport.

## Usage

```bash
opencode acp
```

This starts OpenCode as an ACP-compatible subprocess that communicates with editors over JSON-RPC via stdio.

## Editor Configuration

### Zed

Add to `~/.config/zed/settings.json`:

```json
{
  "agent_servers": {
    "OpenCode": {
      "command": "opencode",
      "args": ["acp"]
    }
  }
}
```

Keybinding:

```json
[
  {
    "bindings": {
      "cmd-alt-o": [
        "agent::NewExternalAgentThread",
        {
          "agent": {
            "custom": {
              "name": "OpenCode",
              "command": {
                "command": "opencode",
                "args": ["acp"]
              }
            }
          }
        }
      ]
    }
  }
]
```

### JetBrains IDEs

Add to `acp.json`:

```json
{
  "agent_servers": {
    "OpenCode": {
      "command": "/absolute/path/bin/opencode",
      "args": ["acp"]
    }
  }
}
```

### Avante.nvim

```lua
{
  acp_providers = {
    ["opencode"] = {
      command = "opencode",
      args = { "acp" }
    }
  }
}
```

### CodeCompanion.nvim

```lua
require("codecompanion").setup({
  interactions = {
    chat = {
      adapter = {
        name = "opencode",
        model = "claude-sonnet-4",
      },
    },
  },
})
```

## Protocol Details

From the CLI docs:

> This command starts an ACP server that communicates via stdin/stdout using nd-JSON.

The ACP server:

1. **Reads from stdin**: Receives JSON-RPC requests from the editor
2. **Writes to stdout**: Sends JSON-RPC responses and events
3. **No network**: No HTTP server, no TCP port — pure stdio transport

## ACP vs HTTP Server

| Mode | Command | Transport | Use Case |
|------|---------|-----------|----------|
| HTTP Server | `opencode serve` | HTTP on port 4096 | Remote access, programmatic API |
| ACP Server | `opencode acp` | stdin/stdout ndjson | Editor integration |

The ACP mode is specifically designed for:

- **Editor plugins**: Zed, JetBrains, Neovim
- **No network exposure**: Pure stdio, no HTTP listener
- **Session-based**: Maintains conversation context per editor session

## How It Works

From DeepWiki's Kilo-Code integration:

1. Sets `process.env.CLIENT = "acp"` for tool availability gating
2. Calls `bootstrap()` to initialize project context
3. Starts the HTTP server with `Server.listen(opts)` internally
4. Wraps `process.stdin` / `process.stdout` into streams
5. Passes both streams to `ndJsonStream()` from `@agentclientprotocol/sdk`
6. Creates an `AgentSideConnection` that bridges ACP to the internal HTTP API

This means ACP is a **thin bridge** over OpenCode's existing HTTP server architecture.

## Supported Features via ACP

All features available in the terminal are supported via ACP:

- Built-in tools (file operations, terminal commands)
- Custom tools and slash commands
- MCP servers from configuration
- Project rules from `AGENTS.md`
- Custom formatters and linters
- Agents and permissions system

**Unsupported**: Some built-in slash commands like `/undo` and `/redo` (as of Apr 2026).

## Related

- `opencode serve` — full HTTP server
- `opencode attach <url>` — connect TUI to remote server
- `acpx` — headless ACP client for automation