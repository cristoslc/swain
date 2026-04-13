---
source-id: "opencode-cli-docs"
title: "CLI | OpenCode — Command reference"
type: web
url: "https://opencode.ai/docs/cli/"
fetched: 2026-04-07T01:57:50Z
hash: "1fc08f30f8cdb307c7ed9fe95957e4fbbdc7211df50f2e031afc7f66fc833924"
---

# CLI | OpenCode

The OpenCode CLI by default starts the TUI when run without any arguments.

```
opencode
```

## tui (default)

Start the OpenCode terminal user interface.

```
opencode [project]
```

| Flag | Short | Description |
| --- | --- | --- |
| `--continue` | `-c` | Continue the last session |
| `--session` | `-s` | Session ID to continue |
| `--fork` | | Fork the session when continuing |
| `--prompt` | | Prompt to use |
| `--model` | `-m` | Model to use in the form `provider/model` |
| `--agent` | | Agent to use |
| `--port` | | Port to listen on |
| `--hostname` | | Hostname to listen on |

## Commands

### attach

Attach a terminal to an already running OpenCode backend server started via `serve` or `web`.

```
opencode attach [url]
```

This allows using the TUI with a remote OpenCode backend:

```bash
# Start the backend server
opencode web --port 4096 --hostname 0.0.0.0

# In another terminal, attach the TUI to the running backend
opencode attach http://10.20.30.40:4096
```

| Flag | Short | Description |
| --- | --- | --- |
| `--dir` | | Working directory to start TUI in |
| `--session` | `-s` | Session ID to continue |

### run

Run opencode in non-interactive mode by passing a prompt directly.

```
opencode run [message..]
```

```bash
opencode run Explain the use of context in Go
```

Attach to a running `opencode serve` instance to avoid MCP server cold boot times:

```bash
# Start a headless server
opencode serve

# Run commands that attach to it
opencode run --attach http://localhost:4096 "Explain async/await in JavaScript"
```

| Flag | Short | Description |
| --- | --- | --- |
| `--continue` | `-c` | Continue the last session |
| `--session` | `-s` | Session ID to continue |
| `--fork` | | Fork the session when continuing |
| `--share` | | Share the session |
| `--model` | `-m` | Model in the form `provider/model` |
| `--agent` | | Agent to use |
| `--file` | `-f` | File(s) to attach to message |
| `--format` | | Output format: `default` or `json` |
| `--title` | | Title for the session |
| `--attach` | | Attach to a running opencode server |
| `--port` | | Port for the local server |

### serve

Start a headless OpenCode server for API access.

```
opencode serve
```

Starts an HTTP server providing API access to opencode functionality without the TUI interface.

| Flag | Description |
| --- | --- |
| `--port` | Port to listen on |
| `--hostname` | Hostname to listen on |
| `--mdns` | Enable mDNS discovery |
| `--cors` | Additional browser origin(s) to allow |

### web

Start a headless OpenCode server with a web interface.

```
opencode web
```

Starts an HTTP server and opens a web browser to access OpenCode through a web interface.

### acp

Start an ACP (Agent Client Protocol) server.

```
opencode acp
```

Communicates via stdin/stdout using nd-JSON.

| Flag | Description |
| --- | --- |
| `--cwd` | Working directory |
| `--port` | Port to listen on |
| `--hostname` | Hostname to listen on |

### session

| Command | Description |
| --- | --- |
| `opencode session list` | List all sessions |

### stats

Show token usage and cost statistics.

```
opencode stats [--days N] [--models] [--project] [--tools N]
```

### agent

| Command | Description |
| --- | --- |
| `opencode agent list` | List all available agents |
| `opencode agent create` | Create a new agent with custom configuration |

### auth

| Command | Description |
| --- | --- |
| `opencode auth login` | Configure API keys for any provider |
| `opencode auth list` | List authenticated providers |
| `opencode auth logout` | Clear a provider's credentials |

### mcp

| Command | Description |
| --- | --- |
| `opencode mcp add` | Add an MCP server |
| `opencode mcp list` | List configured MCP servers |
| `opencode mcp auth [name]` | Authenticate with an OAuth-enabled MCP server |

### models

```
opencode models [provider] [--refresh] [--verbose]
```

List available models. Use `--refresh` to update the cache from models.dev.

### export / import

| Command | Description |
| --- | --- |
| `opencode export [sessionID]` | Export session data as JSON |
| `opencode import <file>` | Import session data from JSON or share URL |

### upgrade

```
opencode upgrade [target]
opencode upgrade v0.1.48
```

## Global Flags

| Flag | Short | Description |
| --- | --- | --- |
| `--help` | `-h` | Display help |
| `--version` | `-v` | Print version number |
| `--print-logs` | | Print logs to stderr |
| `--log-level` | | Log level (DEBUG, INFO, WARN, ERROR) |

## Key environment variables

| Variable | Description |
| --- | --- |
| `OPENCODE_CONFIG` | Path to config file |
| `OPENCODE_TUI_CONFIG` | Path to TUI config file |
| `OPENCODE_SERVER_PASSWORD` | Enable basic auth for `serve`/`web` |
| `OPENCODE_SERVER_USERNAME` | Override basic auth username (default `opencode`) |
| `OPENCODE_DISABLE_CLAUDE_CODE` | Disable reading from `.claude` (prompt + skills) |
| `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS` | Disable loading `.claude/skills` |
| `OPENCODE_DISABLE_AUTOCOMPACT` | Disable automatic context compaction |
| `OPENCODE_EXPERIMENTAL_PLAN_MODE` | Enable plan mode |
| `OPENCODE_ENABLE_EXA` | Enable Exa web search tools |
