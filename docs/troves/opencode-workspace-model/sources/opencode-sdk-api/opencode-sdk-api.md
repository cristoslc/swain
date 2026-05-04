---
source-id: "opencode-sdk-api"
title: "OpenCode JS SDK — Workspace-Relevant API Surface"
type: web
url: "https://opencode.ai/docs/sdk/"
fetched: 2026-04-20T12:00:00Z
hash: ""
notes: "Condensation of the opencode SDK docs focusing on workspace, project, and session APIs relevant to swain-helm."
---

# OpenCode JS SDK — Workspace-Relevant API Surface

## Creating a Client

```typescript
import { createOpencode } from "@opencode-ai/sdk"
const { client } = await createOpencode()
```

Or connecting to an existing server:

```typescript
import { createOpencodeClient } from "@opencode-ai/sdk"
const client = createOpencodeClient({ baseUrl: "http://localhost:4096" })
```

## Project API

| Method | Description | Response |
|--------|-------------|----------|
| `project.list()` | List all projects | `Project[]` |
| `project.current()` | Get current project | `Project` |

The `Project` type contains `id`, `worktree` (main repo path), and `sandboxes` (worktree paths).

## Session API

| Method | Description | Notes |
|--------|-------------|-------|
| `session.list()` | List sessions | Returns `Session[]` |
| `session.create({ body })` | Create session | body: `{ parentID?, title? }` |
| `session.prompt({ path, body })` | Send prompt | Supports structured output, `noReply` for context injection |

## Key Gap for swain-helm

The SDK does not expose explicit workspace CRUD methods. There is no `workspace.list()`, `workspace.create()`, or `workspace.switch()`. The server routes workspace requests via HTTP headers, not via distinct resource endpoints.

To manage workspaces programmatically, swain-helm would need to:
1. Use the project API to discover existing worktrees (`Project.sandboxes`)
2. Directly call the experimental API endpoints for worktree CRUD (not in the SDK)
3. Use session APIs with directory scoping to route messages to the correct workspace