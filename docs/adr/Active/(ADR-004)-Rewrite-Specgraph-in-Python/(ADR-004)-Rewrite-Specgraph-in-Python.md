---
title: "Rewrite Specgraph in Python"
artifact: ADR-004
track: standing
status: Active
author: cristos
created: 2026-03-13
last-updated: 2026-03-14
linked-artifacts:
  - EPIC-013
  - ADR-003
  - SPEC-030
depends-on-artifacts: []
---

# Rewrite Specgraph in Python

## Context

Specgraph is the artifact dependency graph engine that powers swain-status, alignment checking, and artifact lifecycle queries. It is currently implemented as a single 900+ line bash script (`specgraph.sh`) that:

- Parses YAML frontmatter from `docs/**/*.md` files using `sed`/`grep`
- Builds a JSON graph (nodes + typed edges) by string concatenation
- Delegates all graph queries and output formatting to `jq`
- Uses temp files and `comm` for set operations
- Has no test suite

This implementation was appropriate when specgraph was a simple cache builder with a few query commands. It has since grown to 13 subcommands (build, blocks, blocked-by, tree, ready, next, mermaid, status, overview, neighbors, scope, impact, edges) and is the substrate that swain-status, swain-design phase transitions, and alignment checking depend on.

New features require capabilities that are awkward or fragile in bash:

- **Cross-reference validation (xref)**: scanning artifact body text for ID references, computing set differences against frontmatter declarations, and surfacing discrepancies. This requires regex extraction, set operations, and structured output — all of which require temp files, `comm`, and multi-step `jq` pipelines in bash.
- **Bidirectional edge enforcement**: when artifact A declares `depends-on: B`, B should have A in `linked-artifacts`. This is a graph-level consistency check across node pairs.
- **Body-text scanning**: extracting artifact ID patterns from markdown body text (after frontmatter), filtering against the known ID set, and comparing against declared relationships.

The bash implementation has also accumulated correctness issues:
- Shell escaping problems with `!=` in `jq` queries (diagnosed in the swain-status `is_resolved` bug this session)
- Fragile JSON construction via string concatenation (`nodes_json="$nodes_json, \"$artifact\": $node_json"`)
- No ability to unit test individual functions

## Decision

Rewrite specgraph as a Python module at `skills/swain-design/scripts/specgraph.py`, preserving the exact same CLI interface, cache format, and subcommand behavior. Add the new xref and bidirectional-edge features as part of the rewrite.

**Key constraints:**

1. **Same CLI interface** — `specgraph.py <command> [args] [--all] [--all-edges]` with identical subcommand names and semantics. The bash script is replaced by a Python entry point; callers (swain-status.sh, agent prompts) update the path but not the invocation pattern.
2. **Same cache format** — `/tmp/agents-specgraph-<repo-hash>.json` with the same `{nodes, edges, generated, repo}` structure, extended with a new `xref` key. Consumers that read the cache (swain-status.sh `collect_artifacts`) continue working without changes.
3. **No new runtime dependencies** — Python 3.9+ (ships with macOS), standard library only. YAML frontmatter parsing uses regex, not PyYAML.
4. **Testable** — the graph data structure, frontmatter parser, xref logic, and query functions are importable and testable as Python functions.

## Alternatives Considered

**Stay in bash, add xref via temp files + comm.** Technically possible but adds ~150 lines of fragile set-operation code, requires careful handling of empty inputs and `set -euo pipefail` interactions, and produces no testable units. The 1000+ line result would be harder to maintain than the Python equivalent.

**Rewrite in Node.js/TypeScript.** Viable but adds a build step (for TypeScript) or requires Node installed. Python is already available on macOS and better suited to the file-scanning, regex, and graph-traversal workload.

**Use a graph database or library (e.g., NetworkX).** Over-engineered for ~100 nodes and ~150 edges. The graph fits in a single JSON file and Python dicts handle all needed operations.

## Consequences

**Positive:**
- xref validation and bidirectional edge enforcement become straightforward set operations on Python dicts.
- Frontmatter parsing moves from fragile `sed`/`grep` chains to a single regex-based parser that can be unit tested.
- Graph queries move from embedded `jq` to Python functions that are readable, debuggable, and testable.
- The cache format extends cleanly (add `xref` key) without breaking existing consumers.

**Negative:**
- Migration effort: ~900 lines of bash to port. Mitigated by the existing bash serving as an executable specification.
- Python startup time (~50ms) is slower than bash for trivial commands. Acceptable for a development tool.
- Two-language toolchain: swain-status.sh (bash) calls specgraph.py (Python). This is already the pattern (bash calling `jq`, `gh`, `tk`), so no conceptual overhead.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-13 | — | Initial creation |
| Active | 2026-03-14 | 8783f9a | Decision adopted |
