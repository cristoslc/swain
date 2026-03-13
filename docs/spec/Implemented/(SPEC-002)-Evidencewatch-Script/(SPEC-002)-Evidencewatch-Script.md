---
title: "evidencewatch Script"
artifact: SPEC-002
status: Implemented
author: cristos
created: 2026-03-09
last-updated: 2026-03-11
parent-epic: EPIC-001
linked-research: []
linked-adrs: []
depends-on:
  - SPEC-001
addresses: []
swain-do: required
---

# evidencewatch Script

## Problem Statement

Evidence pools can grow unbounded and sources can go stale without anyone noticing. Need a monitoring script (like specwatch for artifacts) that detects oversized pools, stale sources, and manifest inconsistencies.

## External Behavior

A bash script at `skills/swain-search/scripts/evidencewatch.sh` with subcommands:

- `evidencewatch.sh scan` — check all pools for size, freshness, and consistency issues
- `evidencewatch.sh status` — summary of all pools (source count, last refreshed, health)

Exit codes: 0 = healthy, 1 = warnings found.

Output goes to stdout (summary) and `.agents/evidencewatch.log` (details).

### Configurable thresholds

Defaults (overridable via `.agents/evidencewatch.vars.json`):

| Threshold | Default | What it checks |
|-----------|---------|---------------|
| `max_sources_per_pool` | 20 | Source count per pool |
| `max_pool_size_mb` | 5 | Total pool directory size |
| `freshness_multiplier` | 1.5 | Sources past TTL * multiplier are flagged |

## Acceptance Criteria

1. **Given** a pool with >20 sources, **when** `evidencewatch.sh scan` runs, **then** it warns about oversized pool with source count.
2. **Given** a pool >5MB, **when** scan runs, **then** it warns about pool size.
3. **Given** a source past its TTL, **when** scan runs, **then** it flags the stale source with age and TTL.
4. **Given** a source file in `sources/` not listed in manifest, **when** scan runs, **then** it reports the orphaned file.
5. **Given** a manifest entry with no corresponding source file, **when** scan runs, **then** it reports the missing file.
6. **Given** all pools are healthy, **when** scan runs, **then** it exits 0 with "all pools healthy".
7. **Given** custom thresholds in `.agents/evidencewatch.vars.json`, **when** scan runs, **then** it uses the custom values.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-09 | — | Initial creation |
| Approved | 2026-03-11 | — | Approved for implementation |
| Implemented | 2026-03-13 | 93f39f5 | Transitioned — evidencewatch.sh fully implements all 7 AC |
