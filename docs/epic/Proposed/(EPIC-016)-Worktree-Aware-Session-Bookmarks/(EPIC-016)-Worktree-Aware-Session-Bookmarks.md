---
title: "Worktree-Aware Session Bookmarks"
artifact: EPIC-016
track: container
status: Proposed
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
parent-vision: VISION-001
parent-initiative: INITIATIVE-013
success-criteria:
  - swain-session bookmarks capture the active worktree path alongside context, not just main-tree coordinates
  - Restoring a bookmark in a different worktree (or from main) routes the operator to the correct worktree
  - Bookmark format is backward-compatible — old bookmarks without a worktree field load without error
  - swain-doctor detects stale bookmarks pointing to pruned worktrees and offers cleanup
linked-artifacts:
  - EPIC-036
  - SPIKE-048
  - SPIKE-019
depends-on-artifacts:
  - EPIC-015
addresses: []
trove: ""
---

# Worktree-Aware Session Bookmarks

## Goal / Objective

Session bookmarks saved by swain-session are currently worktree-blind: they record artifact IDs and file paths relative to the main checkout. When an operator works across multiple worktrees — the default since EPIC-015 — bookmarks silently resolve against the wrong tree or break entirely on restore.

This epic extends the bookmark format and restore flow so that context captured in a worktree stays anchored to that worktree, and the restore path gracefully handles the case where the worktree no longer exists.

## Scope Boundaries

**In scope:**
- Bookmark schema extension: add optional `worktree` field (absolute path + branch name)
- Bookmark write path: detect current worktree and populate the field when writing
- Bookmark restore path: route operator to correct worktree; warn if pruned
- swain-doctor: detect bookmarks referencing missing worktrees; offer cleanup or re-anchor guidance
- Backward compatibility: bookmarks without `worktree` field continue to work unchanged

**Out of scope:**
- Auto-creating pruned worktrees on restore (operator decision, not agent action)
- Multi-worktree session tabs (out of scope for this epic; future work)
- Changes to the tmux tab naming behavior in swain-session beyond what bookmark restore requires

## Child Specs

Updated as Agent Specs are created under this epic.

## Key Dependencies

- EPIC-015 (Automatic Worktree Lifecycle) — establishes the worktree model that bookmarks must now track
- SPIKE-019 — research spike to determine the correct design before implementation

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation; SPIKE-048 kicks off research |
