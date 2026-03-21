---
title: "MCP Prompts for Key Workflows"
artifact: SPEC-088
track: implementation
status: Proposed
type: feature
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
parent-epic: EPIC-033
depends-on-artifacts:
  - SPEC-083
  - SPEC-087
acceptance-criteria:
  - Four prompts registered: design, do, status, session
  - Each prompt surfaces as `/mcp__swain__design` (etc.) in Claude Code and compatible clients
  - "`design` prompt accepts artifact_type and intent parameters, returns methodology for artifact creation"
  - "`do` prompt accepts spec_id parameter, returns task tracking methodology"
  - "`status` prompt returns current project status with ranked recommendations"
  - "`session` prompt returns session context (active work, recent changes, bookmarks)"
  - Prompts embed relevant resources (artifact definitions, templates) via MCP resource references
  - Prompts include chaining hints that reference load_methodology for sub-workflows
swain-do: required
linked-artifacts:
  - SPEC-083
  - SPEC-087
  - SPEC-090
---

# MCP Prompts for Key Workflows

## Context

MCP Prompts are parameterized message templates surfaced as slash commands in MCP-compatible clients. They are the direct analog of swain's current skill invocation — `/mcp__swain__design` replaces `/swain-design` on non-Claude-Code surfaces. Prompts can return multi-message sequences with embedded resources, making them richer than simple tool calls.

## Scope

**In:**
- Four MCP Prompts: `design` (artifact creation/management workflow), `do` (task tracking and execution workflow), `status` (project status and recommendations), `session` (session context and bookmarks)
- Each prompt accepts parameters (e.g., artifact type, spec ID) and returns methodology instructions + relevant context
- `design` prompt accepts `artifact_type` and `intent` parameters, returns methodology for artifact creation
- `do` prompt accepts `spec_id` parameter, returns task tracking methodology
- `status` prompt returns current project status with ranked recommendations
- `session` prompt returns session context (active work, recent changes, bookmarks)
- Prompts embed relevant resources (artifact definitions, templates) via MCP resource references
- Prompts include chaining hints that reference `load_methodology` for sub-workflows

**Out:**
- Sampling-based orchestration (future)
- Methodology loading logic (that's SPEC-087 — prompts call `load_methodology` internally)

## Acceptance Criteria

- Four prompts registered: `design`, `do`, `status`, `session`
- Each prompt surfaces as `/mcp__swain__design` (etc.) in Claude Code and compatible clients
- `design` prompt accepts `artifact_type` and `intent` parameters, returns methodology for artifact creation
- `do` prompt accepts `spec_id` parameter, returns task tracking methodology
- `status` prompt returns current project status with ranked recommendations
- `session` prompt returns session context (active work, recent changes, bookmarks)
- Prompts embed relevant resources (artifact definitions, templates) via MCP resource references
- Prompts include chaining hints that reference `load_methodology` for sub-workflows

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-19 | | Initial creation |
