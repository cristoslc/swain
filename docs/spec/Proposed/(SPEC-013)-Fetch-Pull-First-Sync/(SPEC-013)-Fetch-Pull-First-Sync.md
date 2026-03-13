---
title: "Fetch/Pull-First Sync Behavior"
artifact: SPEC-013
status: Proposed
type: enhancement
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
parent-epic: EPIC-012
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
linked-artifacts:
  - SPIKE-017
depends-on-artifacts: []
---

# Fetch/Pull-First Sync Behavior

## Problem Statement

swain-push currently stages, commits, and pushes without first incorporating upstream changes. This can lead to push failures, merge conflicts discovered late, and divergent histories. The skill should always fetch and rebase before committing to ensure the local branch is up to date.

Additionally, "push" no longer describes the full behavior — the skill should be renamed to swain-sync to reflect its bidirectional nature.

## External Behavior

### swain-sync (new canonical skill)

1. Fetch upstream changes
2. Rebase local branch onto upstream (stash/pop dirty working tree if needed)
3. Stage changes, generate commit message from diff
4. Verify pre-commit hooks passed
5. Commit and push

### swain-push (deprecation alias)

A thin skill that:
1. Emits a deprecation warning: "swain-push is deprecated, use swain-sync instead"
2. Invokes swain-sync with all arguments forwarded

### Migration path

- swain-doctor detects references to "swain-push" in CLAUDE.md / AGENTS.md and suggests updating to "swain-sync"
- swain router accepts both `/swain-push` and `/swain-sync`
- Alias remains indefinitely (no removal timeline) but warns on every use

## Acceptance Criteria

- **Given** swain-sync is invoked, **when** there are upstream changes, **then** it fetches and rebases before committing
- **Given** the working tree is dirty when rebase is needed, **when** swain-sync runs, **then** it stashes, rebases, and pops cleanly
- **Given** a rebase conflict occurs, **when** swain-sync cannot auto-resolve, **then** it reports the conflict clearly and stops (does not force-push or drop changes)
- **Given** `/swain-push` is invoked, **when** the alias fires, **then** it emits a deprecation warning and delegates to swain-sync
- **Given** AGENTS.md references "swain-push", **when** swain-doctor runs, **then** it flags the stale reference and suggests updating

## Scope & Constraints

- Core behavior change is in the skill script and SKILL.md
- Router update in swain/SKILL.md to add swain-sync route
- AGENTS.md update to reference swain-sync
- Does not include security scanning (separate spec under EPIC-012)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-13 | 34f2d62 | Initial creation |
