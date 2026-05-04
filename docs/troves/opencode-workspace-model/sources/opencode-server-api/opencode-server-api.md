---
source-id: "opencode-server-api"
title: "OpenCode Server API — Workspace-Relevant Endpoints"
type: web
url: "https://opencode.ai/docs/server/"
fetched: 2026-04-20T12:00:00Z
hash: ""
notes: "Condensation of the opencode server API docs focusing on workspace-relevant endpoints."
---

# OpenCode Server API — Workspace-Relevant Endpoints

## How the Server Works

When you run `opencode`, it starts a TUI and a server. The TUI is the client that talks to the server. Running `opencode serve` starts a standalone server. The server exposes an OpenAPI 3.1 spec at `/doc`.

## Workspace Routing

The server routes requests to the correct workspace instance using the `x-opencode-directory` HTTP header. This header carries the directory path of the workspace the client wants to interact with.

## Project Endpoints

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| `GET` | `/project` | List all projects | `Project[]` |
| `GET` | `/project/current` | Get the current project (respects `x-opencode-directory`) | `Project` |

The `Project` type includes:
- `id` — stable project identifier (root commit hash)
- `worktree` — path to main repo
- `sandboxes` — array of workspace (worktree) directory paths
- `vcs` — version control system type

## Session Endpoints (Workspace-Scoped)

| Method | Path | Description | Notes |
|--------|------|-------------|-------|
| `GET` | `/session` | List all sessions | Returns `Session[]` |
| `POST` | `/session` | Create a new session | body: `{ parentID?, title? }` |
| `GET` | `/session/:id` | Get session details | Returns `Session` |
| `POST` | `/session/:id/fork` | Fork a session at a message | Returns `Session` |
| `POST` | `/session/:id/message` | Send a message and wait | Returns message + parts |

Sessions belong to a project. When a workspace (worktree) is active, sessions can be scoped to that workspace via the directory routing.

## Experimental Endpoints

The `/experimental/*` routes expose workspace management APIs including worktree creation, deletion, and reset. These are not yet part of the stable public API.

## Events

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/event` | SSE stream. First event is `server.connected`, then bus events including workspace/workspace-switch events |

## Key Implication for swain-helm

The server API does not have explicit "workspace" CRUD endpoints in the stable API. Workspace management happens through:
1. The `/project/current` endpoint with `x-opencode-directory` header for workspace routing
2. Experimental routes for worktree CRUD
3. The `/tui/*` endpoints for TUI control
4. Session creation is scoped to a project but workspace affinity is managed via directory headers