---
title: "Task Tracker Requirements and Alternatives"
artifact: SPIKE-006
status: Complete
author: cristos
created: 2026-03-12
last-updated: 2026-03-13
question: "What task tracking backend should swain-do use, given the requirements learned from SPIKE-001, SPIKE-002, and SPIKE-005?"
gate: Pre-MVP
risks-addressed:
  - bd/dolt runtime overhead is disproportionate to workload (5,450 server restarts for 18 issues)
  - Backlog.md lacks dependency tracking at the CLI surface
  - No evaluated alternative covers all swain-do requirements
evidence-pool: ""
linked-artifacts:
  - SPIKE-001
  - SPIKE-002
  - SPIKE-005
---

# Task Tracker Requirements and Alternatives

## Question

What task tracking backend should swain-do use, given the requirements learned from prior spikes?

## Requirements (derived from SPIKE-001, -002, -005)

### Must-have

1. **Dependency graph** — `ready` (unblocked tasks), `blocked` (what's blocking), `dep add/remove`. Kahn's algorithm or equivalent. This was the gap that blocked Backlog.md adoption (SPIKE-001).
2. **No runtime database** — No server process, no sockets, no pid files. bd's dolt server lifecycle is the root cause of the performance problems (SPIKE-005). Flat files, SQLite, or in-process storage only.
3. **Git-friendly storage** — Task state must be diffable, mergeable, and committable alongside code. No binary blobs, no out-of-band databases.
4. **Spec lineage tagging** — Tasks must be taggable with artifact IDs (`spec:SPEC-003`, `origin:EPIC-001`) and queryable by those tags.
5. **Claim/complete/abandon** — Atomic status transitions for agent workflow: claim a task, mark it done, or abandon it.
6. **Fast CLI** — <100ms for reads, <200ms for writes. Agent flow cannot tolerate latency.
7. **Multi-agent sync** — Concurrent agents must be able to read and write tasks without corruption or lost updates. Branch-aware merge, CRDTs, file-per-task with git merge, or equivalent. This is the one thing dolt does well — any replacement must match it.

### Should-have

8. **JSON output** — Structured output for programmatic consumption (no stdout parsing).
9. **Health check / doctor** — Self-repair command for data integrity.
10. **Label/metadata** — Free-form key-value pairs beyond status and dependencies.
11. **Export/import** — JSONL or similar for migration and backup.

### Nice-to-have

12. **MCP server** — Native Claude Code integration without CLI wrapping.
13. **Web/TUI board** — Visual task board (Kanban or similar).

### Explicitly NOT required

- Rich document storage (SPIKE-002 settled this — artifacts stay in `docs/`)
- Per-type status workflows (that's swain-design's job, not the tracker's)
- Git history / version control of task state (git already provides this if storage is files)

## Candidates to evaluate

1. **Backlog.md + upstream contribution** — Contribute `ready`/`blocked`/`dep` commands (~180 LOC). Addresses must-haves 1-6 if accepted.
2. **GitHub Issues + gh CLI** — Already have `gh`. Dependencies via "blocked by #N" syntax. No runtime. But: API latency, rate limits, requires network.
3. **Plain markdown / YAML files** — Custom format in `docs/tasks/` or similar. swain-do parses directly. Zero dependencies. But: must build everything.
4. **Linear** — API-first, fast, has dependencies. But: SaaS, not git-native, requires API key.
5. **Taskwarrior** — Mature CLI task manager. Dependencies, JSON export, fast. But: custom binary storage (.task/), not markdown.
6. **Bespoke SQLite CLI** — Purpose-built for swain-do. SQLite file in repo (or .gitignored). Fast, dependency-aware, zero runtime. But: must build it.
7. **dolt-free bd** — Fork bd to strip dolt, use SQLite or flat files. Keeps the CLI surface. But: fork maintenance burden.
8. **Other** — Scan for tools not yet on the radar.

## Go / No-Go Criteria

- **Go**: A candidate meets all 7 must-haves and at least 2 should-haves, with migration path from bd.
- **No-Go**: No candidate meets the bar → build a bespoke solution (candidate 6).

## Pivot Recommendation

If no external tool fits: build a minimal SQLite-backed CLI (`swain-task`) purpose-built for swain-do's term mapping. ~500 LOC Python, zero runtime, ships with the skill. The swain-do abstraction layer already isolates the backend — swapping is cheap.

## Findings

### Evaluation Matrix

| Requirement | ticket | Seeds | Beans | Backlog.md | GitHub Issues | Taskwarrior | kbtz | bd fork |
|---|---|---|---|---|---|---|---|---|
| 1. Dependency graph | **Yes** | **Yes** | **Yes** | Partial | Partial | Yes | Yes | Yes |
| 2. No runtime DB | **Yes** | **Yes** | **Yes** | Yes | Yes (network) | Partial | No | Depends |
| 3. Git-friendly | **Yes** | **Yes** | **Yes** | Yes | No | No | No | Depends |
| 4. Spec lineage | **Yes** | **Yes** | Partial | Yes | Yes | Partial | No | Yes |
| 5. Claim/complete | Partial | **Yes** | **Yes** | Partial | No | No | Yes | Yes |
| 6. Fast CLI | **Yes** | Likely | **Yes** | Yes | No | No | Yes | Unknown |
| 7. Multi-agent sync | Partial | **Yes** | **Yes** | Partial | Yes | No | Yes | Partial |
| **Must-haves** | **5.5/7** | **6.5/7** | **6/7** | **4.5/7** | **3/7** | **2/7** | **5/7** | **4/7** |

### Rank 1: ticket (wedow/ticket)

647 stars, MIT, single bash script (~500 LOC). File-per-task markdown with YAML frontmatter in `.tickets/`.

**Strengths:**
- Full dependency graph: `tk dep`, `tk ready`, `tk blocked`, `tk dep tree`, `tk dep cycle`
- Native `--external-ref` and `--tags` for spec lineage tagging
- Built-in `tk migrate-beads` command
- Zero runtime dependencies (bash + coreutils)
- Single file — trivially vendorable into `skills/swain-do/bin/tk`

**Gaps:**
- Multi-agent sync relies on git merge only (no file locking) — mitigated by file-per-task format
- JSON output requires jq plugin, not native `--json` flag
- No health-check/doctor command
- No dedicated `abandon` command (`tk status <id> open` as workaround)
- Early stage (v0.3.2)

### Rank 2: Seeds (jayminwest/seeds)

56 stars, MIT, TypeScript/Bun. JSONL storage in `.seeds/`. Built as a Beads replacement.

**Strengths:**
- Best multi-agent story: advisory file locks (O_CREAT|O_EXCL), atomic writes (temp+rename), dedup-on-read after `merge=union`
- Full dependency graph: `sd dep add/remove/list`, `sd block/unblock`, `sd ready`, `sd blocked`
- Native `--json` on all commands
- Built-in `sd migrate-from-beads`
- `sd doctor` for health checks

**Gaps:**
- Requires Bun runtime (additional dependency)
- JSONL less human-readable than file-per-task markdown
- Very small community (56 stars, 2 contributors — one is Claude)
- No `--external-ref` field (must use labels for spec lineage)

### Rank 3: Beans (hmans/beans)

579 stars, Go, file-per-task markdown in `.beans/`. GraphQL engine + TUI.

**Strengths:**
- ETag-based optimistic locking for concurrency
- GraphQL engine for complex queries
- Built-in TUI board
- Active development

**Gaps:**
- No CLI dep commands (TUI/GraphQL only)
- No spec lineage tagging
- No migration from bd
- "Does not accept contributions" — single maintainer, breaking changes expected

### Eliminated candidates

- **Backlog.md**: Still missing `ready`/`blocked`/`dep` CLI commands as of v1.40.0 (4.5/7)
- **GitHub Issues**: API latency (~200-500ms) violates fast CLI requirement, requires network (3/7)
- **Taskwarrior 3.0**: 25x performance regression (0.085s → 2.176s), SQLite not git-friendly (2/7)
- **kbtz**: SQLite storage not git-friendly, 1 star, no labels/tags (5/7)
- **dolt-free bd fork**: ~3000+ lines of Dolt coupling, 4-6 weeks effort, exceeds bespoke build cost (4/7)
- **dstask**: No dependency tracking, "not for collaboration" (eliminated)
- **git-bug**: No dependency/blocking between bugs, GPLv3 (eliminated)
- **Linear**: SaaS, not git-native, requires network (eliminated)

### Recommendation

**ticket is the top pick** — closest to all 7 must-haves with the lowest complexity and maintenance burden. The multi-agent gap (no file locking) is the main risk, but file-per-task markdown means concurrent creates never conflict, and concurrent edits to the *same* task are rare in practice.

**Seeds is the insurance policy** — if multi-agent sync proves critical in practice, Seeds has the strongest concurrency story but adds a Bun dependency.

**Suggested approach:**
1. Vendor `tk` (single bash file) into swain-do
2. Prototype the swain-do adapter against `tk` commands
3. Run `tk migrate-beads` on the current `.beads/` data
4. If multi-agent conflicts emerge in practice, evaluate adding advisory locks to `tk` (~50 LOC patch) or switching to Seeds

## Sources

- [ticket (wedow)](https://github.com/wedow/ticket) — 647 stars, MIT
- [Seeds (jayminwest)](https://github.com/jayminwest/seeds) — 56 stars, MIT
- [Beans (hmans)](https://github.com/hmans/beans) — 579 stars, Go
- [Backlog.md (MrLesk)](https://github.com/MrLesk/Backlog.md) — 5.1k stars, MIT
- [kbtz (virgil-king)](https://github.com/virgil-king/kbtz) — 1 star, Apache-2.0
- [Taskwarrior perf issue #3329](https://github.com/GothenburgBitFactory/taskwarrior/issues/3329)
- [GitHub Issues dependencies](https://github.blog/changelog/2025-08-21-dependencies-on-issues/)
- [gh CLI dep flags request #11757](https://github.com/cli/cli/issues/11757)
- [Beads architecture (DeepWiki)](https://deepwiki.com/steveyegge/beads)
- [HN: ticket replacing Beads](https://news.ycombinator.com/item?id=46487580)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-12 | — | Initial creation |
| Active | 2026-03-12 | — | Investigation starting |
| Complete | 2026-03-13 | ad0f05f | Findings captured, ADR-002 adopted ticket (tk) |
