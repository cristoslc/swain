# Related Artifacts Materialization Design

**Date:** 2026-04-03
**Status:** Draft

## Intent

Materialize all graph edges as symlinks so operators can intuitively browse the entire artifact graph from the filesystem. Currently, only parent-child hierarchy edges are materialized. Cross-references and dependencies remain invisible in the folder structure.

## Problem

DESIGN-015 links to EPIC-057 via `linked-artifacts`, but browsing `docs/design/Active/(DESIGN-015)-Usage-Logging-and-Telemetry/` shows no connection to the EPIC. Operators must use `chart neighbors` to discover relationships.

The goal: every edge from `chart` should be browseable as a symlink directory.

## Proposed Solution

Extend the materialization system to create two new symlink directories inside each artifact folder:

| Directory | Edge Type | Source Field |
|-----------|-----------|--------------|
| `_Related/` | Informational cross-references | `linked-artifacts`, `artifact-refs` |
| `_Depends-On/` | Blocking dependencies | `depends-on-artifacts` |

Parent-child hierarchy (existing) remains direct symlinks in the parent folder.

## Filesystem Structure

```
docs/epic/Active/(EPIC-057)-Usage-Telemetry-Implementation/
├── (EPIC-057)-Usage-Telemetry-Implementation.md   # artifact file
├── (SPEC-244)-Telemetry-Configuration/             # direct child symlink
├── (SPEC-245)-Telemetry-Event-Emission/           # direct child symlink
├── _Related/                                       # NEW: cross-references
│   └── (DESIGN-015)-Usage-Logging-and-Telemetry -> ../../../design/Active/(DESIGN-015)-Usage-Logging-and-Telemetry/
└── _Depends-On/                                    # NEW: blocking dependencies (empty in this example)
```

```
docs/design/Active/(DESIGN-015)-Usage-Logging-and-Telemetry/
├── (DESIGN-015)-Usage-Logging-and-Telemetry.md
├── _Related/
│   └── (EPIC-057)-Usage-Telemetry-Implementation -> ../../../epic/Proposed/(EPIC-057)-Usage-Telemetry-Implementation/
└── (no _Depends-On/ since DESIGN doesn't declare dependencies)
```

Both sides get symlinks when both sides declare the relationship (atomic processing).

## Projection Schema Extension

Extend `build_projection()` in `specgraph/graph.py` to include relationship fields:

```python
{
  "artifact": "EPIC-057",
  "type": "EPIC",
  "status": "Proposed",
  "canonical_file": "docs/epic/Proposed/(EPIC-057)-Usage-Telemetry-Implementation.md",
  "canonical_path": "docs/epic/Proposed/(EPIC-057)-Usage-Telemetry-Implementation",
  "direct_parent": "INITIATIVE-002",
  "placement_state": "placed",
  
  # NEW fields:
  "linked_artifacts": ["DESIGN-015"],
  "depends_on_artifacts": []
}
```

Normalization: include just artifact IDs. `materialize.py` resolves paths using the `nodes` dict.

## Materialization Logic

`materialize_children()` extended to process each artifact atomically:

1. **Direct children** (existing): create symlink in parent folder
2. **`_Related/`**: create subdirectory, symlink for each `linked_artifacts` ID
3. **`_Depends-On/`**: create subdirectory, symlink for each `depends_on_artifacts` ID
4. **Cleanup**: remove stale symlinks when frontmatter links removed

Symlink naming: use the target artifact's folder name: `(ARTIFACT-ID)-Title`

Relative path calculation: `os.path.relpath(target_path, start=parent_path)`

## Edge Cases

- **Missing target**: skip symlink if ID not in `nodes` dict (broken reference)
- **Self-reference**: skip symlink if artifact references itself
- **Empty directories**: create `_Related/` or `_Depends-On/` only if non-empty
- **Lifecycle changes**: symlink target updates automatically on next rebuild

## Implementation Scope

1. Extend `build_projection()` to include `linked_artifacts` and `depends_on_artifacts`
2. Extend `materialize_children()` to create `_Related/` and `_Depends-On/` symlinks
3. Add cleanup logic for stale relationship symlinks
4. Tests for new symlink types

## Non-goals

- Rendering `artifact-refs.rel` types in directory structure
- Creating separate directories for different `rel` values
- Materializing edges that don't exist in `chart` output

## Constraints

- `chart` remains sole source of truth for graph interpretation
- No new CLI surface - projection is internal implementation detail
- Atomic processing: each artifact's symlinks derived from its own frontmatter only