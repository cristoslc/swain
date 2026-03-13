---
title: "Specgraph Python Rewrite"
artifact: EPIC-013
status: Proposed
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
parent-vision: VISION-001
success-criteria:
  - specgraph.py passes all existing bash specgraph subcommands with identical output (modulo whitespace)
  - xref validation detects body-text artifact references not declared in frontmatter (and vice versa)
  - Bidirectional edge enforcement flags missing reciprocal linked-artifacts for depends-on edges
  - swain-status.sh works without changes against the new cache format
  - Unit tests cover frontmatter parsing, graph building, xref logic, and each query subcommand
depends-on-artifacts:
  - ADR-004
linked-artifacts:
  - ADR-003
addresses: []
---

# Specgraph Python Rewrite

## Goal / Objective

Replace the 900+ line bash specgraph.sh with a Python implementation that preserves the existing CLI and cache contract while adding cross-reference validation and bidirectional edge enforcement. The rewrite makes the graph engine testable, maintainable, and extensible.

## Scope Boundaries

**In scope:**

### Existing capabilities (port from bash)

1. **Frontmatter parsing** — extract artifact ID, title, status, type, description, and all relationship fields (depends-on-artifacts, linked-artifacts, parent-epic, parent-vision, validates, addresses, superseded-by, evidence-pool, source-issue) from YAML frontmatter in `docs/**/*.md`
2. **Graph building** — construct a node map (artifact ID → metadata) and typed edge list from parsed frontmatter, write to `/tmp/agents-specgraph-<repo-hash>.json` cache
3. **Cache management** — rebuild when any `docs/*.md` file is newer than the cache; force rebuild via `build` command
4. **Dependency queries** — `blocks <ID>`, `blocked-by <ID>`, `tree <ID>` (transitive closure)
5. **Readiness queries** — `ready` (unresolved with all deps satisfied), `next` (ready + what they'd unblock, blocked + what they need)
6. **Visualization** — `mermaid` output with `--all` and `--all-edges` flags, node styling for resolved artifacts
7. **Status summary** — `status` (grouped by type and phase), `overview` (hierarchy tree with blocking indicators and tk integration)
8. **Graph exploration** — `neighbors <ID>` (all direct connections), `scope <ID>` (parent chain, siblings, laterals), `impact <ID>` (transitive reverse lookup)
9. **Raw data** — `edges [<ID>]` (TSV edge list)
10. **Resolved-state detection** — type-aware resolution logic (standing-track types resolve at Active; implementable types at Complete; universal terminal states)
11. **OSC 8 hyperlinks** — clickable file:// links in terminal output when stdout is a TTY

### New capabilities

12. **Cross-reference validation (xref)** — scan artifact body text for `TYPE-NNN` patterns, filter to known artifact IDs, compare against frontmatter declarations. Surface two categories:
    - **Body-not-in-frontmatter**: artifact ID mentioned in body but not in any frontmatter relationship field → agent should determine if it's `depends-on-artifacts` or `linked-artifacts` and update frontmatter
    - **Frontmatter-not-in-body**: artifact declared in frontmatter but never mentioned in body → possible stale reference

13. **Bidirectional edge enforcement** — when A declares `depends-on-artifacts: [B]`, check that B has A in its `linked-artifacts`. Surface missing reciprocal edges for the agent to fix.

14. **`xref` subcommand** — output cross-reference discrepancies (body vs frontmatter gaps + missing reciprocal edges) as structured JSON and human-readable text

15. **xref in cache** — store xref results in the specgraph cache under an `xref` key so swain-status can surface them without a separate scan

16. **swain-status integration** — surface xref discrepancies in the status dashboard and agent summary template

### Quality

17. **Unit tests** — test frontmatter parser, graph builder, xref logic, resolved-state detection, and each query subcommand against fixture data
18. **Drop-in replacement** — identical CLI interface (`specgraph.py <command> [args] [--all] [--all-edges]`), identical cache path and JSON structure (extended with `xref`), consumers update the script path only

**Out of scope:**
- Third-party dependencies (PyYAML, NetworkX, etc.) — stdlib only
- Interactive commands or TUI
- Changing the cache location or format structure (beyond adding `xref`)
- Modifying swain-status.sh beyond updating the specgraph path reference and adding xref rendering

## Child Specs

_Updated as Agent Specs are created under this epic._

- SPEC-030: Specgraph Python Core (frontmatter parsing, graph building, cache management, CLI interface)
- SPEC-031: Specgraph Query Commands (port all 11 query subcommands)
- SPEC-032: Cross-Reference Validation and Bidirectional Edge Enforcement (xref)
- SPEC-033: swain-status xref Integration (render discrepancies in dashboard and agent summary)

## Key Dependencies

- ADR-004: Rewrite Specgraph in Python (decision to proceed)
- ADR-003: Normalize Artifact Lifecycle to Three Tracks (defines resolved-state logic that specgraph implements)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-13 | — | Initial creation |
