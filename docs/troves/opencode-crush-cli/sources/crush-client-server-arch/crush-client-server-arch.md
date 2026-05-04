---
source-id: "crush-client-server-arch"
title: "Crush Client-Server Architecture (v0.55.0 Experimental)"
type: web
url: "https://github.com/charmbracelet/crush/releases/tag/v0.55.0"
fetched: 2026-04-08T00:00:00Z
---

# Crush Client-Server Architecture

Version 0.55.0 (April 2, 2026) introduces an experimental server-client architecture behind the `CRUSH_CLIENT_SERVER=1` environment variable.

## Overview

From the release notes:

> If you run Crush with `CRUSH_CLIENT_SERVER=1`, it'll now run via a brand new server-client architecture.
>
> Keep in mind, though, this is **VERY experimental**! There are known bugs when using Crush in this mode. We'll be polishing it with time and only make it the default once it's stable.

## Implementation Details

The commit history shows:

- `feat(server): initial implementation of Crush RPC server/client` (0f2e2f0)
- `feat: add AppWorkspace implementation of Workspace interface gated behind CRUSH_CLIENT_SERVER env var` (9a63da5)
- `feat: add generated swagger docs and serve them in the server` (248d8b9)
- `feat: send server client version info` (1b37d55)

## Architecture Components

| Component | Description |
|-----------|-------------|
| **RPC Server** | New RPC layer replacing direct app access |
| **AppWorkspace** | Workspace interface implementation for client-server mode |
| **Swagger docs** | Auto-generated API documentation served by the server |
| **Proto encoding** | Sessions encoded in protocol buffer format |
| **Client methods** | Migrated from direct app access to client API |

## Migration

Commands are being refactored to use the client API:

- `crush run` — migrated to use client API instead of direct app access
- `crush login` — migrated to use client API
- `crush --continue` / `crush --session` — work in client-server mode

## How to Enable

```bash
CRUSH_CLIENT_SERVER=1 crush
```

## Current Status

- **Experimental**: Not the default behavior
- **Known bugs**: Expected issues in this mode
- **Goal**: Will become default once stable

## Design Pattern

This follows the same architectural pattern as OpenCode:

- OpenCode always runs a server alongside the TUI
- Crush is evolving toward the same client-server split
- The TUI becomes a client of the RPC server
- External clients can connect via `--host` flag

## Related Files

- `internal/cmd/server.go` — server command implementation
- `internal/server/` — RPC server implementation
- `internal/backend/` — agent, session, permission, event logic (refactored from app)

## Comparison to OpenCode

| Aspect | OpenCode | Crush (experimental) |
|--------|----------|----------------------|
| Server by default | Yes (always running) | No (only with `CRUSH_CLIENT_SERVER=1`) |
| TUI as client | Yes | Yes (in client-server mode) |
| HTTP API | Yes (OpenAPI 3.1) | Yes (Swagger docs generated) |
| External clients | Yes (`opencode attach`) | Yes (`crush --host`) |
| Transport | HTTP/REST | RPC (protocol not yet documented) |