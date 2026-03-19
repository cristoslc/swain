---
title: "Swain MCP Server"
artifact: EPIC-033
track: container
status: Proposed
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
parent-vision: VISION-003
parent-initiative: INITIATIVE-014
priority-weight: high
success-criteria:
  - MCP server exposes artifact CRUD, lifecycle transitions, chart queries, and methodology loading
  - MCP Prompts surface key workflows as slash commands in any MCP-compatible client
  - Server bundles as a Claude Code plugin (auto-start on install)
  - Server packages as Desktop Extension (.mcpb) for Claude Desktop Chat
  - Server publishable as npm package for any MCP client
  - Artifact state persists across sessions via SQLite
  - Deterministic lifecycle state machine (refuses invalid transitions)
depends-on-artifacts:
  - SPIKE-028
  - SPIKE-029
  - SPIKE-030
addresses: []
evidence-pool: ""
---

# Swain MCP Server

## Goal / Objective

Build `swain-mcp` — an MCP server that exposes swain's artifact lifecycle engine, decision-support patterns, and methodology loading as portable MCP primitives. This is the core portability investment: one server that works across Claude Code, Claude Desktop, VS Code, Cursor, JetBrains, and any other MCP-compatible client.

The server uses all three MCP primitives:
- **Tools** — artifact CRUD, lifecycle transitions, chart queries, status, task tracking, and `load_methodology` (the portable skill-chaining mechanism)
- **Prompts** — methodology templates for key workflows (`design`, `do`, `status`, `session`), surfaced as slash commands
- **Resources** — artifact definitions, templates, and current artifact content, available via URI

Near-term, the server complements existing skills (hybrid architecture). Medium-term, as MCP Sampling with Tools gains client support, the server can absorb orchestration and become the primary interface.

## Scope Boundaries

**In scope:**
- MCP server implementation (language TBD: TypeScript or Python)
- SQLite persistence layer for artifact state
- 10–15 Tools covering artifact lifecycle, chart, status, task tracking, and methodology loading
- MCP Prompts for `design`, `do`, `status`, `session` workflows
- MCP Resources for definitions, templates, and artifact content
- Claude Code plugin packaging (`plugin.json` with skills + MCP)
- Desktop Extension packaging (.mcpb)
- npm package for standalone MCP distribution

**Out of scope:**
- Remote hosting / Claude web Connector deployment (deferred until local proves value)
- MCP Sampling integration (deferred until client support matures)
- Replacing existing skills (they coexist in hybrid mode)
- Per-runtime bundle optimization (INITIATIVE-014 Phase 4)

## Child Specs

_To be created during implementation planning. Expected specs:_
- Core MCP server scaffold + SQLite persistence
- Artifact CRUD tools
- Lifecycle state machine tools
- Chart query tools
- `load_methodology` tool + methodology content
- MCP Prompts for key workflows
- MCP Resources for definitions and templates
- Claude Code plugin packaging
- Desktop Extension (.mcpb) packaging

## Key Dependencies

- SPIKE-028, SPIKE-029, SPIKE-030 — research findings inform design
- Python MCP SDK (FastMCP, 1.2.0+)
- Existing specgraph Python package (reuse for chart queries and artifact graph)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-18 | | Initial creation |
