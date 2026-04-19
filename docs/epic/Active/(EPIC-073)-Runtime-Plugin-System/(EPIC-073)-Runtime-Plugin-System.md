---
title: "Runtime Plugin System"
artifact: EPIC-073
track: container
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-18
parent-vision: VISION-006
parent-initiative: INITIATIVE-018
priority-weight: high
success-criteria:
  - Runtime adapter plugin contract is defined and documented (NDJSON protocol, event/command types).
  - Reference Claude Code adapter as subprocess plugin. Reference OpenCode adapter as subprocess plugin sharing a global opencode serve (EPIC-085). Reference Tmux adapter as subprocess plugin. Cancel support (POST /session/{id}/abort). Approval support (POST /session/{id}/permissions/{pid}).
  - Plugin handles session start, text output, tool calls, approval forwarding, and session end.
  - At least one additional runtime plugin (OpenCode or ACP-generic) demonstrates the contract works for multiple runtimes.
depends-on-artifacts:
  - ADR-038
  - EPIC-085
addresses: []
evidence-pool: "agentic-runtime-chat-adapters"
---

# Runtime Plugin System

## Goal / Objective

Define the runtime adapter plugin contract and ship reference plugins as subprocess executables speaking NDJSON over stdio. Runtime adapters are now true plugins (not in-process classes) per ADR-038.

## Desired Outcomes

Each session spawns a runtime adapter subprocess. The adapter translates between the runtime's native protocol and NDJSON over stdio. OpenCode, Claude Code, and Tmux adapters are reference implementations. Adapters can be written in any language.

## Scope Boundaries

**In scope:**
- Runtime adapter NDJSON protocol specification (event types, command types, config format).
- Reference Claude Code plugin (Python, wrapping CLI with streaming JSON).
- Second reference plugin: OpenCode (`--format json`) or ACP-generic (`agent-client-protocol` Python SDK).
- Tmux process wrapping (start CLI in tmux, attach adapter to stdout/stdin).
- Approval forwarding (runtime requests permission → plugin emits `approval_needed` → kernel routes to chat → operator responds → plugin sends approval back).

**Out of scope:**
- Chat-side rendering of runtime events (EPIC-072).
- TUI fallback for terminal-only runtimes (future).
- The project bridge kernel itself (EPIC-071).

## Child Specs

- SPEC-322: Project Bridge Microkernel Refactor (adapter subprocess integration)

## Key Dependencies

- EPIC-071 (Project Bridge Kernel) — spawns and communicates with runtime adapters.
- ADR-038 (Microkernel Plugin Architecture) — defines the subprocess/NDJSON contract.
- SPIKE-059 (Agent Runtime I/O Compatibility) — validated runtime JSON output formats.
- `agentic-runtime-chat-adapters` trove — ACP Python SDK, ACPX ecosystem.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | -- | Created from VISION-006 decomposition. |
| Active | 2026-04-18 | -- | Updated for swain-helm architecture. Added EPIC-085 dependency. |
