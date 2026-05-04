---
title: Git Worktrees
url: https://www.getagentcraft.com/docs/features/worktrees
fetched: 2026-05-04
type: documentation
---

# Git Worktrees

Spawn heroes in different git worktrees.

Git worktrees let you have multiple working directories for the same repository. AgentCraft supports this by scanning sessions from all worktrees, displaying worktree info in the UI, and letting you spawn heroes in specific worktrees.

## Spawning in a Worktree

Press R with the Town Hall selected to open the worktree picker. Select a worktree to spawn a new hero in that directory.

You can also spawn heroes in specific worktrees from the SpawnModal by selecting the target worktree before spawning.

## Automatic Detection

AgentCraft detects git worktrees automatically at startup by running git worktree list. Sessions from all worktrees appear in the hero roster, each tagged with their source worktree.

## UI Indicators

- InfoPanel — When a hero is selected, the info panel shows which worktree it's working in
- HeroRoster — The roster tooltip includes the worktree name
- Each worktree has its own project identifier, so sessions are naturally separated

## Refreshing Worktrees

If you create a new worktree after starting the server, it won't be detected automatically. You can refresh the worktree list without restarting:

```
curl -X POST http://localhost:2468/admin/refresh-worktrees
```

## How It Works

Claude Code stores sessions in ~/.claude/projects/{projectIdentifier}/ where projectIdentifier is the path with slashes replaced by dashes. Each worktree has its own project identifier, so sessions are naturally separated.

The SessionScanner caches worktree paths on construction and scans session directories for each worktree. Sessions are tagged with their source worktree path, which is propagated to the frontend via the session_roster WebSocket event.

## Spawn Validation

When spawning an internal hero with a workingDir parameter, the path is validated against known worktrees. Invalid paths are rejected to prevent spawning heroes in arbitrary directories.