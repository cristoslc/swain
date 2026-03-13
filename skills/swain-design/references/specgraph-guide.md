# Specgraph Guide

Reference for `specgraph.sh` subcommands and output interpretation.

## Subcommands

| Command | What it does |
|---------|-------------|
| `overview` | **Default.** Hierarchy tree with status indicators + execution tracking |
| `build` | Force-rebuild graph from frontmatter |
| `blocks <ID>` | What does this artifact depend on? (direct dependencies) |
| `blocked-by <ID>` | What depends on this artifact? (inverse lookup) |
| `tree <ID>` | Transitive dependency tree (all ancestors) |
| `ready` | Active/Planned artifacts with all deps resolved |
| `next` | What to work on next (ready items + what they unblock, blocked items + what they need) |
| `mermaid` | Mermaid diagram to stdout |
| `status` | Summary table by type and phase |
| `neighbors <ID>` | All directly connected artifacts (any edge type, both directions) |
| `scope <ID>` | Alignment scope — parent chain to Vision, siblings, lateral links |
| `impact <ID>` | Everything that references this artifact transitively |
| `edges [<ID>]` | Raw edge list with types, optionally filtered to one artifact |

## Options

| Flag | Effect |
|------|--------|
| `--all` | Include finished artifacts (terminal states like Complete, Abandoned, etc.). By default `overview`, `status`, and `mermaid` hide them to reduce noise. |
| `--all-edges` | Show all edge types in mermaid output (not just depends-on and parent edges). |

Run `blocks <ID>` before phase transitions to verify dependencies are resolved. Run `ready` to find unblocked work. Run `tree <ID>` for transitive dependency chains. Run `scope <ID>` before alignment checks.

## Overview output

The `overview` command renders a hierarchy tree showing every artifact with its status, blocking dependencies, and swain-do progress:

```
  ✓ VISION-001: Personal Agent Patterns [Active]
  ├── → EPIC-007: Spec Management System [Active]
  │   ├── ✓ SPEC-001: Artifact Lifecycle [Implemented]
  │   ├── ✓ SPEC-002: Dependency Graph [Implemented]
  │   └── → SPEC-003: Cross-reference Validation [Draft]
  │         ↳ blocked by: SPIKE-002
  └── → EPIC-008: Execution Tracking [Proposed]

── Cross-cutting ──
  ├── → ADR-001: Graph Storage Format [Adopted]
  └── → PERSONA-001: Solo Developer [Validated]

── Execution Tracking ──
  (tk status output here)
```

**Status indicators:** `✓` = resolved (Complete/Implemented/Adopted/etc.), `→` = active/in-progress. Blocked dependencies show inline with `↳ blocked by:`. Cross-cutting artifacts (ADR, Persona, Runbook, Bug, Spike) appear in their own section. The swain-do tail calls `tk ready` automatically.

**Display rule:** Present the `specgraph.sh overview` output verbatim — do not summarize, paraphrase, or reformat the tree. The script's output is already designed for human consumption. You may add a brief note after the output only if the user asked a specific question (e.g., "what should I work on next?").

## Edge types

The graph captures all frontmatter relationship fields as typed edges:

| Edge type | Source | Target | Purpose |
|-----------|--------|--------|---------|
| `depends-on` | Any | Any | Blocking dependency |
| `parent-vision` | EPIC, JOURNEY | VISION | Hierarchy (child → parent) |
| `parent-epic` | SPEC, STORY, EPIC | EPIC | Hierarchy (child → parent) |
| `linked-adrs` | SPEC, EPIC, DESIGN | ADR | Architectural decision link |
| `linked-specs` | ADR, DESIGN | SPEC | Specification link |
| `linked-epics` | ADR, DESIGN | EPIC | Epic link |
| `linked-research` | SPEC, ADR, SPIKE, EPIC | SPIKE | Research dependency |
| `linked-personas` | JOURNEY | PERSONA | Persona reference |
| `linked-journeys` | PERSONA | JOURNEY | Journey reference |
| `linked-stories` | PERSONA, DESIGN | STORY | Story reference |
| `linked-designs` | EPIC, STORY, SPEC | DESIGN | Design reference |
| `addresses` | SPEC, STORY, EPIC | JOURNEY.PP-NN | Pain point being addressed |
| `validates` | RUNBOOK | EPIC, SPEC | Operational validation |
| `superseded-by` | ADR, DESIGN | ADR, DESIGN | Replacement link |
| `evidence-pool` | Any | Pool ID | Research evidence pool |
| `source-issue` | SPEC | GitHub ref | External issue tracker link |

`depends-on` is the only edge type that gates `ready` and `next`. All other types are informational relationships used by `scope`, `impact`, `neighbors`, and `mermaid --all-edges`.

## Neighbors output

The `neighbors <ID>` command shows all directly connected artifacts with direction, edge type, and artifact metadata:

```
outgoing  depends-on    SPEC-004  [Implemented]  Unified SPEC Type System
outgoing  parent-epic   EPIC-002  [Complete]     Artifact Type System
incoming  linked-adrs   ADR-001   [Adopted]      Graph Storage Format
```

## Scope output

The `scope <ID>` command groups related artifacts for alignment checking:

```
CHAIN:
  EPIC-002  [Complete]  Artifact Type System
  VISION-001  [Active]  Swain

SIBLING:
  SPEC-004  [Implemented]  Unified SPEC Type System
  SPEC-006  [Implemented]  BUG-to-SPEC Migration

LATERAL:
  JOURNEY-001.PP-01  (addresses)

SUPPORTING:
  vision: VISION-001  Swain
  file: docs/vision/Active/(VISION-001)-Swain/(VISION-001)-Swain.md
  architecture: docs/vision/Active/(VISION-001)-Swain/architecture-overview.md
```

- **CHAIN**: Parent hierarchy from the artifact up to the Vision
- **SIBLING**: Other artifacts sharing the same immediate parent
- **LATERAL**: Non-hierarchical relationships (linked-*, addresses, validates)
- **SUPPORTING**: The Vision anchor and architecture overview (if present)

Use `scope` as the input for alignment checks — see [alignment-checking.md](alignment-checking.md).

## Impact output

The `impact <ID>` command shows everything that references an artifact:

```
DIRECT:
  SPEC-008  [Implemented]  Superpowers Integration

AFFECTED CHAINS:
  SPEC-008 → EPIC-004

TOTAL AFFECTED: 2 artifact(s)
```

Use `impact` for change analysis — before modifying or deprecating an artifact, see what would be affected.

## Edges output

The `edges` command outputs raw edge data in TSV format:

```
SPEC-005  EPIC-002        parent-epic
SPEC-005  JOURNEY-001.PP-01  addresses
SPEC-005  SPEC-004        depends-on
```

Without an ID argument, outputs all edges in the graph. Useful for scripting and programmatic access.
