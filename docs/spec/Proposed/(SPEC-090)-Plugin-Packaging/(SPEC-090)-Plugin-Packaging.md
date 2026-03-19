---
title: "Plugin + Desktop Extension Packaging"
artifact: SPEC-090
track: implementation
status: Proposed
type: feature
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
parent-epic: EPIC-033
depends-on-artifacts:
  - SPEC-082
  - SPEC-083
  - SPEC-084
  - SPEC-085
  - SPEC-086
  - SPEC-087
  - SPEC-088
  - SPEC-089
acceptance-criteria:
  - Claude Code plugin installs via standard plugin mechanism and auto-starts the MCP server
  - Plugin bundles existing swain skills alongside MCP server — both coexist (hybrid architecture)
  - Desktop Extension (.mcpb) installs in Claude Desktop Chat via drag-and-drop
  - npm package works via `npx swain-mcp` for standalone MCP server usage
  - Plugin persistent data uses `${CLAUDE_PLUGIN_DATA}` for SQLite database
  - Installation tested on Claude Code, Claude Desktop Chat, and one non-Anthropic client (e.g., Cursor)
swain-do: required
---

# Plugin + Desktop Extension Packaging

## Context

The distribution layer. Packages the swain-mcp server for three surfaces: Claude Code plugin (`plugin.json` bundling skills + MCP config, auto-start), Desktop Extension (`.mcpb` for Claude Desktop Chat, one-click install), and npm package (standalone MCP for any client).

## Scope

**In:**
- `plugin.json` manifest bundling existing swain skills alongside MCP server config
- `.mcpb` packaging via `npx @anthropic-ai/mcpb pack`
- npm package configuration for `npx swain-mcp` standalone usage
- Installation documentation for each surface

**Out:**
- Remote MCP server hosting (for Claude web Connectors — deferred)
- MCP Registry submission (deferred until registry GA)
- Per-runtime bundle optimization (Phase 4)

## Acceptance Criteria

- Claude Code plugin installs via standard plugin mechanism and auto-starts the MCP server
- Plugin bundles existing swain skills alongside MCP server — both coexist (hybrid architecture)
- Desktop Extension (`.mcpb`) installs in Claude Desktop Chat via drag-and-drop
- npm package works via `npx swain-mcp` for standalone MCP server usage
- Plugin persistent data uses `${CLAUDE_PLUGIN_DATA}` for SQLite database
- Installation tested on Claude Code, Claude Desktop Chat, and one non-Anthropic client (e.g., Cursor)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-19 | | Initial creation |
