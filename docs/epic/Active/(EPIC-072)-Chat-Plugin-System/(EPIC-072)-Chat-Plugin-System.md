---
title: "Chat Plugin System"
artifact: EPIC-072
track: container
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-18
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
  - Stream narrow filtering per project bridge.
  - Topic naming from worktree branch names (trunk, feature-x).
  - Control topic commands handled directly by project bridge.
depends-on-artifacts:
  - ADR-037
  - ADR-038
  - DESIGN-022
addresses: []
evidence-pool: "chat-server-features"
---

# Chat Plugin System

## Goal / Objective

Define the chat adapter plugin contract and ship a reference Zulip plugin that operates as a subprocess of the ProjectBridge, scoped to one Zulip stream with worktree-based topic routing.

## Desired Outcomes

Each ProjectBridge spawns its own ZulipChatAdapter subprocess. The adapter subscribes to one Zulip stream with a narrow filter, routes messages by topic to worktree sessions, and handles control topic commands. One bot account is shared across all project bridges.

## Scope Boundaries

**In scope:**
- Chat adapter NDJSON protocol specification (event types, command types, routing metadata, config format).
- Reference Zulip plugin (Python, using `zulip` SDK).
- Room/thread mapping for Zulip (stream = project, topic = session, pinned topic = control thread).
- Stream narrow filtering for multi-bridge coexistence.
- Topic routing by worktree branch name.
- Continuous posting behavior, `@` mentions for approvals.
- Graceful failure on unknown events.

**Out of scope:**
- Plugins for other platforms (Slack, Telegram, Discord) — community can build these against the contract.
- The interaction design details (DESIGN-022 — consulted, not owned).

## Child Specs

SPEC-325: Chat Adapter Stream Filtering

## Key Dependencies

- ADR-037 (Chat Platform) — Zulip Cloud as reference platform.
- ADR-038 (Microkernel Plugin Architecture) — defines the subprocess/NDJSON contract.
- DESIGN-022 (Chat Interface Interaction) — informs UX patterns.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | -- | Created from VISION-006 decomposition. |
| Active | 2026-04-18 | -- | Updated for swain-helm architecture. Removed EPIC-070 dependency. |
