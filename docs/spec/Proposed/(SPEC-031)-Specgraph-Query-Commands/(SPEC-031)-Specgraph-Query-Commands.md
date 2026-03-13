---
title: "Specgraph Query Commands"
artifact: SPEC-031
status: Proposed
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
type: feature
parent-epic: EPIC-013
linked-artifacts:
  - ADR-004
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
