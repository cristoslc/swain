---
title: "Methodology Loading Tool"
artifact: SPEC-087
track: implementation
status: Proposed
type: feature
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
parent-epic: EPIC-033
depends-on-artifacts:
  - SPEC-082
acceptance-criteria:
  - "`load_methodology` accepts a methodology name and returns full instructional text as tool result"
  - "Available methodologies include: design, do, status, session, brainstorming, writing-plans, tdd, verification"
  - Methodology content is sourced from existing SKILL.md files or extracted methodology docs
  - "`list_methodologies` returns available methodologies with descriptions"
  - Returned text includes chaining hints (e.g., "when brainstorming is complete, call load_methodology with 'writing-plans'")
  - Works in any MCP client — no Claude Code-specific dependencies in the returned text
swain-do: required
---

# Methodology Loading Tool

## Context

Swain's workflow patterns — brainstorming, writing plans, test-driven development, verification before completion — are currently encoded in SKILL.md files that only activate inside Claude Code via the skill-chaining mechanism. Agents working in other MCP clients (Claude Desktop, VS Code, Cursor, JetBrains) cannot access these patterns today.

`load_methodology` is the portable bridge. It accepts a methodology name and returns the full instructional text as a tool result. The model reads that text and follows it — functionally equivalent to SKILL.md injection but working across any MCP client. This is the key innovation that makes swain's workflow patterns portable beyond Claude Code.

Chaining hints embedded in the returned text tell the model what to call next, replicating the skill-chaining table from AGENTS.md without requiring the client to understand it natively.

## Scope

**In scope:**
- `load_methodology` tool: accepts a methodology name, returns the full instructional text
- Methodology content sourced from SKILL.md files or dedicated methodology markdown files
- Methodology registry with at minimum: brainstorming, writing-plans, test-driven-development, verification-before-completion, swain-design, swain-do, swain-status, swain-session
- `list_methodologies` tool: returns available methodologies with descriptions
- Chaining hints embedded in returned text (e.g., next methodology to call on completion)
- Returned text is client-agnostic — no Claude Code-specific syntax or constructs

**Out of scope:**
- MCP Prompts surfacing methodologies as slash commands (SPEC-088)
- MCP Resources exposing methodology content by URI (SPEC-089)
- Sampling-based orchestration (deferred until client support matures)

## Acceptance Criteria

- `load_methodology` accepts a methodology name and returns full instructional text as tool result
- Available methodologies include: design, do, status, session, brainstorming, writing-plans, tdd, verification
- Methodology content is sourced from existing SKILL.md files or extracted methodology docs
- `list_methodologies` returns available methodologies with descriptions
- Returned text includes chaining hints (e.g., "when brainstorming is complete, call load_methodology with 'writing-plans'")
- Works in any MCP client — no Claude Code-specific dependencies in the returned text

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-19 | | Initial creation |
