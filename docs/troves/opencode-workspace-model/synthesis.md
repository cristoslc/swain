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

### ADR-047 already decided: one session per worktree

ADR-047 (swain-helm Watchdog Architecture) already specifies the worktree lifecycle model:

- Each project bridge polls `git worktree list --porcelain` every 15s.
- New worktrees get a Zulip topic named after their branch.
- Removed worktrees result in session termination and cleanup.
- A project bridge holds exactly one opencode session per worktree.
- Trunk always has a session (topic: `trunk`).
- The watchdog does not manage worktrees — that is a per-project-bridge concern.

This means the architecture already accounts for worktree lifecycle. The question is not *whether* to support it, but *how* to implement the bridge side given what opencode's server actually exposes.

### How opencode's model maps to ADR-047

The opencode research confirms and clarifies several implementation details for the existing design.

**Worktree discovery:** The bridge's planned 15s `git worktree list --porcelain` poll is correct. OpenCode does not expose stable API endpoints for workspace enumeration. The `GET /project/current` endpoint returns `Project.sandboxes`, but this only lists worktrees that opencode itself created (under `~/.local/share/opencode/worktree/`). Worktrees created by `git worktree add` directly (which is what swain-do creates) may not appear in `sandboxes`. Polling `git worktree list` from the project root is therefore more reliable than querying opencode's API for worktree discovery.

**Session routing:** When the bridge sends a message to an opencode session for a specific worktree, it must set the `x-opencode-directory` header to the worktree's directory path. This is how opencode's own web/desktop clients route requests. Sessions belong to a project, but the directory header scopes them to a worktree. The bridge does not need opencode's workspace CRUD API to route messages — it just needs the header.

**Session creation per worktree:** The bridge creates one session per worktree by calling `POST /session` with the `x-opencode-directory` header set to the worktree path. OpenCode resolves this to the correct project and routes the session to that directory. This works whether the worktree was created by opencode's desktop UI or by `git worktree add`.

**Worktree creation is not the bridge's job:** ADR-047 correctly places worktree creation outside the bridge. The bridge discovers worktrees after they exist. This avoids the need to call opencode's experimental `/experimental/*` worktree endpoints. The bridge treats worktrees as a discovered fact, not a managed resource.

**Removed worktree cleanup:** When `git worktree list` shows a worktree is gone, the bridge should clean up its session. The opencode session for that worktree becomes orphaned (the workspace no longer exists on disk). The v1.4.8 changelog shows opencode now has "improved workspace session handling when a workspace no longer exists" — the bridge should simply delete its session reference and let opencode handle the orphan internally.

### Gaps the research reveals

1. **No stable programmatic worktree enumeration from opencode.** The bridge must use `git worktree list` rather than any opencode API. This is fine — `git worktree list --porcelain` is stable and always accurate.

2. **`Project.sandboxes` may not include swain-managed worktrees.** If swain creates worktrees outside of opencode's `~/.local/share/opencode/worktree/` directory, they won't appear in `sandboxes`. The bridge should not rely on `GET /project/current` for worktree discovery.

3. **Auth context propagation across worktrees is now supported.** Since v1.4.7, workspaces receive auth context, so the bridge does not need to re-authenticate per worktree session. A single auth at project level suffices.

4. **Plugin workspace adaptors are a future integration point.** Since v1.4.4, opencode plugins can register custom workspace adaptors. swain-helm could eventually register as a workspace adaptor so that creating a worktree from the desktop/web UI triggers bridge setup. This is a v2+ consideration.