---
title: "Replace Beads CLI with Backlog.md"
artifact: SPIKE-001
status: Active
author: cristos
created: 2026-03-10
last-updated: 2026-03-11
question: "Should swain-do replace bd (beads) CLI with Backlog.md as the task tracking backend?"
gate: Pre-MVP
risks-addressed:
  - bd installation friction (brew/cargo, platform-specific)
  - Dolt server runtime complexity (.beads/ directory, pid files, sockets, locks)
  - .beads/.gitignore hygiene burden (swain-doctor dedicates an entire section to this)
  - No web UI for task visualization
  - No native MCP server support in bd
depends-on: []
evidence-pool: ""
---

# Replace Beads CLI with Backlog.md

## Question

Should swain-do replace bd (beads) CLI with [Backlog.md](https://github.com/MrLesk/Backlog.md) (v1.40.0, MIT, 5.1k stars) as the task tracking backend?

### What is Backlog.md?

A markdown-native task manager designed for spec-driven AI development. Key properties:

- **Storage**: Each task is a `.md` file in a `backlog/` directory, tracked in git
- **CLI**: `backlog task create`, `backlog task edit`, `backlog task list`, `backlog search`, `backlog board` (terminal Kanban)
- **Web UI**: `backlog browser` launches a React app with drag-and-drop Kanban boards
- **MCP server**: `backlog mcp start` — native Claude Code integration
- **Install**: `npm i -g backlog.md` or `brew install backlog-md`
- **Config**: `backlog/config.yml` (project) + `~/backlog/user` (user overrides) — similar to swain's two-tier settings
- **AI workflow**: Built-in CLAUDE.md/AGENTS.md conventions, spec-driven task decomposition

### Why consider replacing bd?

bd introduces significant operational friction that swain-doctor has to compensate for:

- Installation requires brew or cargo (platform-specific)
- Runtime creates `.beads/` directory with Dolt database, sockets, pid files, lock files
- swain-doctor dedicates an entire section to `.beads/.gitignore` hygiene
- The fallback text ledger already exists because bd is unreliable to install
- Most swain users never use bd's advanced features (Dolt sync, remote supervision)
- bd has no web UI or visual task board
- bd has no MCP server

Backlog.md would:

- Install via npm/brew (broader platform support)
- Store tasks as plain markdown in git (no database, no runtime files)
- Eliminate the entire `.beads/` directory and its maintenance burden
- Provide terminal Kanban + web UI out of the box
- Offer MCP integration for direct Claude Code access
- Be human-readable and editable outside of swain

## Go / No-Go Criteria

1. **Term mapping coverage**: Can every operation in swain-do's term mapping table (implementation plan, task, origin ref, spec tag, dependency, ready work, claim, complete, abandon, escalate) be expressed in Backlog.md's CLI? Pass if ≥90% map cleanly.

2. **Dependency tracking**: bd supports `bd dep add`, `bd ready` (blocker-aware), and `bd blocked`. Does Backlog.md support task dependencies and blocker-aware readiness queries? Pass if equivalent functionality exists or can be approximated.

3. **Spec lineage tagging**: swain-do uses `--external-ref` (origin ref) and `--labels spec:SPEC-003` (spec tags) to link tasks to artifacts. Can Backlog.md labels/metadata serve the same purpose? Pass if tasks can be tagged and queried by artifact ID.

4. **bd doctor equivalent**: bd has `bd doctor --fix` for self-repair. Does Backlog.md have equivalent health checks? Pass if task file integrity can be validated.

5. **Migration path**: Can existing `.beads/` data be exported and re-created as Backlog.md task files? Pass if a migration script is feasible.

6. **MCP integration value**: Does the MCP server provide capabilities that improve the swain workflow beyond what CLI invocation offers? Evaluate whether swain-do should use the MCP server or continue with CLI wrapping.

## Pivot Recommendation

If Backlog.md cannot handle dependency tracking (criterion 2), consider:

- **Option A**: Use Backlog.md as the default backend for simple projects, retain bd as an opt-in backend for dependency-heavy projects. swain-do's abstraction layer already supports backend switching.
- **Option B**: Contribute dependency tracking to Backlog.md upstream (MIT license, active community with 25 contributors).

## Findings

**Verdict: HYBRID — contribute upstream, reassess after.**

### Criterion 1: Term mapping coverage — PARTIAL PASS (70%)

Backlog.md covers the core CRUD operations well:

| swain-do term | Backlog.md equivalent | Status |
|---|---|---|
| implementation plan | `backlog task create` with labels | OK |
| task | `backlog task create` | OK |
| origin ref | `backlog task create --metadata origin:SPEC-001` | OK (via metadata) |
| spec tag | `backlog task create --label spec:SPEC-003` | OK |
| dependency | **No CLI command** | FAIL |
| ready work | **No CLI command** | FAIL |
| claim | `backlog task edit --status "In Progress"` | OK |
| complete | `backlog task edit --status "Done"` | OK |
| abandon | `backlog task edit --status "Cancelled"` | OK (custom status) |
| escalate | No equivalent | FAIL |

The core gap is dependency tracking — there's no `backlog dep add`, `backlog ready`, or `backlog blocked` command.

### Criterion 2: Dependency tracking — FAIL (but algorithms exist internally)

Backlog.md's TypeScript source contains `computeSequences()` which implements Kahn's algorithm for topological sorting — the same algorithm needed for `ready` and `blocked` queries. However, this is only used internally for the board's sequence numbering. There are no CLI commands exposing dependency operations.

The task file format supports a `dependencies` metadata field, and the internal `TaskGraph` class can resolve them. The gap is purely at the CLI/MCP surface — the engine can do it, the interface doesn't expose it.

**Upstream contribution feasibility:** The codebase is TypeScript/Bun, MIT-licensed, with 25 contributors and active maintenance. Adding `backlog ready` and `backlog blocked` commands would require:
- Exposing `TaskGraph.getReadyTasks()` via CLI (~50 LOC)
- Adding a `--blocked` filter to `backlog task list` (~30 LOC)
- Adding `backlog dep add/remove` commands (~100 LOC)

This is a tractable contribution.

### Criterion 3: Spec lineage tagging — PASS

Labels and metadata fields are free-form strings. `backlog task create --label "spec:SPEC-003" --metadata "origin:EPIC-001"` works. Querying by label: `backlog task list --label "spec:SPEC-003"` returns matching tasks. This is equivalent to bd's `--external-ref` and `--labels` functionality.

### Criterion 4: bd doctor equivalent — PARTIAL PASS

Backlog.md has `backlog doctor` which validates task file integrity (YAML frontmatter parsing, required fields, orphaned references). It does not auto-fix issues — it reports them. This is weaker than `bd doctor --fix` but sufficient for diagnostics. swain-doctor could wrap the output and apply fixes.

### Criterion 5: Migration path — PASS

bd tasks can be exported via `bd list --format` and recreated as Backlog.md markdown files. A migration script would:
1. `bd list --format json` to dump all tasks
2. For each task, create a `.md` file in `backlog/tasks/` with the appropriate frontmatter
3. Map bd statuses to Backlog.md statuses
4. Translate `bd dep` relationships into `dependencies:` metadata

The .beads/ directory and Dolt database can be deleted after migration.

### Criterion 6: MCP integration value — PASS (significant)

Backlog.md's MCP server (`backlog mcp start`) provides:
- `task_create`, `task_edit`, `task_list`, `task_search` tools
- Direct Claude Code integration without CLI wrapping
- Structured JSON responses (no stdout parsing)
- Real-time board updates via SSE

This eliminates the fragile bd CLI wrapping in swain-do and enables agent-native task operations.

### Recommendation

**Do not replace bd today.** The dependency tracking gap (criterion 2) blocks a clean swap — swain-do relies heavily on `ready` and `blocked` queries for execution prioritization.

**Next steps:**
1. Contribute `ready`/`blocked`/`dep` commands to Backlog.md upstream (estimated: 1-2 days for a PR)
2. If accepted, build swain-do backend adapter for Backlog.md
3. If rejected or stalled, evaluate forking — the MIT license and TypeScript codebase make this low-risk
4. Retain bd as fallback until Backlog.md backend is proven

**Fork viability:** The codebase is ~8k LOC TypeScript/Bun, well-structured with clear separation between storage, CLI, and MCP layers. Forking to add dependency commands is straightforward. The risk is maintenance burden of a fork vs. upstream acceptance.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-10 | 038f8db | Initial creation |
| Active | 2026-03-11 | — | Investigation findings recorded |
