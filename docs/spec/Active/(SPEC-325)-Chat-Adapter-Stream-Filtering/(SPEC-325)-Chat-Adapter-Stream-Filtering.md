---
title: "Chat Adapter Stream Filtering"
artifact: SPEC-325
track: implementable
status: Active
author: cristos
created: 2026-04-18
last-updated: 2026-04-18
priority-weight: medium
type: feature
parent-epic: EPIC-072
parent-initiative: ""
linked-artifacts:
  - ADR-046
  - EPIC-072
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Chat Adapter Stream Filtering

## Problem Statement

Each project bridge's chat adapter receives all messages from all streams. Without per-stream filtering, every bridge processes messages intended for other projects, wasting compute and creating routing ambiguity. The adapter needs a narrow subscription limited to its project's stream, plus client-side routing to direct messages to the correct session based on topic.

## Desired Outcomes

Each ZulipChatAdapter subscribes to exactly one stream (its project's stream). Messages are routed by topic: worktree topics route to the corresponding session, the control topic routes to the control handler. No host-scope topic handling — host commands are handled by the project bridge directly.

## External Behavior

**Narrow subscription:** `ZulipChatAdapter._poll_zulip` uses a narrow filter for its project's stream only.

**Topic routing:**
- Messages in a worktree topic (e.g., "trunk", "feature-x") → that worktree's session.
- Messages in the control topic → `control_message` handler.
- No host-scope topic handling.

**Topic naming convention:**
- Trunk → topic "trunk".
- Worktrees → branch name directly as topic.

## Acceptance Criteria

1. **Given** a ProjectBridge for project "swain", **when** its `ZulipChatAdapter` subscribes, **then** it uses a narrow filter for the "swain" stream only.

2. **Given** a message arrives in a worktree topic (e.g., "feature-x"), **when** the adapter routes it, **then** it is delivered to that worktree's session.

3. **Given** a message arrives in the control topic, **when** the adapter routes it, **then** it is delivered to the `control_message` handler.

4. **Given** the topic naming convention, **when** trunk messages arrive, **then** they are routed to topic "trunk"; worktree messages are routed by branch name directly.

5. **Given** the adapter receives a message, **when** it routes, **then** there is no host-scope topic handling — host commands are handled by the project bridge directly.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- ~60 lines of modification to existing ZulipChatAdapter.
- Narrow filter is implemented at the Zulip API subscription level — not a post-fetch filter.
- Topic routing is client-side within the adapter's message handler.
- No changes to the Zulip API client library — just the filter parameter to the existing subscribe/poll calls.
- This spec does not define what the control topic name is; that is project-level config.

## Implementation Approach

1. Update `_poll_zulip` to pass a narrow filter parameter: `{"stream": project_stream_name}`.
2. In the message handler, extract the topic from each incoming message.
3. If topic matches a known worktree branch (from WorktreeScanner or SessionRegistry), route to that session.
4. If topic is the control topic, route to `control_message` handler.
5. Remove any existing host-scope topic handling code — replace with project bridge direct handling.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-18 | -- | Initial creation |