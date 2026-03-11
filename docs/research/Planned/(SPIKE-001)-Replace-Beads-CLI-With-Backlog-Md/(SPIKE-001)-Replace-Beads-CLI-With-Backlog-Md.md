---
title: "Replace Beads CLI with Backlog.md"
artifact: SPIKE-001
status: Planned
author: cristos
created: 2026-03-10
last-updated: 2026-03-10
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

Results of the investigation (populated during Active phase).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-10 | 038f8db | Initial creation |
