---
title: "MCP Resources for Definitions and Templates"
artifact: SPEC-089
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
  - "`swain://definitions/{type}` returns the definition file for any artifact type (vision, initiative, epic, spec, spike, adr, persona, runbook, design, journey)"
  - "`swain://templates/{type}` returns the template file for any artifact type"
  - "`swain://artifacts/{id}` returns the full markdown content of an artifact by its ID (e.g., SPEC-082)"
  - "`swain://chart` returns the current artifact hierarchy (JSON graph from specgraph)"
  - Resource list endpoint returns all available resources with descriptions
  - Resources sourced from the project's docs/ and skills/swain-design/references/ directories
swain-do: required
---

# MCP Resources for Definitions and Templates

## Context

MCP Resources provide structured data/context that models or users can read via URI-addressed references. For swain, resources expose artifact type definitions, templates, and current artifact content — making the project's documentation structure accessible from any MCP client.

## Scope

**In:**
- Resource URI patterns:
  - `swain://definitions/{type}` — artifact type definitions
  - `swain://templates/{type}` — artifact templates
  - `swain://artifacts/{id}` — current artifact content by ID
  - `swain://chart` — current hierarchy graph
- Resource list endpoint for discovery

**Out:**
- Dynamic resource subscriptions (future)
- Resource templates with user input (future)

## Acceptance Criteria

- `swain://definitions/{type}` returns the definition file for any artifact type (vision, initiative, epic, spec, spike, adr, persona, runbook, design, journey)
- `swain://templates/{type}` returns the template file for any artifact type
- `swain://artifacts/{id}` returns the full markdown content of an artifact by its ID (e.g., SPEC-082)
- `swain://chart` returns the current artifact hierarchy (JSON graph from specgraph)
- Resource list endpoint returns all available resources with descriptions
- Resources sourced from the project's docs/ and skills/swain-design/references/ directories

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-19 | | Initial creation |
