---
title: "Chart + Status Query Tools"
artifact: SPEC-085
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
acceptance-criteria:
  - "`chart_query` supports at minimum: default hierarchy tree, scope (parent chain + siblings), ready (actionable items), and unanchored views"
  - "`chart_query` reuses specgraph package — no reimplementation of graph logic"
  - "`status_dashboard` returns structured data: active epics with child spec counts by phase, blocked items, and a ranked recommendation"
  - Both tools work without any skill context (pure MCP, no SKILL.md dependency)
swain-do: required
---

# Chart + Status Query Tools

## Context

Swain's decision-support value depends on being able to answer "what's the state of the project?" from any MCP client — not just Claude Code. Today that visibility lives in the `swain-status` skill and the `specgraph` Python package (in `skills/swain-design/scripts/specgraph/`). The MCP server needs to expose these queries as tools so operators and agents can get hierarchy trees, ready views, blocked item lists, and ranked recommendations without invoking a skill or loading a SKILL.md.

Crucially, `specgraph` already implements the artifact graph traversal, view generation, and recommendation logic. These tools wrap it — they do not reimplement it.

## Scope

**In scope:**
- `chart_query` tool: hierarchy tree (default), scope/ancestry (parent chain + siblings), ready view (actionable items), recommend view (ranked next steps), debt view, and unanchored view — all delegating to the specgraph package
- `status_dashboard` tool: aggregated project status returning active epics with progress ratios (child spec counts by phase), blocked items, and a ranked recommendation

**Out of scope:**
- Task tracking tools (SPEC-086)
- Methodology loading (SPEC-087)
- MCP Prompts or Resources wrapping these queries (SPEC-088, SPEC-089)
- Any reimplementation of graph traversal or view logic from specgraph

## Acceptance Criteria

- `chart_query` supports at minimum: default hierarchy tree, scope (parent chain + siblings), ready (actionable items), and unanchored views
- `chart_query` reuses specgraph package — no reimplementation of graph logic
- `status_dashboard` returns structured data: active epics with child spec counts by phase, blocked items, and a ranked recommendation
- Both tools work without any skill context (pure MCP, no SKILL.md dependency)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-19 | | Initial creation |
