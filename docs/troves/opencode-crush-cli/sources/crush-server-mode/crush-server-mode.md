---
source-id: "crush-server-mode"
title: "Crush Server — Headless HTTP API Mode"
type: web
url: "https://github.com/charmbracelet/crush"
fetched: 2026-04-08T00:00:00Z
---

# Crush Server Mode

Crush supports a server mode for headless operation, exposed via the `crush server` subcommand.

## CLI Reference

```
crush server [--flags]

FLAGS:
  -c --cwd       Current working directory
  -D --data-dir  Custom crush data directory
  -d --debug     Debug
  -h --help      Help for server
  -H --host      Server host (TCP or Unix socket) (unix:///tmp/crush-501.sock)
```

## Architecture

The server command starts a standalone Crush server without the TUI. From `internal/cmd/server.go`:

1. **Initialization**: Loads configuration via `config.Load()`, sets up logging to `~/.local/share/crush/crush.log`
2. **Host parsing**: Resolves `--host` flag to TCP or Unix socket via `server.ParseHostURL()`
3. **Server start**: Creates a `server.NewServer()` instance and calls `ListenAndServe()`
4. **Signal handling**: Listens for `os.Interrupt` and gracefully shuts down with 5-second timeout

## Host Options

The `--host` flag supports both TCP and Unix sockets:

- **TCP**: `--host 127.0.0.1:4096` or `--host 0.0.0.0:4096`
- **Unix socket**: `--host unix:///tmp/crush-501.sock` (default on macOS/Linux)

## Use Cases

- **CI/CD pipelines**: Run Crush headlessly in automated workflows
- **Remote access**: Start server on a remote machine, connect via client
- **IDE integration**: Drive Crush from an external editor/plugin
- **Shell scripting**: Non-interactive mode with `crush run` can connect to a running server

## Comparison to opencode

| Feature | Crush `crush server` | OpenCode `opencode serve` |
|---------|---------------------|---------------------------|
| Subcommand | `server` | `serve` |
| Default port | Not specified (uses `--host`) | `4096` |
| Unix socket | Yes (default) | Yes |
| OpenAPI spec | Not documented | `/doc` endpoint |
| TUI control API | Not documented | `/tui/*` endpoints |
| HTTP Basic auth | Not documented | `OPENCODE_SERVER_PASSWORD` |

## Related

- `crush run` — non-interactive mode (can use existing server via `--host` client connect)
- `crush --host <url>` — connect to a running server from the TUI
- `CRUSH_CLIENT_SERVER=1` — experimental client-server architecture (v0.55.0+)