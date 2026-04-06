---
title: "Runtime Plugin System"
artifact: EPIC-073
track: container
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
parent-vision: VISION-006
parent-initiative: INITIATIVE-018
priority-weight: high
success-criteria:
  - Runtime adapter plugin contract is defined and documented (NDJSON protocol, event/command types).
  - Reference Claude Code plugin wraps `claude --output-format stream-json` and `--input-format stream-json`.
  - Plugin handles session start, text output, tool calls, approval forwarding, and session end.
  - At least one additional runtime plugin (OpenCode or ACP-generic) demonstrates the contract works for multiple runtimes.
depends-on-artifacts:
  - ADR-038
  - EPIC-071
addresses: []
evidence-pool: "agentic-runtime-chat-adapters"
---

# Runtime Plugin System

## Goal / Objective

Define the runtime adapter plugin contract and ship reference plugins for Claude Code and at least one other runtime. The contract is the stable interface; plugins translate between runtime-specific I/O and the kernel's published language.

## Desired Outcomes

The operator can configure which runtime to use per session. The project bridge spawns the correct runtime adapter plugin, which wraps the headless CLI in tmux. Events (tool calls, text, approvals) flow through the plugin to the project bridge. Commands (prompts, approvals) flow back.

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

_To be created during implementation planning._

## Key Dependencies

- EPIC-071 (Project Bridge Kernel) — spawns and communicates with runtime adapters.
- ADR-038 (Microkernel Plugin Architecture) — defines the subprocess/NDJSON contract.
- SPIKE-059 (Agent Runtime I/O Compatibility) — validated runtime JSON output formats.
- `agentic-runtime-chat-adapters` trove — ACP Python SDK, ACPX ecosystem.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | -- | Created from VISION-006 decomposition. |
