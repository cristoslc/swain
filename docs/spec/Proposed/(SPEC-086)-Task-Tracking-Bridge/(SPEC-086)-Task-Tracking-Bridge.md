---
title: "Task Tracking Bridge Tools"
artifact: SPEC-086
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
  - "`tk_query` returns task list with filtering by status (todo/in-progress/done/blocked), plan, and parent spec"
  - "`tk_update` changes task status and appends notes"
  - "`tk_create` creates tasks with title, description, and optional parent plan/spec linkage"
  - Tools shell out to the tk binary (skills/swain-do/bin/tk) — no reimplementation
  - Graceful error if tk binary not found (suggest installing swain)
swain-do: required
linked-artifacts:
  - SPEC-082
  - SPEC-090
---

# Task Tracking Bridge Tools

## Context

Swain uses `tk` (ticket) as its task tracking system — a vendored CLI binary managed by the `swain-do` skill. Agents working in any MCP client need to query and update tasks without having to drop into a terminal or invoke a Claude Code skill. The MCP server exposes `tk` operations as tools by shelling out to the existing binary rather than reimplementing task tracking logic.

This is a bridge, not a replacement. `swain-do` remains the authoritative interface for plan ingestion and complex task workflows. These tools cover the read-query and simple-write operations that an agent needs during execution.

## Scope

**In scope:**
- `tk_query` tool: list tasks with filtering by status (todo/in-progress/done/blocked), plan, and parent spec
- `tk_update` tool: update task status and append notes to an existing task
- `tk_create` tool: create a new task or plan with title, description, and optional parent plan/spec linkage

**Out of scope:**
- Full `tk` CLI reimplementation
- Plan ingestion from specs (that is `swain-do`'s responsibility)
- Complex workflow orchestration (pick-up, handoff, retry logic)

## Acceptance Criteria

- `tk_query` returns task list with filtering by status (todo/in-progress/done/blocked), plan, and parent spec
- `tk_update` changes task status and appends notes
- `tk_create` creates tasks with title, description, and optional parent plan/spec linkage
- Tools shell out to the tk binary (`skills/swain-do/bin/tk`) — no reimplementation
- Graceful error if tk binary not found (suggest installing swain)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-19 | | Initial creation |
