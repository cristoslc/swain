# Specgraph Guide

Reference for `chart.sh` (swain chart) and `specgraph.sh` subcommands.

> **Note:** `chart.sh` is the primary interface. `specgraph.sh` is a deprecated alias that continues to work.

## swain chart — vision-rooted hierarchy

`chart.sh` renders all artifacts as a tree rooted at Vision artifacts. Titles are the primary label; IDs are hidden by default. Lenses filter and annotate the tree for different decision contexts.

### Lenses

| Command | What it shows | Default depth |
|---------|-------------|---------------|
| `chart.sh` | **Default.** All non-terminal artifacts with status icons | strategic (2) |
| `chart.sh ready` | Unblocked artifacts ready for work | execution (4) |
| `chart.sh recommend [--focus ID]` | Scored by priority × unblock count | strategic (2) |
| `chart.sh attention [--days N]` | Recent git activity per vision | strategic (2) |
| `chart.sh debt` | Unresolved decisions (Proposed Spikes/ADRs/Epics) | strategic (2) |
| `chart.sh unanchored` | Artifacts with no Vision ancestry | strategic (2) |
| `chart.sh status` | All artifacts annotated with phase | strategic (2) |

### Display options

| Flag | Effect |
|------|--------|
| `--depth N` | Set tree depth (2=strategic, 4=execution) |
| `--detail` | Alias for `--depth 4` |
| `--phase active,ready` | Only show artifacts in these phases |
| `--hide-terminal` | Exclude Complete, Abandoned, etc. |
| `--ids` | Show artifact IDs alongside titles |
| `--flat` | Flat list output for scripting |
| `--json` | Structured JSON output |

### Depth precedence

1. `--depth N` — explicit flag, always wins
2. Focus lane — execution depth (4) when set, strategic (2) when unset
3. Lens default — each lens defines its own

## Low-level graph queries

These commands pass through to the specgraph engine:

| Command | What it does |
|---------|-------------|
| `build` | Force-rebuild graph from frontmatter |
| `blocks <ID>` | What does this artifact depend on? (direct dependencies) |
| `blocked-by <ID>` | What depends on this artifact? (inverse lookup) |
| `deps <ID>` | Transitive dependency closure (all ancestors). Formerly `tree`. |
| `tree <ID>` | Alias for `deps` (backward compat) |
| `ready` | Active/Planned artifacts with all deps resolved |
| `next` | What to work on next (ready items + what they unblock) |
| `mermaid` | Mermaid diagram to stdout |
| `status` | Summary table by type and phase |
| `neighbors <ID>` | All directly connected artifacts (any edge type, both directions) |
| `scope <ID>` | Alignment scope — parent chain to Vision, siblings, lateral links |
| `impact <ID>` | Everything that references this artifact transitively |
| `edges [<ID>]` | Raw edge list with types, optionally filtered to one artifact |
| `recommend [--focus VISION-ID] [--json]` | Ranked recommendations |
| `decision-debt [--json]` | Decision debt per vision |
| `attention [--days N] [--json]` | Attention distribution and drift detection |

| Flag | Effect |
|------|--------|
| `--all` | Include finished artifacts (terminal states). |
| `--all-edges` | Show all edge types in mermaid output. |

Run `blocks <ID>` before phase transitions to verify dependencies are resolved. Run `chart.sh ready` to find unblocked work. Run `deps <ID>` for transitive dependency chains. Run `scope <ID>` before alignment checks.

## Overview output

The `overview` command renders a hierarchy tree showing every artifact with its status, blocking dependencies, and swain-do progress:

```
  ✓ VISION-001: Personal Agent Patterns [Active]
  ├── → EPIC-007: Spec Management System [Active]
  │   ├── ✓ SPEC-001: Artifact Lifecycle [Complete]
  │   ├── ✓ SPEC-002: Dependency Graph [Complete]
  │   └── → SPEC-003: Cross-reference Validation [Proposed]
  │         ↳ blocked by: SPIKE-002
  └── → EPIC-008: Execution Tracking [Proposed]

── Cross-cutting ──
  ├── → ADR-001: Graph Storage Format [Active]
  └── → PERSONA-001: Solo Developer [Active]

── Execution Tracking ──
  (tk status output here)
```

**Status indicators:** `✓` = resolved (Complete/Active/etc.), `→` = active/in-progress. Blocked dependencies show inline with `↳ blocked by:`. Cross-cutting artifacts (ADR, Persona, Runbook, Bug, Spike) appear in their own section. The swain-do tail calls `tk ready` automatically.

**Display rule:** Present the `specgraph.sh overview` output verbatim — do not summarize, paraphrase, or reformat the tree. The script's output is already designed for human consumption. You may add a brief note after the output only if the user asked a specific question (e.g., "what should I work on next?").

## Edge types

The graph captures all frontmatter relationship fields as typed edges:

| Edge type | Source | Target | Purpose |
|-----------|--------|--------|---------|
| `depends-on-artifacts` | Any (except SPIKE) | Any | Blocking dependency |
| `parent-vision` | INITIATIVE, EPIC, JOURNEY | VISION | Hierarchy (child → parent) |
| `parent-initiative` | EPIC, SPEC | INITIATIVE | Hierarchy (child → parent) |
| `parent-epic` | SPEC, EPIC | EPIC | Hierarchy (child → parent) |
| `linked-artifacts` | Any | Any | Unified cross-reference (replaces per-type linked-* fields) |
| `addresses` | SPEC, EPIC | JOURNEY.PP-NN | Pain point being addressed |
| `validates` | RUNBOOK | EPIC, SPEC | Operational validation |
| `superseded-by` | ADR, DESIGN | ADR, DESIGN | Replacement link |
| `evidence-pool` | Any | Pool ID | Research evidence pool |
| `source-issue` | SPEC | GitHub ref | External issue tracker link |

`depends-on-artifacts` is the only edge type that gates `ready` and `next`. All other types are informational relationships used by `scope`, `impact`, `neighbors`, and `mermaid --all-edges`.

## Neighbors output

The `neighbors <ID>` command shows all directly connected artifacts with direction, edge type, and artifact metadata:

```
outgoing  depends-on    SPEC-004  [Complete]  Unified SPEC Type System
outgoing  parent-epic   EPIC-002  [Complete]     Artifact Type System
incoming  linked-artifacts  ADR-001   [Active]      Graph Storage Format
```

## Scope output

The `scope <ID>` command groups related artifacts for alignment checking:

```
CHAIN:
  EPIC-002  [Complete]  Artifact Type System
  VISION-001  [Active]  Swain

SIBLING:
  SPEC-004  [Complete]  Unified SPEC Type System
  SPEC-006  [Complete]  BUG-to-SPEC Migration

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
  SPEC-008  [Complete]  Superpowers Integration

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

## Recommend output

The `recommend` command ranks artifacts by prioritization score to guide the operator toward the highest-leverage work:

```
RECOMMENDED NEXT:
  1. EPIC-012  [Proposed]  Scoring Engine     score=12  (unblocks: 4, weight: high)
  2. SPEC-031  [Ready]     Graph Persistence  score=6   (unblocks: 2, weight: medium)
  3. EPIC-009  [Proposed]  Search Indexing    score=3   (unblocks: 3, weight: low)
```

**Score formula:** `score = unblock_count × vision_weight`, where `vision_weight` maps `high → 3`, `medium → 2`, `low → 1` from the artifact's `priority-weight` field. Artifacts with no `priority-weight` default to `medium`.

`--focus VISION-ID` limits output to artifacts under that Vision. `--json` outputs the ranked list as a JSON array.

## Decision-debt output

The `decision-debt` command summarizes unresolved blocking artifacts (SPIKEs, ADRs in Proposed) per Vision:

```
DECISION DEBT:
  VISION-001  Personal Agent Patterns
    SPIKE-014  [Proposed]  Storage format evaluation      (blocks: SPEC-028, SPEC-029)
    ADR-007    [Proposed]  Auth provider selection        (blocks: EPIC-011)

  VISION-002  Collaboration Layer
    (no debt)
```

Use this to identify where research or decisions are delaying downstream work. `--json` outputs structured debt data keyed by Vision ID.

## Attention output

The `attention` command analyzes git commit history to surface attention distribution and drift:

```
ATTENTION DISTRIBUTION (last 30 days):
  EPIC-007  Spec Management    ████████████  42 commits  (40%)
  EPIC-012  Scoring Engine     ████          12 commits  (11%)
  EPIC-009  Search Indexing    ██             6 commits   (6%)
  (unlinked)                   ██████        22 commits  (21%)

DRIFT DETECTED:
  EPIC-011  [Active] Auth Layer — 0 commits in 30 days (last touched: 45 days ago)
```

**Drift detection:** any Active artifact with zero commits in the window is flagged. Default window is 30 days; `--days N` overrides it. `--json` outputs attention counts and drift flags per artifact.
