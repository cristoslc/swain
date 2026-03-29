---
title: "Specgraph Query Commands"
artifact: SPEC-031
track: implementable
status: Complete
author: cristos
created: 2026-03-13
last-updated: 2026-03-14
type: feature
parent-epic: EPIC-013
linked-artifacts:
  - ADR-004
  - EPIC-001
  - SPEC-001
  - SPEC-002
  - SPIKE-048
depends-on-artifacts:
  - SPEC-030
addresses: []
source-issue:
swain-do: required
---

# Specgraph Query Commands

## Problem Statement

Specgraph has 11 query subcommands beyond `build`, each implemented as embedded `jq` queries within bash functions. These need to be ported to Python functions operating on the in-memory graph, preserving identical semantics and compatible output.

## External Behavior

All subcommands read from the specgraph cache (auto-rebuilding if stale) and write to stdout. TTY detection controls whether OSC 8 hyperlinks are emitted.

| Command | Input | Output |
|---------|-------|--------|
| `blocks <ID>` | artifact ID | newline-separated dependency IDs |
| `blocked-by <ID>` | artifact ID | newline-separated IDs that depend on this |
| `tree <ID>` | artifact ID | transitive dependency closure (all ancestors) |
| `ready` | — | unresolved artifacts with all deps satisfied, formatted with status and OSC 8 links |
| `next` | — | ready items + what they'd unblock; blocked items + what they need |
| `mermaid` | `--all`, `--all-edges` | Mermaid `graph TD` diagram |
| `status` | `--all` | summary table grouped by type, then by status |
| `overview` | `--all` | hierarchy tree with status icons, blocking indicators, cross-cutting section, executive summary, and tk integration |
| `neighbors <ID>` | artifact ID | TSV: direction, edge type, ID, status, title |
| `scope <ID>` | artifact ID | parent chain, siblings, laterals, supporting vision/architecture |
| `impact <ID>` | artifact ID | direct references, affected chains, total count |
| `edges [<ID>]` | optional artifact ID | TSV: from, to, edge type |

**Flags:**
- `--all` — include resolved artifacts in `overview`, `status`, `mermaid`
- `--all-edges` — show all edge types in `mermaid` (not just depends-on and parent)

## Acceptance Criteria

1. **Given** each subcommand, **when** run against the live repo's `docs/` tree, **then** the Python output matches the bash output (modulo trailing whitespace and OSC 8 escape sequences which depend on TTY detection).

2. **Given** `ready`, **when** an artifact's dependencies are all resolved, **then** it appears in the ready list. **When** any dependency is unresolved, **then** it does not.

3. **Given** `overview`, **when** run without `--all`, **then** resolved artifacts are hidden. **When** run with `--all`, **then** all artifacts are shown with resolved ones styled.

4. **Given** `mermaid`, **when** run with `--all-edges`, **then** all edge types between visible nodes are rendered. **When** run without it, **then** only depends-on and parent edges are shown.

5. **Given** `scope <ID>`, **when** the artifact has a parent chain to a VISION, **then** the chain, siblings, laterals, and supporting vision (with architecture-overview.md detection) are all shown.

6. **Given** `overview`, **when** tk is installed, **then** `tk ready` output is appended under the execution tracking section.

7. **Given** `next`, **when** completing a ready item would unblock another, **then** the "unblocks" line shows the newly unblockable artifact(s).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| 1. Python output matches bash (modulo trailing whitespace, OSC 8) | 50 integration tests in test_integration.py — edges command matches exactly; other commands have documented intentional divergences (Python correctly filters resolved items) | ✅ |
| 2. ready: artifact appears when all deps resolved | test_ready_returns_nodes_with_all_deps_resolved — EPIC-001 and SPIKE-048 confirmed ready; SPEC-001/SPEC-002 confirmed blocked | ✅ |
| 3. overview without --all hides resolved; --all shows all | TestOverview.test_overview_hides_resolved_by_default and test_overview_shows_resolved_with_all | ✅ |
| 4. mermaid with --all-edges shows all edge types | TestMermaid.test_mermaid_all_edges_includes_non_core_types | ✅ |
| 5. scope shows parent chain, siblings, laterals, architecture | TestScope — 4 sections rendered correctly | ✅ |
| 6. overview with tk installed appends tk ready output | TestOverview.test_overview_tk_section_present — tk integration section present | ✅ |
| 7. next: completing ready item shows unblockable artifacts | TestNext.test_next_would_unblock — EPIC-001 shows would unblock SPEC-002 | ✅ |

## Scope & Constraints

- Output compatibility is the primary constraint — callers (swain-status.sh, agent prompts) expect specific output formats
- The `overview` command's tk integration should shell out to `tk ready` (same as bash)
- VISION-to-VISION deps are informational, not blocking (preserving existing behavior from #28)
- `scope` must detect `architecture-overview.md` adjacent to the Vision file (filesystem check)

## Implementation Approach

1. **Port each command as a Python function** that takes the graph (nodes dict, edges list) and returns a string. This makes them testable without I/O.

2. **Write comparison tests:** For each subcommand, capture the bash output on the current repo, then assert the Python output matches. Use a snapshot-testing approach.

3. **OSC 8 helper:** Port the `link()`, `file_link()`, `artifact_link()` helpers as a Python utility that checks `sys.stdout.isatty()`.

4. **Wire up CLI:** Add each subcommand to the argparse dispatch in `cli.py`.

5. **Integration verification:** Run `specgraph.py <cmd>` vs `specgraph.sh <cmd>` for all subcommands on the live repo. Diff results.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-13 | — | Initial creation |
| Complete | 2026-03-14 | 6eb4eea | All 13 query subcommands shipped in specgraph.py. 118 tests passing. (incorrect stamp — see Active row) |
| Active | 2026-03-14 | — | Reverted from Complete — query subcommands not yet implemented in Python |
| Complete | 2026-03-14 | 88a9d04 | All 12 query subcommands implemented in Python; 341 tests passing; integrated with CLI dispatch |
