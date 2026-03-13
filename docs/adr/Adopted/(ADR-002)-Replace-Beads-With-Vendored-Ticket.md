---
title: "Replace Beads with Vendored Ticket"
artifact: ADR-002
status: Adopted
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
evidence-pool: ""
linked-artifacts:
  - SPIKE-001
  - SPIKE-002
  - SPIKE-005
  - SPIKE-006
depends-on-artifacts: []
---

# Replace Beads with Vendored Ticket

## Context

swain-do uses bd (beads) for task tracking. Beads uses Dolt — a git-for-databases SQL engine — as its storage backend. In practice, Dolt's server lifecycle management causes severe performance problems:

- 5,450 server restart attempts in a single 9-hour session for 18 issues (SPIKE-005)
- 23 stale circuit breaker files, 2 orphan server processes
- 8.1 MB of log churn from restart storms
- 97 MB RSS for a 1.5 MB database

Four spikes investigated the problem space:

- **SPIKE-001**: Evaluated Backlog.md as a replacement — dependency tracking CLI commands are missing (ready/blocked/dep), blocking adoption
- **SPIKE-002**: Evaluated Backlog.md for artifact management — fundamental impedance mismatch, rejected
- **SPIKE-005**: Diagnosed dolt performance — root cause is server lifecycle, not query performance. Applied workarounds (batch auto-commit, server cleanup) but the architectural overhead remains
- **SPIKE-006**: Broadened search across 10+ candidates with 7 must-have requirements including dependency graphs, no runtime database, git-friendly storage, and multi-agent sync

## Decision

**Replace bd (beads) with a vendored copy of [ticket](https://github.com/wedow/ticket) (wedow/ticket), extended with atomic claim support.**

Specifically:

1. **Vendor** the `tk` bash script (~500 LOC) into `skills/swain-do/bin/tk`
2. **Add `tk claim`** using POSIX `mkdir`-based locking (~20 LOC) for multi-agent atomic task acquisition
3. **Add `tk release`** to clean up claim locks
4. **Map** swain-do's term table from `bd` commands to `tk` commands
5. **Migrate** existing `.beads/` data via `tk migrate-beads`
6. **Remove** the beads integration section from AGENTS.md
7. **Update** swain-doctor, swain-init, and swain-preflight to reference `.tickets/` instead of `.beads/`
8. **Submit** the claim commands as an upstream PR (courtesy contribution, not a dependency)

### Why ticket?

- **File-per-task markdown with YAML frontmatter** — maximally git-friendly, human-readable, diffable
- **Full dependency graph** — `tk ready`, `tk blocked`, `tk dep tree`, `tk dep cycle`
- **Zero runtime dependencies** — bash + coreutils, no server process, no database
- **Native spec lineage** — `--external-ref` and `--tags` support `spec:SPEC-003` tagging
- **Built-in beads migration** — `tk migrate-beads` command
- **Vendorable** — single file, trivial to audit and patch

## Alternatives Considered

### Keep bd (beads) with workarounds
Applied batch auto-commit, server cleanup, dolt upgrade in SPIKE-005. Reduces symptoms but doesn't address the architectural mismatch: a full SQL database server for a flat list of tasks. The dolt server lifecycle will continue to cause issues as session lengths increase.

### Seeds (jayminwest/seeds)
Ranked #2 in SPIKE-006. Strongest multi-agent story (advisory locks, atomic writes, dedup-on-read). But requires Bun runtime (additional dependency), uses JSONL (less human-readable than file-per-task), and has a very small community (56 stars, 2 contributors — one is Claude). Higher dependency risk.

### Beans (hmans/beans)
Ranked #3. GraphQL engine, ETag-based concurrency, TUI. But no CLI dep commands (TUI/GraphQL only), no spec lineage tagging, doesn't accept contributions, and breaking changes are expected. Too volatile.

### Backlog.md + upstream contribution
Blocked on missing `ready`/`blocked`/`dep` CLI commands since SPIKE-001. The internal engine supports it but the CLI doesn't expose it. Contributing upstream (~180 LOC) is possible but depends on maintainer acceptance timeline.

### Bespoke SQLite CLI
Would meet all requirements but requires building from scratch (~800-1200 LOC). ticket already exists and covers 5.5/7 must-haves out of the box, with the gap (atomic claims) addressable in ~20 LOC.

### Fork bd to strip Dolt
~3000+ lines of Dolt coupling in the beads codebase. Estimated 4-6 weeks to replace — exceeds bespoke build cost. Not viable.

## Consequences

### Positive

- **No server process** — eliminates the entire class of dolt lifecycle bugs
- **Human-readable storage** — tasks are markdown files readable in any editor
- **Zero install friction** — bash script, no brew/cargo/npm dependency
- **Git-native merge** — file-per-task means concurrent creates never conflict
- **Vendored = controlled** — no external dependency to break, version to track, or runtime to manage

### Accepted downsides

- **Lose Dolt's version history** — task state changes tracked by git commits instead of database history. This is sufficient for our use case.
- **Lose Dolt's cell-level merge** — file-per-task with git merge is coarser. In practice, two agents editing the same task simultaneously is rare; the `mkdir`-based claim mechanism prevents it for the common case.
- **Lose `bd dolt push/pull`** — remote sync becomes `git push/pull`. This is actually simpler.
- **Upstream drift risk** — vendored copy may diverge. Mitigated by ticket being a small, stable bash script. Monitor upstream releases periodically.
- **Major breaking change** — existing `.beads/` users must migrate. Migration path provided via `tk migrate-beads`.

### Migration path

A migration script and documentation must be provided:

1. `tk migrate-beads` converts `.beads/` data to `.tickets/` format
2. Release notes document the breaking change and migration steps
3. swain-doctor detects stale `.beads/` directories and offers cleanup guidance
4. One major version bump signals the breaking change

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Adopted | 2026-03-12 | — | Decision made based on SPIKE-001, -002, -005, -006 findings |
