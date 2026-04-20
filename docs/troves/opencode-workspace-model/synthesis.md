# Synthesis: OpenCode Workspace Model and swain-helm Interaction

## Key Findings

### 1. Workspaces ARE git worktrees — no separate abstraction

In OpenCode, a "workspace" is not a distinct concept from a git worktree. When you create a workspace in the desktop or web UI, OpenCode runs `git worktree add` under the hood, creates a branch named `opencode/<slug>`, and records the new directory in `Project.Info.sandboxes`. There is no workspace entity in the database — the workspace IS the worktree directory.

This means:
- Workspaces are fundamentally bound to git branches and directories.
- You cannot have a workspace without a worktree, and you cannot have a worktree without a branch.
- The workspace identity is the directory path, not a UUID or database ID.

### 2. The TUI has zero workspace management

The TUI is a single-terminal, single-project interface. It has:
- No workspace sidebar.
- No workspace creation.
- No workspace switching.
- No session list UI (issue #20238).

Feature request #20535 proposes Blender-style tabs for the TUI, but this is not implemented. When running `opencode` in a terminal, you get one project in one terminal. To work on multiple workspaces, you either:
- Open multiple terminal tabs and run `opencode` in each worktree directory.
- Use `opencode web` or `opencode desktop` to access the workspace-aware UI.
- Use `opencode serve` and connect programmatically via the SDK.

### 3. The server API supports workspace routing, not workspace CRUD

The stable server API provides:
- `GET /project` and `GET /project/current` — returns `Project` with `sandboxes` array.
- `GET /session` — lists sessions scoped to a project.
- All requests accept an `x-opencode-directory` header for workspace routing.

The server does NOT expose stable CRUD endpoints for workspaces. Worktree creation/management lives in:
- The `/experimental/*` routes (undocumented, evolving).
- The desktop/web UI frontend code (which calls internal routes).
- The `WorktreeAdaptor` control-plane interface (extensible via plugins).

### 4. Plugin-provided workspace adaptors exist

Since v1.4.4, plugins can register custom workspace adaptors that appear in the workspace creation UI. This is an extension point that swain-helm could potentially use to register itself as a workspace provider, injecting custom behavior when a workspace is created.

### 5. Remote workspace reconnection is maturing rapidly

The v1.4.x changelog shows active development on:
- Workspace routing (fixing requests going to wrong instance).
- Remote workspace reconnection with exponential backoff.
- Auth context propagation across workspaces.
- Sync ordering (wait for sync before returning writes).

These are exactly the problems swain-helm needs to solve for bridging Zulip messages to the right opencode workspace.

## Points of Agreement

All sources agree on these facts:
- A workspace is a git worktree managed by opencode.
- Project identity is derived from the first git commit hash.
- The TUI lacks workspace features entirely.
- The server routes workspace requests via directory headers.
- Start commands run when worktrees are created.

## Points of Disagreement / Tension

1. **Naming confusion**: Users and issue reporters use "workspace" and "worktree" interchangeably, but some want workspace features that go beyond what worktrees provide (e.g., #10060 wants grouped worktrees across repos; this would need a workspace abstraction above the worktree).

2. **Stability of experimental APIs**: The workspace management endpoints are labeled experimental and may change. Building swain-helm on top of them carries risk.

3. **TUI vs. web/desktop feature gap**: The TUI team has not committed to workspace features (#20535 is open discussion). This means swain-helm should not assume TUI workspace support will arrive.

## Gaps

1. **No documented workspace API**: The stable server API does not document how to create, list, switch, or delete workspaces programmatically. The SDK has no `workspace.*` methods.

2. **No workspace session affinity**: Sessions belong to a project, not a workspace. Session-to-worktree routing is implicit via the `x-opencode-directory` header, not an explicit foreign key.

3. **No workspace state persistence**: There is no workspace-level config or state. Each workspace (worktree) inherits the project's `opencode.json` and `.opencode/` directory. Per-workspace configuration (custom base branch, symlinked files) was requested in #13592 but is not fully implemented.

4. **Remote env worktree path issues**: Worktrees created by the web UI are stored under `~/.local/share/opencode/worktree/` by default, which breaks in devContainers (#12759). No config option exists to control the worktree storage path.

## Implications for swain-helm

### Option A: One swain-helm session per workspace

Each opencode workspace (worktree) gets its own swain-helm bridge session. When a Zulip message arrives, the bridge routes it to the matching workspace by setting the `x-opencode-directory` header.

**Pros**: Clean isolation, matches opencode's own model, each workspace has its own branch and session context.

**Cons**: Requires the bridge to know about workspaces, needs workspace discovery via `/project`, needs to handle workspace creation/deletion lifecycle, may need UI for workspace selection from Zulip.

### Option B: One swain-helm session per project, workspace as a parameter

The bridge manages one session per project. When a message arrives, the operator includes a workspace hint (e.g., a Zulip topic prefix) that the bridge maps to a worktree directory.

**Pros**: Simpler bridge, fewer connections, one Zulip stream per project.

**Cons**: No session isolation, workspace context must be manually tracked, risk of routing messages to wrong workspace.

### Option C: Use opencode's worktree infrastructure directly

swain-helm itself creates and manages worktrees using opencode's `Worktree.create` (via the experimental API or by calling `git worktree add` directly). Each swain-helm "project bridge" owns one or more worktrees and creates opencode sessions within them.

**Pros**: Full control over workspace lifecycle, matches swain's own worktree discipline.

**Cons**: Duplicates worktree management that opencode already does, may conflict with worktrees created by the desktop/web UI, harder to coordinate.

### Recommended approach

**Option A with a pragmatic fallback**: Start with one bridge session per project (Option B) since opencode's workspace API is still experimental. Layer in workspace-specific routing later using the `x-opencode-directory` header pattern. The bridge should:

1. Discover the current project and its worktrees via `GET /project/current`.
2. Allow the operator to specify a worktree directory via Zulip topic or command.
3. Route messages with the `x-opencode-directory` header to target the correct workspace.
4. Defer workspace creation to the operator (who creates them via desktop/web/CLI), not the bridge.

This approach avoids depending on unstable workspace APIs while still supporting multi-workspace routing when the operator sets it up.