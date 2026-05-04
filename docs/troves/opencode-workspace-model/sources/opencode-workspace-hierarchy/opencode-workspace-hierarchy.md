---
source-id: "opencode-workspace-hierarchy"
title: "OpenCode Workspace Hierarchy — Projects, Workspaces, and Sessions"
type: web
url: "https://deepwiki.com/anomalyco/opencode/9.3-workspace-hierarchy"
fetched: 2026-04-20T12:00:00Z
hash: ""
notes: "DeepWiki page describing the three-level hierarchy in OpenCode: Projects, Workspaces, and Sessions. Covers how these entities relate, how they are stored in UI state, and how the sidebar renders them."
---

# OpenCode Workspace Hierarchy

## Three-Level Organizational Hierarchy

OpenCode organizes work into three levels:

1. **Project** — The top-level unit, representing a Git repository. A project is identified by the SHA-1 hash of the first git commit (stable across clones). A project contains sessions and one or more workspaces.

2. **Workspace** — A workspace is a git worktree within a project. The "root" workspace is the main checkout; additional workspaces are sandboxes (git worktrees) created for isolated work. Workspaces are only shown when Git worktrees are enabled for the project in the desktop/web sidebar settings.

3. **Session** — A conversation with an AI agent, scoped to a project and optionally to a workspace. Sessions belong to the project but can be associated with a specific worktree directory.

### How Workspaces Relate to Worktrees

- Workspaces ARE git worktrees. There is no separate abstraction — a workspace in OpenCode is literally a `git worktree add` managed by the platform.
- The root workspace is the main checkout (where `opencode` was first run). Additional workspaces are created via the desktop/web UI "New Workspace" button, which calls `Worktree.create` internally.
- Each workspace gets its own random slug (e.g., `cosmic-lagoon`) and a branch named `opencode/<slug>`.
- The `Project.Info` type has a `sandboxes` array listing all active worktree directories for a project.

### Workspace Management in the UI

- In the desktop and web apps, workspaces appear as sub-items in a sidebar under the project.
- Workspaces can be reordered via drag-and-drop using `syncWorkspaceOrder`.
- The TUI does not have a sidebar — it is a single-terminal, single-project interface. There is no workspace switcher in the TUI.
- `opencode attach` can connect a TUI to a running server that has multiple projects/workspaces, but the TUI itself creates one server per invocation.

### Key Data Model Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | SHA-1 hash of first git commit, or `"global"` |
| `worktree` | string | Path to main repository (parent of `.git/commondir`) |
| `sandboxes` | string[] | Array of all active working directories |
| `commands.start` | string | Startup command for new worktrees |

### `x-opencode-directory` Header

The server uses the `x-opencode-directory` HTTP header to route requests to the correct workspace. When a workspace is selected in the web or desktop UI, the client sends this header with the workspace directory path. The server resolves it back to the root project, finds the matching sandbox, and routes accordingly.