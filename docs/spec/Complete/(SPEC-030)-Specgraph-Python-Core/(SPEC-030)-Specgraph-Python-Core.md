---
title: "Specgraph Python Core"
artifact: SPEC-030
status: Complete
author: cristos
created: 2026-03-13
last-updated: 2026-03-14
type: feature
parent-epic: EPIC-013
linked-artifacts:
  - ADR-004
  - ADR-003
depends-on-artifacts:
  - ADR-004
addresses: []
source-issue:
swain-do: required
---

# Specgraph Python Core

## Problem Statement

The specgraph engine's core infrastructure — frontmatter parsing, graph building, cache management, and CLI dispatch — is currently implemented in bash with fragile `sed`/`grep` parsing and JSON string concatenation. This spec covers porting the foundational layer to Python, establishing the module structure that query commands (SPEC-031) and xref validation (SPEC-032) build on.

## External Behavior

**Input:** `docs/**/*.md` files containing YAML frontmatter with `artifact:` field.

**Output:** A JSON cache file at `/tmp/agents-specgraph-<repo-hash>.json` with structure:

```json
{
  "generated": "ISO-8601 timestamp",
  "repo": "/absolute/path/to/repo",
  "nodes": {
    "ARTIFACT-ID": {
      "title": "string",
      "status": "string",
      "type": "string (e.g., EPIC, SPEC, ADR)",
      "file": "relative/path/from/repo/root",
      "description": "first ~120 chars of description/question/body"
    }
  },
  "edges": [
    {"from": "ID", "to": "ID", "type": "edge-type"}
  ]
}
```

**CLI:** `specgraph.py build [--all] [--all-edges]` — force rebuild and print node/edge counts. Auto-rebuild when any `docs/*.md` is newer than cache.

**Edge types parsed:** `depends-on-artifacts`, `linked-artifacts`, `validates`, `addresses`, `parent-epic`, `parent-vision`, `superseded-by`, `evidence-pool`, `source-issue`.

**Module structure:**
```
skills/swain-design/scripts/
  specgraph.py          # CLI entry point
  specgraph/
    __init__.py
    parser.py           # frontmatter extraction
    graph.py            # graph building, cache I/O
    resolved.py         # type-aware resolution logic
    cli.py              # argument parsing, subcommand dispatch
```

## Acceptance Criteria

1. **Given** a `docs/` tree with artifact markdown files, **when** `specgraph.py build` is run, **then** the cache JSON is identical to the bash version (same nodes, same edges, same types) modulo key ordering and whitespace.

2. **Given** a file with YAML frontmatter containing all supported relationship fields, **when** parsed, **then** all fields are extracted correctly including list fields (depends-on-artifacts, linked-artifacts), scalar fields (parent-epic, source-issue), and full-format fields (addresses with JOURNEY-NNN.PP-NN).

3. **Given** a cache file older than a `docs/*.md` file, **when** any subcommand is invoked, **then** the cache is silently rebuilt before executing the command.

4. **Given** a fresh cache, **when** any subcommand is invoked, **then** no rebuild occurs and the cached data is used directly.

5. **Given** an artifact with `question:` frontmatter (SPIKE), **when** description is extracted, **then** `question` takes priority over `description` and body text fallback.

6. **Given** resolved-state logic, **when** evaluated, **then** standing-track types (VISION, JOURNEY, PERSONA, ADR, RUNBOOK, DESIGN) resolve at Active; implementable types (SPEC) resolve at Complete and terminal states; container types (EPIC, SPIKE) resolve at Complete and terminal states. Universal terminals (Abandoned, Retired, Superseded) always resolve.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Python 3.9+ stdlib only — no PyYAML, no third-party packages
- Frontmatter parsing via regex (`---` delimited block), not a YAML library
- Cache path derivation must match bash: `printf '%s' "$REPO_ROOT" | shasum -a 256 | cut -c1-12` → Python equivalent using `hashlib.sha256`
- Title cleaning: strip `TYPE-NNN: ` prefix from title field (matching bash behavior)
- The `specgraph.sh` bash script remains in place during development; the Python version runs alongside it until all SPECs in the epic are complete, then the bash script is removed

## Implementation Approach

1. **Parser (TDD):** Write tests for frontmatter extraction against fixture files covering all field types. Implement `parser.py` with regex-based YAML frontmatter extraction.

2. **Graph builder (TDD):** Write tests for edge construction from parsed frontmatter. Implement `graph.py` with node/edge construction and JSON cache I/O.

3. **Resolution logic (TDD):** Write tests for `is_resolved()` against all type/status combinations. Implement `resolved.py` matching the bash jq `is_resolved` function.

4. **CLI dispatch:** Implement `cli.py` with argparse, cache freshness check, and subcommand routing. Only `build` is wired up in this spec; query commands come in SPEC-031.

5. **Integration test:** Run both bash and Python `build` on the live repo, diff the cache JSON output (after normalizing key order).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-13 | — | Initial creation |
| Complete | 2026-03-14 | 6eb4eea | Shipped with Python specgraph package: parser, graph, cache, CLI dispatch. 118 tests passing. |
