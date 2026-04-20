---
source-id: "opencode-project-worktree-internals"
title: "OpenCode Project and Worktree Management Internals"
type: web
url: "https://deepwiki.com/sst/opencode/2.7-project-and-worktree-management"
fetched: 2026-04-20T12:00:00Z
hash: ""
notes: "DeepWiki page on the internal project detection system, worktree creation flow, and instance management. Source code references from the sst/opencode fork (pre-fork)."
---

# OpenCode Project and Worktree Management Internals

## Project Detection

When OpenCode starts in a directory, it discovers the project context:

1. **Git Discovery**: `Project.fromDirectory` uses `fs.up()` to find a `.git` directory starting from the current directory
2. **ID Caching**: Checks for a cached ID in the `opencode` file within the git directory
3. **Root Commit Query**: If no ID is cached, runs `git rev-list --max-parents=0 HEAD`
4. **ID Generation**: First root commit hash becomes the stable project ID, written to cache
5. **Worktree Resolution**: Determines the `worktree` path using `git rev-parse --git-common-dir`

## Path Resolution

Three directory types are distinguished:

| Type | Description | Resolution Method |
|------|-------------|-------------------|
| **worktree** | Main repository location | `git rev-parse --git-common-dir` |
| **sandbox** | Current working directory | `git rev-parse --show-toplevel` |
| **directory** | Specific path server was started in | Provided as input to `Instance.provide` |

When in a git worktree, `worktree` points to the main repo while `sandbox` points to the worktree checkout.

## Worktree Creation Flow

The `Worktree.create` function:

1. Generates a unique name via `candidate()`:
   - If a custom name is provided: slugified version
   - Otherwise: random human-readable slug via `Slug.create()`
2. Creates a branch named `opencode/<slug>`
3. Runs `git worktree add` to create the physical checkout
4. Optionally runs start commands (project-level + worktree-level)
5. Stores metadata about the new worktree

**Start Commands**: Projects can define a `start` command that runs in new worktrees (e.g., `npm install`). This comes from `Project.Info.commands.start` and can be overridden per-worktree via `Worktree.CreateInput.startCommand`.

## Control-Plane Workspace System

OpenCode implements an adaptor architecture for workspace management:

- `WorktreeAdaptor` bridges high-level workspace requests to the underlying `Worktree.Service`
- The experimental routes at `/experimental/*` expose workspace creation/management APIs
- Plugins can register custom workspace adaptors that appear in workspace creation

## Key Source Files

- `packages/opencode/src/project/project.ts` — Project detection and data model
- `packages/opencode/src/worktree/index.ts` — Worktree creation and management
- `packages/opencode/src/project/instance.ts` — Instance context and routing
- `packages/opencode/src/control-plane/adaptors/worktree.ts` — Adaptor architecture
- `packages/opencode/src/server/routes/experimental.ts` — Experimental workspace API routes