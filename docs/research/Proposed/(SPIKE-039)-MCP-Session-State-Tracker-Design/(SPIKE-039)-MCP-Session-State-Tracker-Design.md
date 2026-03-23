---
title: "MCP Session-State Tracker Design"
artifact: SPIKE-039
track: container
status: Proposed
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
question: "What is the minimum viable MCP server (or equivalent) that tracks session-level process state (artifacts consulted, skills invoked, transitions completed) so that stateless PreToolUse hooks can query it for compliance decisions?"
gate: Pre-MVP
parent-initiative: INITIATIVE-020
risks-addressed:
  - Stateless hooks cannot enforce session-aware process rules without an external state source
  - MCP server complexity may exceed maintenance budget for a personal tool
  - Session state tracking may introduce latency that degrades the agent experience
evidence-pool: "platform-hooks-validation@21aa91c"
linked-artifacts:
  - SPIKE-038
  - VISION-005
---

# MCP Session-State Tracker Design

## Summary

## Question

What is the minimum viable MCP server (or equivalent) that tracks session-level process state (artifacts consulted, skills invoked, transitions completed) so that stateless PreToolUse hooks can query it for compliance decisions?

## Go / No-Go Criteria

- **Go**: A lightweight MCP server (< 500 LOC) can track the 3–5 process events that matter (spec read, ADR check run, skill invoked, lifecycle transition) and respond to hook queries within 100ms
- **No-Go**: Session-state tracking requires deep integration with each platform's internal state (not just tool call observation), making it impractical without platform-specific code

## Pivot Recommendation

If an MCP server is too heavy, investigate:
1. **File-based state** — hooks write/read a session state file (`.swain/session-state.json`) that tracks process events. Simpler but not queryable across MCP boundaries.
2. **Claude Code `agent` hooks** — on Claude Code specifically, agent hooks can inspect context directly. Fall back to platform-specific solutions rather than a portable MCP server.

## Findings

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-22 | 730b957 | Initial creation |
