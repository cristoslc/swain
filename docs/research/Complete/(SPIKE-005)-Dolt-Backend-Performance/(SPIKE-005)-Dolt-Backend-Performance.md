---
title: "Dolt Backend Performance in Beads"
artifact: SPIKE-005
status: Complete
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
question: "Can the dolt backend overwhelm problem in bd be resolved upstream, or do we need a local workaround?"
gate: Pre-MVP
risks-addressed:
  - bd write latency degrades agent flow when dolt auto-commits accumulate
  - dolt GC or compaction may stall during long sessions
depends-on: []
evidence-pool: ""
---

# Dolt Backend Performance in Beads

## Question

The dolt backend in bd (beads) gets overwhelmed during sustained agent sessions — writes slow down, queries lag, and the database can become unresponsive. Is this a known issue in the beads project? Are there configuration knobs, upstream fixes, or alternative storage backends that resolve it?

## Go / No-Go Criteria

- **Go (upstream fix exists):** A beads release or configuration change reduces p95 write latency to <200ms under sustained agent workload (50+ writes/session). Adopt the fix.
- **Go (workaround viable):** A local mitigation (batch writes, async commits, periodic GC) keeps bd responsive without forking beads. Document and implement.
- **No-Go:** Neither upstream nor local fix brings latency under threshold → trigger pivot.

## Pivot Recommendation

If dolt cannot be stabilized: evaluate switching bd's storage backend to SQLite (which beads also supports) for local single-agent use, reserving dolt for multi-agent sync scenarios only. File an ADR capturing the decision.

## Investigation Threads

1. **Upstream issues** — Search the beads GitHub repo for open/closed issues related to dolt performance, GC, compaction, or write amplification.
2. **Configuration** — Check if dolt exposes tuning knobs (GC interval, WAL size, commit batching) that bd surfaces or could surface.
3. **Alternative backends** — Does beads support SQLite or other lightweight backends? What's the migration path?
4. **Profiling** — Reproduce the slowdown locally, capture timing data, identify the bottleneck (dolt commit? index rebuild? disk I/O?).

## Findings

### Root Cause: Server Lifecycle Thrashing

The problem is **not** dolt's write performance or GC — it's bd's server lifecycle management. Evidence from local logs:

- **5,450 server start attempts** in a single 9-hour session (for a database with 18 issues)
- **2 dolt server processes** running simultaneously on different ports
- **23 stale circuit breaker files** in `/tmp/`, 6 in tripped state
- **8.1 MB / 78K lines** of log from pure restart churn
- The database itself is tiny: **1.5 MB, 90 dolt commits, 18 issues**

Each `bd` command calls `EnsureRunning()` which attempts to start a new server, even when one is already running. This creates a restart storm that causes the observed slowdowns.

### Upstream Fixes (already available)

| Issue | Fix | Version |
|-------|-----|---------|
| [#2324](https://github.com/steveyegge/beads/issues/2324) — idle-monitor shuts down server every ~30 min, tripping circuit breaker | Daemon infrastructure removed | v0.59.0 |
| [#2504](https://github.com/steveyegge/beads/issues/2504) — race in `KillStaleServers()` outside flock causes journal corruption | Orphan cleanup moved inside flock | v0.60.0 |

We are already on **bd v0.60.0** and **dolt 1.83.0**, so these fixes are present. The restart storm may be residual from before the upgrade, or a remaining edge case.

### Configuration: Batch Auto-Commit

bd exposes `--dolt-auto-commit` with three modes:
- `off` — no auto-commits
- `on` — commit after each write (current default)
- **`batch`** — defer commits, flush on SIGTERM/SIGHUP (added v0.56.1)

Batch mode was specifically designed to reduce commit overhead in high-write scenarios.

### Alternative Backends: Dead End

- **SQLite in mainline bd**: Permanently removed by maintainer
- **no-db/JSONL mode**: Broken upstream ([#534](https://github.com/steveyegge/beads/issues/534))
- **beads_rust (`br`)**: Community Rust fork using SQLite (719 stars), viable escape hatch but loses version history and remote sync
- **Export path**: `bd export` → JSONL → `bd init --from-jsonl` provides roundtrip migration

### Dolt Performance Profile

Dolt handles ~300 writes/sec max with serialized writes. Our 18-issue database is nowhere near this ceiling. Auto-GC is on by default since dolt 1.75 (triggers at 125MB growth). No GC or memory tuning needed at our scale.

## Recommendation: Go (workaround)

### Immediate actions (no code changes)

1. `bd dolt killall` then `bd dolt start` — clean single-server state
2. `rm /tmp/beads-dolt-circuit-*.json` — purge stale circuit breakers
3. Add `dolt-auto-commit: batch` to `.beads/config.yaml`
4. Truncate `.beads/dolt-server.log` (8.1 MB of restart noise)
5. `brew upgrade dolt` (1.83.0 → 1.83.5)

### If problems persist

6. File upstream issue on steveyegge/beads with the 5,450-restart log evidence
7. Consider `beads_rust` (`br`) as SQLite-backed fallback (last resort)

### Do NOT pursue

- no-db/JSONL mode (broken upstream)
- Dolt GC tuning (1.5 MB database, irrelevant)
- Dolt memory/connection tuning (97 MB RSS is fine)
- SQLite in mainline bd (removed by maintainer)

## Sources

- [Beads Issue #2324 — Server Shutdown](https://github.com/steveyegge/beads/issues/2324)
- [Beads Issue #2504 — Journal Corruption](https://github.com/steveyegge/beads/issues/2504)
- [Beads Issue #534 — No-DB Mode Broken](https://github.com/steveyegge/beads/issues/534)
- [Beads Discussion #1836 — SQLite Compatibility](https://github.com/steveyegge/beads/discussions/1836)
- [Dolt Auto-GC Announcement](https://www.dolthub.com/blog/2025-02-28-announcing-automatic-gc-in-sql-server/)
- [Dolt Server Configuration](https://docs.dolthub.com/sql-reference/server/configuration)
- [Dolt Performance in the Wild](https://www.dolthub.com/blog/2021-10-27-dolt-perf-in-the-wild/)
- [beads_rust (SQLite fork)](https://github.com/Dicklesworthstone/beads_rust)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-12 | — | Initial creation |
| Active | 2026-03-12 | — | Investigation starting |
| Complete | 2026-03-12 | 4831536 | Transition to Complete |
