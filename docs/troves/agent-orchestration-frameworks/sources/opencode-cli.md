# CLI | OpenCode

## CLI

OpenCode CLI options and commands.

The OpenCode CLI by default starts the TUI when run without any arguments.

```bash
opencode
```

But it also accepts commands as documented on this page. This allows you to interact with OpenCode programmatically.

```bash
opencode run "Explain how closures work in JavaScript"
```

## Session Management

### session

Manage OpenCode sessions.

```bash
opencode session [command]
```

#### list

List all OpenCode sessions.

```bash
opencode session list
```

Flags:
- `--max-count`, `-n`: Limit to N most recent sessions
- `--format`: Output format: table or json (table)

#### delete

Delete an OpenCode session.

```bash
opencode session delete <sessionID>
```

### Session Storage

Sessions are stored in a local SQLite database at `~/.local/share/opencode/storage`.

### Export

Export session data as JSON.

```bash
opencode export [sessionID]
```

If you don't provide a session ID, you'll be prompted to select from available sessions.

Flags:
- `--sanitize`: Redact sensitive transcript/file data

### Import

Import session data from a JSON file or OpenCode share URL.

```bash
opencode import <file>
```

You can import from a local file or an OpenCode share URL.

```bash
opencode import session.json
opencode import https://opncd.ai/s/abc123
```

## Database

### db path

Print the database path.

```bash
opencode db path
```

Output: `~/.local/share/opencode/storage`

## TUI Mode

Start the OpenCode terminal user interface.

```bash
opencode [project]
```

Flags:
- `--continue`, `-c`: Continue the last session
- `--session`, `-s`: Session ID to continue
- `--fork`: Fork the session when continuing (use with `--continue` or `--session`)
- `--prompt`: Prompt to use
- `--model`, `-m`: Model to use in the form of provider/model
- `--agent`: Agent to use
- `--port`: Port to listen on
- `--hostname`: Hostname to listen on
- `--mdns`: Enable mDNS discovery
- `--mdns-domain`: Custom mDNS domain name
- `--cors`: Additional browser origin(s) to allow CORS

## MCP Commands

### mcp

Manage Model Context Protocol servers.

```bash
opencode mcp [command]
```

#### add

Add an MCP server to your configuration.

```bash
opencode mcp add
```

#### list

List all configured MCP servers and their connection status.

```bash
opencode mcp list
opencode mcp ls
```

## ACP Server

### acp

Start an ACP (Agent Client Protocol) server.

```bash
opencode acp
```

This command starts an ACP server that communicates via stdin/stdout using nd-JSON.

Flags:
- `--cwd`: Working directory
- `--port`: Port to listen on
- `--hostname`: Hostname to listen on
- `--mdns`: Enable mDNS discovery
- `--mdns-domain`: Custom mDNS domain name
- `--cors`: Additional browser origin(s) to allow CORS

## Server Mode

### serve

Start a headless OpenCode server for API access.

```bash
opencode serve
```

This starts an HTTP server that provides API access to opencode functionality without the TUI interface. Set `OPENCODE_SERVER_PASSWORD` to enable HTTP basic auth (username defaults to `opencode`).

Flags:
- `--port`: Port to listen on
- `--hostname`: Hostname to listen on
- `--mdns`: Enable mDNS discovery
- `--mdns-domain`: Custom mDNS domain name
- `--cors`: Additional browser origin(s) to allow CORS

### web

Start a headless OpenCode server with a web interface.

```bash
opencode web
```

Flags:
- `--port`: Port to listen on
- `--hostname`: Hostname to listen on
- `--mdns`: Enable mDNS discovery
- `--mdns-domain`: Custom mDNS domain name
- `--cors`: Additional browser origin(s) to allow CORS

### attach

Attach a terminal to an already running OpenCode backend server.

```bash
opencode attach [url]
```

This allows using the TUI with a remote OpenCode backend. For example:

```bash
# Start the backend server for web/mobile access
opencode web --port 4096 --hostname 0.0.0.0

# In another terminal, attach the TUI to the running backend
opencode attach http://10.20.30.40:4096
```

## Other Commands

### run

Run opencode in non-interactive mode by passing a prompt directly.

```bash
opencode run [message..]
```

You can also attach to a running `opencode serve` instance to avoid MCP server cold boot times on every run:

```bash
# Start a headless server in one terminal
opencode serve

# In another terminal, run commands that attach to it
opencode run --attach http://localhost:4096 "Explain async/await in JavaScript"
```

### agent

Manage agents for OpenCode.

```bash
opencode agent [command]
```

### auth

Command to manage credentials and login for providers.

```bash
opencode auth [command]
```

### models

List all available models from configured providers.

```bash
opencode models [provider]
```

### stats

Show token usage and cost statistics for your OpenCode sessions.

```bash
opencode stats
```

Flags:
- `--days`: Show stats for the last N days (all time)
- `--tools`: Number of tools to show (all)
- `--models`: Show model usage breakdown (hidden by default)
- `--project`: Filter by project

Source: https://opencode.ai/docs/cli/
Fetched: 2026-05-05
