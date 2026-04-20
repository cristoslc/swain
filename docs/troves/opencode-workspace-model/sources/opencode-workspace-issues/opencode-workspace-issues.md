---
source-id: "opencode-workspace-issues"
title: "OpenCode Workspace Feature Requests and Bug Reports"
type: web
url: "https://github.com/anomalyco/opencode/issues?q=workspace+worktree"
fetched: 2026-04-20T12:00:00Z
hash: ""
notes: "Aggregation of GitHub issues related to workspaces, worktrees, and the TUI/web gap. Multiple issues from anomalyco/opencode."
---

# OpenCode Workspace Feature Requests and Bug Reports

## Issue #14656 — The WorkSpace settings in OpenCode Web

- **Status**: Open, assigned to nexxeln
- **Summary**: No way to set a default workspace in OpenCode Web via config or CLI. You can navigate to a workspace via base64-encoded URL path, but it won't appear in the sidebar.
- **Key need**: Workspace configuration and persistent sidebar management for the web UI.

## Issue #13592 — Enhanced Workspace Support: Custom Settings & Creation Dialog

- **Status**: Closed (PR #13593)
- **Summary**: Workspace (worktree) support is limited — you can set a startup command, but names and branches are randomly generated.
- **Requested features**: Project-level default base branch, lists of files to symlink/copy to new worktrees, custom creation dialog prompting for workspace name and branch name, per-workspace base branch override.
- **Implementation plan**: Update database schema for `worktree_settings`, update `Worktree.create` logic, add UI dialogs.

## Issue #9965 — Allow "New Workspace" to be initialized from existing branch

- **Status**: Open
- **Summary**: New workspaces always branch off `main`. Users want to branch off `staging` or other branches, and to pull down existing remote/local branches as new worktrees directly.
- **Use case**: Teams that work off develop/staging branches.

## Issue #13343 — GitHub/Git Worktree & Branch Picker from Desktop/Web UI

- **Summary**: Request for a native GitHub integration allowing repo selection, branch picking, and automatic clone/pull with worktree creation from the UI. Currently all worktree management is manual.

## Issue #12759 — New worktree creation broken for remote envs

- **Summary**: In devContainers, creating a worktree via the WebUI creates the worktree but messages route to the main branch session instead of the worktree session.
- **Root cause**: Worktree paths are stored under `~/.local/share/opencode/worktree/` but remote envs expect `/workspace`.

## Issue #16182 — Worktree paths remain as separate projects in sidebar

- **Summary**: Web UI bug — worktrees opened via the project picker persist as top-level projects instead of collapsing under the root project. The backend correctly reports the sandbox relationship, but the UI collapse logic fails.

## Issue #13346 — Worktree sandbox directory triggers external_directory permission prompts

- **Summary**: Agent inside a worktree incorrectly requests `external_directory` permission for the worktree's own path under `~/.opencode`.

## Issue #20535 — Blender-Style Workspace Tabs for TUI

- **Summary**: Feature request for tab-based workspace switching in the TUI (currently TUI has no workspace management). Proposes Blender-style keyboard-driven tabs for multiple agents/sessions.
- **Relevance**: Directly addresses the TUI workspace gap.

## Issue #13723 — Allow specifying git branch when creating a new workspace

- **Summary**: Allow passing an explicit git branch name when creating a workspace. If branch exists locally and isn't checked out elsewhere, create a worktree for it. If it doesn't exist, create from current HEAD. Keep `opencode/*` managed branches separate from user-created branches.

## Issue #10060 — Grouped worktrees by workspaces

- **Summary**: Request for managing grouped worktrees across multiple repos (e.g., frontend + backend in a non-monorepo setup) from a single project context. Currently workspaces are limited to a single working directory per project.

## Issue #5608 — OpenCode-Desktop Remote Workspace

- **Summary**: Request for remote development workflow similar to VS Code Remote. opencode already decouples client and server, but the desktop app doesn't support connecting to a remote opencode server for a different project.

## Issue #20238 — Session list missing in TUI mode

- **Referenced by**: #20535 (Blender-style tabs). The TUI currently lacks session management features that the web/desktop UI has.

## Key Takeaways

1. **Workspaces are the same as git worktrees** — there is no separate workspace abstraction.
2. **The TUI has zero workspace support** — workspace creation, switching, and sidebar management are exclusive to the desktop and web apps.
3. **The server API does expose workspace routing** via `x-opencode-directory` header and experimental endpoints, but these are not documented in the public API yet.
4. **Worktree start commands exist** — `Project.Info.commands.start` runs when a new worktree is created, enabling per-project setup scripts.
5. **Branch naming for worktrees uses the `opencode/` prefix** — user-managed branches are separate from auto-generated ones.
6. **Remote environments (devContainers) have known issues** with worktree paths.