---
title: "Backlog.md for artifact management"
artifact: SPIKE-002
status: Active
author: cristos
created: 2026-03-10
last-updated: 2026-03-11
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

**Verdict: REJECT — fundamental impedance mismatch. Improve specgraph instead.**

### Criterion 1: Rich content support — FAIL

Backlog.md's task serializer strips or reformats content that doesn't fit its expected task structure. Investigation found:

- **Custom frontmatter fields are dropped.** Backlog.md's `TaskSerializer` recognizes a fixed set of fields (`title`, `status`, `priority`, `labels`, `assignee`, `created`, `updated`, `dependencies`). Swain artifacts use type-specific fields (`question`, `gate`, `risks-addressed`, `evidence-pool`, `parent-epic`, `parent-vision`, `acceptance-criteria`, etc.) — these are silently discarded on write.
- **Body content survives** read/write cycles if it's plain markdown, but structured sections (verification matrices, lifecycle tables with pipe formatting, mermaid diagrams) may have whitespace/formatting altered by the serializer's markdown normalization.
- **Multi-page artifacts** (some swain specs exceed 500 lines) are technically storable but the tool's UX assumes task-sized content — `backlog task edit` opens the full file in an editor, `backlog board` truncates display.

This is a fundamental mismatch: Backlog.md is designed for task cards (title + short description + metadata), not document artifacts (rich multi-section content with domain-specific frontmatter).

### Criterion 2: Custom status workflows — FAIL

Backlog.md's status model uses a single configurable list in `config.yml`:

```yaml
statuses:
  - To Do
  - In Progress
  - Done
```

Custom statuses can be added to this list, but:
- **One status list applies to all tasks.** There is no per-type status progression. A SPEC and a SPIKE would share the same status options.
- Swain has 11 artifact types, each with a different lifecycle (e.g., Spec: Draft → Approved → Implementing → Implemented → Verified; Spike: Planned → Active → Complete; ADR: Proposed → Accepted/Declined/Superseded). A single status list would need to contain the union of all ~30 distinct statuses, making the Kanban board and filtering noisy and confusing.
- **No transition validation.** Backlog.md allows any status → any status. Swain's phase progressions are directional (a Spec can't go from Implementing back to Draft without an explicit revert). There's no way to enforce this.

### Criterion 3: Graph operations — PARTIAL PASS (but not worth it)

Backlog.md's internal `TaskGraph` could theoretically support `ready`/`blocked` queries (see SPIKE-001 findings). However, reimplementing specgraph's full command set (`blocks`, `blocked-by`, `tree`, `overview`, `mermaid`) against Backlog.md's data format would require:
- Custom CLI commands or MCP tools (not upstream-ready since they're artifact-specific, not task-specific)
- A translation layer between swain's artifact model and Backlog.md's task model
- Maintaining parity between two graph implementations

This is more work than improving specgraph directly, with no net benefit.

### Criterion 4: Hybrid model feasibility — POSSIBLE but unjustified

A metadata overlay (Backlog.md as index, artifacts as standalone files) is technically feasible:
- Backlog.md task files could contain only metadata (status, labels, dependencies) with a `content-file:` field pointing to the real artifact
- A sync script would keep frontmatter and Backlog.md entries aligned

However, this adds a second source of truth and a synchronization burden. The risks it addresses (specgraph rebuild cost, fragile frontmatter parsing) are better solved by improving specgraph directly.

### Criterion 5: specwatch equivalent — FAIL

Backlog.md has no validation command for cross-references. It doesn't track which tasks reference other tasks in their body content — only explicit `dependencies:` metadata. Building a specwatch equivalent on top of Backlog.md would require the same file-scanning approach that specgraph already uses.

### Criterion 6: Migration path — PASS (but moot)

A migration script is feasible: scan `docs/` artifacts, extract frontmatter, create Backlog.md task files. But since the verdict is reject, migration is not needed.

### Recommendation

**Do not adopt Backlog.md for artifact management.** The impedance mismatch is fundamental — Backlog.md manages tasks (small, uniform, metadata-centric), while swain manages document artifacts (large, type-diverse, content-centric).

**Instead, improve specgraph:**

1. **Replace regex-based YAML extraction with a proper parser.** Use Python's `yaml` module or `yq` instead of `sed`/`grep` regex. This addresses the "fragile frontmatter parsing" risk.
2. **Add `specgraph board` command.** Render a terminal Kanban view of artifacts by status, similar to Backlog.md's `backlog board`. This addresses the "no visual board" risk.
3. **Eliminate `git mv` for phase transitions.** Status changes should update frontmatter in-place. The phase subdirectory convention (`Draft/`, `Active/`, etc.) can be kept as an organizational hint but shouldn't be the source of truth — frontmatter `status:` already is.
4. **Add incremental rebuild.** Track file mtimes and only re-extract frontmatter for changed files, instead of scanning all `.md` files. This addresses the rebuild cost risk.
5. **Add `description` field to nodes** (already implemented in this session).

### Fork viability assessment

Forking Backlog.md to make it artifact-aware would require:
- Extending the serializer to preserve arbitrary frontmatter fields
- Adding per-type status workflow configuration
- Modifying the board/browser UI to handle multi-page content
- Adding graph query commands

This would be a substantial fork (~2k+ LOC changes) that diverges significantly from upstream's task-management focus. Maintenance burden would be high and upstream merge potential low. **Not recommended.**

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-10 | 038f8db | Initial creation |
| Active | 2026-03-11 | — | Investigation findings recorded |
