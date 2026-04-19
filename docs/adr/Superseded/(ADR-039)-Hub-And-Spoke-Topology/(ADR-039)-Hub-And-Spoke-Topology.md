---
title: "Hub-and-Spoke Topology"
artifact: ADR-039
track: standing
status: Superseded
superseded-by: ADR-046
author: cristos
created: 2026-04-06
last-updated: 2026-04-18
linked-artifacts:
  - VISION-006
  - INITIATIVE-018
  - ADR-038
depends-on-artifacts:
  - ADR-038
evidence-pool: ""
---

# Hub-and-Spoke Topology

## Context

The system has three component types that need to communicate: the host bridge, project bridges, and the chat adapter. A single chat bot account serves all projects in a security domain (one Zulip bot posts to many rooms). The question is: who routes events between project bridges and the shared chat adapter?

## Decision

Hub-and-spoke with the host bridge as the hub.

```
Chat Adapter ←→ Host Bridge ←→ Project Bridge (swain)
                            ←→ Project Bridge (rk)
                            ←→ Project Bridge (houseops)
```

The host bridge:
- Spawns and supervises project bridges.
- Spawns the shared chat adapter plugin (one per security domain).
- Routes events from project bridges to the chat adapter (with bridge ID for room routing).
- Routes commands from the chat adapter to the correct project bridge.

Project bridges never talk to the chat adapter directly. They emit events and receive commands through the host bridge.

If the host bridge goes down, all project bridges in that domain stop cleanly. It is unsafe to continue unmonitored agent sessions without the operator's steering surface.

The host bridge is scoped to a security domain, not a physical host. One machine can run multiple host bridges (personal, work, client-A). Each sees only its own projects via an include/exclude list.

## Alternatives Considered

- **Direct connection: each project bridge talks to the chat adapter.** Eliminates the hub but means N project bridges each maintain a chat connection. The shared bot account posts to all rooms, so each bridge would need to filter for its own room. Harder to reason about, harder to secure (each bridge has chat credentials).
- **Chat adapter as hub.** The chat adapter routes between project bridges and the chat service. Possible but makes the chat adapter (a plugin, operator-replaceable) the most critical component. The host bridge (kernel code, not a plugin) is a better trust anchor.
- **Peer-to-peer: all components discover each other.** Over-engineered for a single-operator system with known topology.

## Consequences

- The host bridge is the single point of failure for its security domain. Acceptable — if the hub dies, stopping everything is the safe default.
- Project bridges are simpler — they manage sessions and runtimes, nothing about chat.
- The chat adapter is simpler — it receives pre-routed events with bridge IDs, posts to the right room/thread.
- Event latency adds one hop (project bridge → host bridge → chat adapter) but this is local IPC over stdio, not network — sub-millisecond.
- The NDJSON protocol needs a `bridge` routing field on every event and command.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | -- | Decided during VISION-006 brainstorming. |
| Superseded | 2026-04-18 | -- | Superseded by ADR-046 (project-level microkernel). |
