---
title: "MCP as Distribution Layer"
artifact: SPIKE-030
track: container
status: Active
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
question: "Can MCP (Model Context Protocol) serve as swain's primary distribution layer — packaging skill capabilities as MCP tools/resources that any MCP-compatible client can consume?"
gate: Pre-MVP
parent-initiative: INITIATIVE-014
risks-addressed:
  - Building on a protocol that doesn't have sufficient adoption or stability
  - MCP's tool model being too narrow for swain's workflow-oriented patterns
evidence-pool: ""
---

# MCP as Distribution Layer

## Summary

<!-- Populated on completion -->

## Question

Can MCP (Model Context Protocol) serve as swain's primary distribution layer — packaging skill capabilities as MCP tools/resources that any MCP-compatible client can consume?

## Go / No-Go Criteria

- **Go**: MCP's tool + resource model can express swain's core capabilities (artifact CRUD, lifecycle transitions, status queries, chart navigation), AND at least 3 clients support MCP (Claude desktop, Claude web, plus one non-Anthropic client)
- **No-Go**: MCP's model is too primitive for stateful workflows (e.g., no session persistence, no file system access, no multi-step tool chaining), or adoption is limited to a single client

## Pivot Recommendation

If MCP is insufficient, fall back to surface-specific packaging: system prompts for Claude web, native skills for Claude Code, and AGENTS.md for runtimes that support it. Accept fragmentation and minimize per-surface maintenance via shared markdown source.

## Findings

<!-- Populated by research -->

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | | Initial creation |
