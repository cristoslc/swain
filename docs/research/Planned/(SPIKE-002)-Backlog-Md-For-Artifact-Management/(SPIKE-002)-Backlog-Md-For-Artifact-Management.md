---
title: "Backlog.md for artifact management"
artifact: SPIKE-002
status: Planned
author: cristos
created: 2026-03-10
last-updated: 2026-03-10
question: "Should swain-design use Backlog.md to manage artifact lifecycle instead of the current frontmatter-scanning + specgraph approach?"
gate: Pre-MVP
risks-addressed:
  - specgraph.sh rebuild cost (scans every .md file in docs/ on every invocation)
  - Fragile frontmatter parsing (regex-based YAML extraction in bash)
  - Phase transitions require git mv of directories
  - Separate index files (list-*.md) that drift from source of truth
  - No visual board for artifact status
depends-on:
  - SPIKE-001
evidence-pool: ""
---

# Backlog.md for artifact management

## Question

Should swain-design use [Backlog.md](https://github.com/MrLesk/Backlog.md) to manage artifact lifecycle instead of the current frontmatter-scanning + specgraph approach?

### Current approach (swain-design + specgraph)

Each artifact is a standalone `.md` file with YAML frontmatter, organized in phase subdirectories:

```
docs/spec/Draft/(SPEC-001)-Title/(SPEC-001)-Title.md
docs/spec/Active/(SPEC-002)-Title/(SPEC-002)-Title.md
docs/epic/Proposed/(EPIC-001)-Title/(EPIC-001)-Title.md
```

- **specgraph.sh** rebuilds the dependency graph by `find`-ing all `.md` files and regex-extracting frontmatter
- Phase transitions require `git mv` of the entire directory to a new phase subdirectory
- `list-*.md` index files are manually maintained supplements
- Artifact discovery requires recursive find + frontmatter extraction

### What Backlog.md could offer

Backlog.md stores each item as an individual markdown file with metadata, queryable via CLI:

- `backlog task list -s "Draft"` — filter by status
- `backlog search "EPIC-001"` — full-text search across all items
- `backlog board` — terminal Kanban view of all items by status
- `backlog browser` — web UI with drag-and-drop phase transitions
- Status changes are metadata edits, not directory moves
- Labels support cross-referencing (`parent-epic:EPIC-001`, `depends-on:SPEC-002`)
- MCP server gives agents direct access without CLI wrapping

### Key tensions

1. **Backlog.md is designed for tasks, not document artifacts.** Swain artifacts (Vision, Epic, Spec, ADR, Spike, etc.) are rich documents with structured sections, not task cards. Can Backlog.md's task model accommodate multi-page specs with acceptance criteria tables, verification matrices, and lifecycle histories?

2. **Artifact content vs. metadata.** Backlog.md excels at metadata operations (status, labels, search, board views). But swain artifacts are primarily *content* — the spec body, the ADR rationale, the epic success criteria. Would Backlog.md manage just the metadata index while artifacts remain as standalone docs? Or would it own the entire file?

3. **11 artifact types with different lifecycles.** Backlog.md has a single status flow (To Do → In Progress → Done). Swain has type-specific phase progressions (e.g., Spec: Draft → Approved → Implementing → Implemented → Verified). Can Backlog.md's status model be extended or configured per type?

## Go / No-Go Criteria

1. **Rich content support**: Can a Backlog.md task file contain the full body of a swain artifact (multi-section markdown, tables, code blocks, mermaid diagrams) without the tool stripping or reformatting content? Pass if artifact content round-trips cleanly through create/edit/read.

2. **Custom status workflows**: Can Backlog.md be configured with per-type status progressions (not just To Do/In Progress/Done)? Or can custom statuses be used freely? Pass if swain's 11 artifact types can each have their own phase progression.

3. **Graph operations**: Can specgraph's core commands (`ready`, `blocked-by`, `tree`, `overview`) be reimplemented against Backlog.md's CLI or data format? Pass if dependency-aware queries work without a separate caching layer.

4. **Hybrid model feasibility**: If Backlog.md manages metadata/index only, can it point to external artifact files while keeping status, labels, and relationships in its own store? Pass if a clean separation between "index entry" and "content file" is achievable.

5. **specwatch equivalent**: Can Backlog.md detect stale cross-references (artifact A references artifact B, but B's status changed)? Pass if a validation command or watch mode exists, or if one can be built atop the MCP/CLI interface.

6. **Migration path**: Can existing `docs/` artifacts with frontmatter be imported into Backlog.md without losing metadata or content? Pass if a migration script can process all 11 artifact types.

## Pivot Recommendation

If Backlog.md cannot handle rich content or custom status workflows (criteria 1-2), consider a **metadata overlay** approach:

- Keep artifacts as standalone files in `docs/` (current model)
- Use Backlog.md as a parallel index that tracks status, relationships, and labels
- specgraph reads from Backlog.md instead of scanning frontmatter
- Phase transitions update the Backlog.md entry (one CLI call) instead of moving directories
- A sync script keeps frontmatter and Backlog.md entries aligned

This gets the query/visualization benefits without forcing artifacts into a task-shaped container.

## Findings

Results of the investigation (populated during Active phase).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-10 | 038f8db | Initial creation |
