---
title: "Multi-Agent Collision Vectors"
artifact: SPIKE-022
track: container
status: Proposed
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
question: "What are the collision vectors when multiple agents operate in the same swain project, and what mitigation strategies are appropriate for a solo-operator context?"
gate: Pre-development
risks-addressed:
  - Two agents editing the same file simultaneously, producing corrupted or conflicting state
  - Race conditions on .tickets/ during concurrent claim/close operations
  - Conflicting git commits from agents operating in the same branch
  - Artifact index files (list-*.md) diverging under concurrent updates
  - session.json corruption from concurrent writes
linked-artifacts:
  - EPIC-020
  - EPIC-015
evidence-pool: ""
---

# Multi-Agent Collision Vectors

## Summary

<!-- Populated when transitioning to Complete. -->

## Question

What are the collision vectors when multiple agents operate in the same swain project, and what mitigation strategies are appropriate for a solo-operator context?

## Go / No-Go Criteria

**GO (build mitigations):**
- Real collision vectors exist that can cause data loss or corrupted state
- Mitigations are implementable without adding heavyweight dependencies (no distributed locks, no databases)
- The effort is proportional to the risk — focus on vectors that actually occur in practice

**NO-GO (defer):**
- Collision vectors are theoretical only — current usage patterns don't trigger them
- Git's own merge conflict resolution is sufficient for all practical cases
- Worktree isolation already prevents the dangerous cases

## Investigation Areas

### 1. File-level collision inventory

Map every shared mutable file in a swain project and classify by risk:
- `.tickets/*.md` — task state (claim, close, add-note)
- `docs/*/list-*.md` — artifact index files
- `.agents/session.json` — session state
- `AGENTS.md` — governance (rarely mutated, but cross-referenced)
- `skills-lock.json` — skill registry
- Source code files — during parallel implementation tasks
- Git state (`.git/`) — commits, branches, refs

For each: how likely is concurrent mutation? What happens if two agents write simultaneously?

### 2. tk (ticket) concurrency audit

Audit `tk claim`, `tk close`, `tk add-note` for atomicity:
- Does `tk claim` use atomic file operations (write-then-rename)?
- What happens if two agents `tk claim` the same ticket simultaneously?
- What happens if one agent `tk close` while another `tk add-note` on the same ticket?
- Are there TOCTOU (time-of-check-time-of-use) races?

### 3. Git concurrency under worktrees

When agents operate in separate worktrees sharing the same `.git` directory:
- Can two worktrees commit simultaneously without corruption?
- What happens when both try to push to the same remote branch?
- How do shared refs (tags, remote tracking branches) behave under concurrent access?
- Does `git worktree` provide any built-in locking?

### 4. Artifact index race conditions

When two agents both update a `list-*.md` index file:
- Both read the same version, append a row, write back — last write wins, first entry lost
- Mitigation options: lock files, append-only logs, index regeneration from filesystem state
- How does specgraph handle this? Can it regenerate indexes on demand?

### 5. Mitigation strategy evaluation

For each real collision vector, evaluate:
- **Worktree isolation** — can the operation be moved to an isolated worktree?
- **File locking** (flock/lockfile) — lightweight, local-only, POSIX-standard
- **Atomic file operations** (write-tmp-then-rename) — prevents partial writes
- **Regeneration** — don't protect the file, regenerate it from source of truth (e.g., regenerate indexes from filesystem)
- **Convention** — document which files agents should not touch concurrently, enforce via swain-doctor

### 6. Architecture overview update scope

Determine what needs to be added to the architecture overview:
- Concurrency model diagram (what's isolated, what's shared, how shared state is protected)
- Agent isolation boundaries (worktree = default, shared workdir = exceptional)
- Conventions for swain-dispatch and subagent-driven-development

## Findings

<!-- Populated during Active phase. -->

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation; informs EPIC-020 |
