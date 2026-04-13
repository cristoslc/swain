---
title: "Chat Plugin System"
artifact: EPIC-072
track: container
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
parent-vision: VISION-006
parent-initiative: INITIATIVE-018
priority-weight: high
success-criteria:
  - Chat adapter plugin contract is defined and documented (NDJSON protocol, event/command types, routing metadata).
  - Reference Zulip plugin creates streams (rooms), topics (threads), posts events as messages, and routes operator messages back as commands.
  - Plugin handles continuous posting without rate limit violations.
  - Plugin surfaces approval requests with `@` mention of the operator.
  - Control thread per project room shows session inventory and accepts lifecycle commands.
  - Graceful failure on unrecognized events — surfaces warnings, not crashes.
depends-on-artifacts:
  - ADR-037
  - ADR-038
  - EPIC-070
  - DESIGN-022
addresses: []
evidence-pool: "chat-server-features"
---

# Chat Plugin System

## Goal / Objective

Define the chat adapter plugin contract and ship a reference Zulip plugin. The contract is the stable interface; the plugin is the first implementation. Community plugins for Slack, Telegram, Discord follow the same contract.

## Desired Outcomes

The operator installs a chat adapter plugin (e.g., `swain-chat-zulip`), points config at their Zulip Cloud org, and the bridge starts posting session events to chat. The plugin maps rooms to projects, topics to sessions, and surfaces the control thread for lifecycle commands.

## Scope Boundaries

**In scope:**
- Chat adapter NDJSON protocol specification (event types, command types, routing metadata, config format).
- Reference Zulip plugin (Python, using `zulip` SDK).
- Room/thread mapping for Zulip (stream = project, topic = session, pinned topic = control thread).
- Continuous posting behavior, `@` mentions for approvals.
- Graceful failure on unknown events.

**Out of scope:**
- Plugins for other platforms (Slack, Telegram, Discord) — community can build these against the contract.
- The host bridge routing logic (EPIC-070).
- The interaction design details (DESIGN-022 — consulted, not owned).

## Child Specs

_To be created during implementation planning._

## Key Dependencies

- EPIC-070 (Host Bridge Kernel) — spawns and communicates with the chat adapter.
- ADR-037 (Chat Platform) — Zulip Cloud as reference platform.
- ADR-038 (Microkernel Plugin Architecture) — defines the subprocess/NDJSON contract.
- DESIGN-022 (Chat Interface Interaction) — informs UX patterns.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | -- | Created from VISION-006 decomposition. |
