---
title: "Multi-Agent Collision Vectors"
artifact: SPIKE-022
track: container
status: Active
author: cristos
created: 2026-03-14
last-updated: 2026-03-20
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
  - EPIC-038
trove: ""
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

### 3a. Integration atomicity (TOCTOU at merge time)

**Motivated by:** [EPIC-038](../../../epic/Active/(EPIC-038)-Priority-Roadmap-And-Decision-Surface/EPIC-038.md) retro — [SPEC-107](../../../spec/Active/(SPEC-107)-Sibling-Order-Ranking/SPEC-107.md) and [SPEC-108](../../../spec/Active/(SPEC-108)-Roadmap-Data-Model/SPEC-108.md) both modified `roadmap.py` in parallel worktrees. Both agents' tests passed in isolation. After sequential checkout/merge to main, [SPEC-108](../../../spec/Active/(SPEC-108)-Roadmap-Data-Model/SPEC-108.md)'s enrichment fields were missing — the second merge was textually clean but semantically broken.

**Core problem:** Git three-way merge guarantees textual conflict detection, not semantic consistency. Two agents can produce individually-correct, textually-non-overlapping changes that are semantically incompatible. No git mechanism catches this.

**Investigation threads:**
- **Serialized integration with test gates:** Can a local merge queue apply each agent's branch sequentially, running tests between each merge? (Analogous to GitHub merge queue / bors but local)
- **File-overlap analysis at dispatch time:** Read implementation plans, infer which files each task touches, serialize tasks with overlapping file sets instead of running them in parallel
- **Optimistic concurrency (CAS):** Record the base commit hash each agent started from; at integration time, reject if the target file was modified since that hash — forces re-run on the new base
- **Post-merge verification as fallback:** When prevention fails, grep for key deliverables and re-run tests in main context before claiming delivery. This is detection, not prevention — acceptable as a last line of defense but not the primary strategy
- **CI merge queue mechanisms:** Do GitHub merge queue, Mergify, or bors provide useful primitives? Could swain-dispatch integrate with them for remote agent results?

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

### Evidence: EPIC-038 worktree TOCTOU (2026-03-20)

**Incident:** During [EPIC-038](../../../epic/Active/(EPIC-038)-Priority-Roadmap-And-Decision-Surface/EPIC-038.md) Phase 1, [SPEC-107](../../../spec/Active/(SPEC-107)-Sibling-Order-Ranking/SPEC-107.md) (sort-order) and [SPEC-108](../../../spec/Active/(SPEC-108)-Roadmap-Data-Model/SPEC-108.md) (data model) were dispatched to parallel worktree agents. Both modified `roadmap.py`. Both agents reported success with passing tests.

**Failure mode:** After sequential checkout into main, SPEC-108's enrichment fields were missing from the merged result. The agent tested its worktree copy, not the integrated result. Git merge succeeded textually — no conflict markers — but the semantic result was incomplete.

**Classification:** TOCTOU — Time of Check (agent tests in isolated worktree) vs Time of Use (changes applied to main where another agent already mutated shared files).

**Key insight:** This is not preventable by git's merge machinery. Textually clean merges can be semantically broken. The fix must be at a higher layer — either preventing overlapping dispatch or verifying after integration.

**Source:** [EPIC-038 Phase 1 Retro](../../swain-retro/2026-03-20-epic-038-phase-1.md)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation; informs EPIC-020 |
| Active | 2026-03-20 | fa63b5a | Activated by EPIC-038 retro — concrete TOCTOU evidence in area 3a |
