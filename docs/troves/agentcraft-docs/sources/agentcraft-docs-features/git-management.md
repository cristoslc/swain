---
title: Git Management
url: https://www.getagentcraft.com/docs/features/git-management
fetched: 2026-05-04
type: documentation
---

# Git Management

Built-in stash and branch management without leaving AgentCraft.

AgentCraft includes built-in git tooling so you can manage stashes, branches, and commit history without leaving the game view.

## Stash Manager

The stash manager lets you create, apply, and manage git stashes directly from the UI.

| Action | Description |
| --- | --- |
| Create stash | Stash current changes with an optional message |
| Apply | Apply a stash without removing it from the list |
| Pop | Apply a stash and remove it from the list |
| Drop | Delete a stash without applying |

### Options

- Include untracked files — Optionally stash untracked files alongside staged/unstaged changes
- Per-worktree — Stashes are scoped to the active worktree when using git worktrees

## Branch Management

View and switch between branches from the UI. Create new branches, delete merged branches, and see the current branch status at a glance.

## Commit History

Browse recent commit history for the current branch with commit messages, authors, and timestamps.