---
source-id: "opencode-server-docs"
title: "Server | OpenCode — HTTP server mode documentation"
type: web
url: "https://opencode.ai/docs/server/"
fetched: 2026-04-07T01:57:48Z
hash: "ae3c8284a47d51b5e7a14d8f1d6beb115f70849046df21051fcdfbdb2d6ce20b"
---

# Server | OpenCode

Interact with the opencode server over HTTP.

The `opencode serve` command runs a headless HTTP server that exposes an OpenAPI endpoint that an opencode client can use.

## Usage

```
opencode serve [--port <number>] [--hostname <string>] [--cors <origin>]
```

### Options

| Flag | Description | Default |
| --- | --- | --- |
| `--port` | Port to listen on | `4096` |
| `--hostname` | Hostname to listen on | `127.0.0.1` |
| `--mdns` | Enable mDNS discovery | `false` |
| `--mdns-domain` | Custom domain name for mDNS service | `opencode.local` |
| `--cors` | Additional browser origins to allow | `[]` |

`--cors` can be passed multiple times:

```
opencode serve --cors http://localhost:5173 --cors https://app.example.com
```

## Authentication

Set `OPENCODE_SERVER_PASSWORD` to protect the server with HTTP basic auth. The username defaults to `opencode`, or set `OPENCODE_SERVER_USERNAME` to override it. This applies to both `opencode serve` and `opencode web`.

```
OPENCODE_SERVER_PASSWORD=your-password opencode serve
```

## How it works

When you run `opencode`, it starts a TUI and a server. The TUI is the client that talks to the server. The server exposes an OpenAPI 3.1 spec endpoint. This endpoint is also used to generate an SDK.

This architecture lets opencode support multiple clients and allows you to interact with opencode programmatically.

You can run `opencode serve` to start a standalone server. If you have the opencode TUI running, `opencode serve` will start a new server.

### Connect to an existing server

When you start the TUI it randomly assigns a port and hostname. You can pass in the `--hostname` and `--port` flags to fix them. Then use this to connect to its server.

The `/tui` endpoint can be used to drive the TUI through the server. For example, you can prefill or run a prompt. This setup is used by the OpenCode IDE plugins.

## Spec

The server publishes an OpenAPI 3.1 spec that can be viewed at:

```
http://<hostname>:<port>/doc
```

For example, `http://localhost:4096/doc`.

## APIs

### Global

| Method | Path | Description | Response |
| --- | --- | --- | --- |
| `GET` | `/global/health` | Get server health and version | `{ healthy: true, version: string }` |
| `GET` | `/global/event` | Get global events (SSE stream) | Event stream |

### Project

| Method | Path | Description | Response |
| --- | --- | --- | --- |
| `GET` | `/project` | List all projects | `Project[]` |
| `GET` | `/project/current` | Get the current project | `Project` |

### Sessions

| Method | Path | Description | Notes |
| --- | --- | --- | --- |
| `GET` | `/session` | List all sessions | Returns `Session[]` |
| `POST` | `/session` | Create a new session | body: `{ parentID?, title? }` |
| `GET` | `/session/:id` | Get session details | Returns `Session` |
| `DELETE` | `/session/:id` | Delete a session | Returns `boolean` |
| `POST` | `/session/:id/fork` | Fork an existing session at a message | Returns `Session` |
| `POST` | `/session/:id/abort` | Abort a running session | Returns `boolean` |
| `POST` | `/session/:id/share` | Share a session | Returns `Session` |
| `GET` | `/session/:id/diff` | Get the diff for this session | Returns `FileDiff[]` |
| `POST` | `/session/:id/summarize` | Summarize the session | Returns `boolean` |
| `POST` | `/session/:id/revert` | Revert a message | Returns `boolean` |
| `POST` | `/session/:id/permissions/:permissionID` | Respond to a permission request | Returns `boolean` |

### Messages

| Method | Path | Description | Notes |
| --- | --- | --- | --- |
| `GET` | `/session/:id/message` | List messages in a session | Returns messages + parts |
| `POST` | `/session/:id/message` | Send a message and wait for response | Returns message + parts |
| `POST` | `/session/:id/prompt_async` | Send a message asynchronously (no wait) | Returns `204 No Content` |
| `POST` | `/session/:id/command` | Execute a slash command | Returns message + parts |
| `POST` | `/session/:id/shell` | Run a shell command | Returns message + parts |

### TUI

The `/tui` endpoint family drives the TUI programmatically (used by IDE plugins):

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/tui/append-prompt` | Append text to the prompt |
| `POST` | `/tui/submit-prompt` | Submit the current prompt |
| `POST` | `/tui/clear-prompt` | Clear the prompt |
| `POST` | `/tui/execute-command` | Execute a command |
| `POST` | `/tui/show-toast` | Show toast notification |
| `GET` | `/tui/control/next` | Wait for the next control request |
| `POST` | `/tui/control/response` | Respond to a control request |
| `POST` | `/tui/open-help` | Open the help dialog |
| `POST` | `/tui/open-sessions` | Open the session selector |
| `POST` | `/tui/open-themes` | Open the theme selector |
| `POST` | `/tui/open-models` | Open the model selector |

### Events

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/event` | Server-sent events stream. First event is `server.connected`, then bus events |

### Files

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/find?pattern=<pat>` | Search for text in files |
| `GET` | `/find/file?query=<q>` | Find files and directories by name |
| `GET` | `/find/symbol?query=<q>` | Find workspace symbols |
| `GET` | `/file?path=<path>` | List files and directories |
| `GET` | `/file/content?path=<p>` | Read a file |

### LSP, Formatters & MCP

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/lsp` | Get LSP server status |
| `GET` | `/formatter` | Get formatter status |
| `GET` | `/mcp` | Get MCP server status |
| `POST` | `/mcp` | Add MCP server dynamically |

### Auth

| Method | Path | Description |
| --- | --- | --- |
| `PUT` | `/auth/:id` | Set authentication credentials |
