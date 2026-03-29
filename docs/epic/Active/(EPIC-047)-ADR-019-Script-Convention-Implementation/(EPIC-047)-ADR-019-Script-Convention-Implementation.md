---
title: "ADR-019 Script Convention Implementation"
artifact: EPIC-047
track: implementation
status: Active
author: cristos
created: 2026-03-28
last-updated: 2026-03-28
parent-initiative: INITIATIVE-019
linked-artifacts:
  - ADR-019
  - EPIC-029
  - SPEC-136
  - SPEC-137
depends-on-artifacts: []
---

# ADR-019 Script Convention Implementation

## Goal

Implement the two-tier script convention defined in ADR-019 across the swain toolchain. Operator-facing scripts get `bin/` symlinks; agent-facing scripts get `.agents/bin/` symlinks. swain-doctor auto-repairs both, and swain-init bootstraps them on onboarding.

## Context

ADR-019 defines the convention but nothing implements the symlink lifecycle in consumer projects. SPEC-136/137/147 (EPIC-029) updated the paths that skills *reference*, but consumer projects have no mechanism to create or repair the symlinks. The Homelab project's doctor correctly reports `.agents/bin/swain-trunk.sh` as missing — because nothing creates it.

## Child Specs

| Spec | Title | Priority |
|------|-------|----------|
| SPEC-186 | Doctor `.agents/bin/` auto-repair | high |
| SPEC-187 | Init `.agents/bin/` bootstrap | medium |
| SPEC-188 | Doctor `bin/` auto-repair | medium |
| SPEC-189 | Migrate swain-box to `bin/` | low |
| SPEC-190 | Migrate all skills to `.agents/bin/` resolution | medium |

SPEC-186 is the minimum viable fix — it unblocks the release by making doctor self-heal the missing symlinks. SPEC-187 ensures new projects get them on first run. SPEC-188/189 extend the convention to operator-facing scripts. SPEC-190 completes the migration by replacing all `find`-based script lookups (~55 across 14 skills) with direct `.agents/bin/` resolution.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-28 | — | Created to implement ADR-019 distribution layer |
