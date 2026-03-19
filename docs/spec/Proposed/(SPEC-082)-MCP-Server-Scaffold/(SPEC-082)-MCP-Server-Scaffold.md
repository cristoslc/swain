---
title: "MCP Server Scaffold + SQLite Persistence"
artifact: SPEC-082
track: implementation
status: Proposed
type: feature
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
parent-epic: EPIC-033
depends-on-artifacts: []
acceptance-criteria:
  - FastMCP server starts via `python -m swain_mcp` or `uvx swain-mcp`
  - SQLite database created at `.agents/swain.db` on first run
  - Schema supports all swain artifact types with frontmatter fields
  - Database indexes artifacts from docs/ directory on startup (scan and populate)
  - Health check tool returns server version and database stats
  - Server discoverable by Claude Code via `.mcp.json` config
swain-do: required
---

# MCP Server Scaffold + SQLite Persistence

## Context

Foundation for the swain-mcp server. Sets up a Python FastMCP server with SQLite for artifact state persistence. This is the base that all other specs build on. Without this scaffold, no artifact tooling (SPEC-083), lifecycle enforcement (SPEC-084), or chart queries (SPEC-085) can exist. The server must be self-contained enough to be installed via `uvx` and auto-discovered by Claude Code through `.mcp.json`.

## Scope

**In scope:**
- FastMCP server initialization and entry point (`python -m swain_mcp` and `uvx swain-mcp`)
- SQLite schema design: `artifacts` table with columns for `id`, `type`, `title`, `status`, `parent_refs`, `frontmatter_json`, `file_path`, and timestamps
- Database migration framework (versioned, idempotent migrations)
- Basic server startup and shutdown lifecycle
- Health check tool returning server version and database statistics
- Project root detection (walk up from cwd to find `.agents/` or `docs/`)
- Startup scan: index all artifacts from `docs/` directory into SQLite on first run

**Out of scope:**
- Specific artifact CRUD tools (SPEC-083)
- Lifecycle transition logic (SPEC-084)
- Chart and query tools (SPEC-085)

## Acceptance Criteria

- FastMCP server starts via `python -m swain_mcp` or `uvx swain-mcp`
- SQLite database created at `.agents/swain.db` on first run
- Schema supports all swain artifact types with frontmatter fields
- Database indexes artifacts from `docs/` directory on startup (scan and populate)
- Health check tool returns server version and database stats
- Server discoverable by Claude Code via `.mcp.json` config

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-19 | | Initial creation |
