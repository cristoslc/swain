---
title: "Remote Operator Interaction"
artifact: INITIATIVE-018
track: container
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-04-06
parent-vision: VISION-006
priority-weight: high
success-criteria:
  - Operator can steer, monitor, and approve agent work from phone or messaging app without losing local environment context
  - Approval prompts forwarded to a remote surface so unattended sessions don't stall indefinitely
  - Status dashboard information accessible outside the terminal (via swain-stage web UI, channel, or mobile)
  - At least one channel integration (Telegram or Discord) delivering swain notifications and accepting operator commands
depends-on-artifacts: []
linked-artifacts:
  - INITIATIVE-014
  - INITIATIVE-015
  - INITIATIVE-005
addresses: []
trove: "claude-code-remote-interaction@08ec2b5"
---

# Remote Operator Interaction

## Strategic Focus

Enable the swain operator to interact with running agent sessions from anywhere — phone, messaging app, browser, or programmatic API — without sacrificing the local environment context that makes swain valuable.

Today, swain requires the operator to be at the terminal. Swarming sessions, long-running builds, and dispatched agents all produce decision points that stall until someone is physically present. Meanwhile, Claude Code has shipped three remote interaction modes (Channels, Remote Control, Headless/Agent SDK) that swain doesn't yet leverage.

This initiative is about **using** those capabilities to extend swain's operator loop beyond the terminal. It is not about building the surfaces themselves (that's INITIATIVE-015 for the web UI) or making swain run on other AI runtimes (that's INITIATIVE-014). It's about the operator's ability to stay in the loop from wherever they are. While the initial implementation targets Claude Code's channel/RC primitives, the principles are runtime-agnostic — other runtimes will provide their own remote interaction primitives that swain should leverage the same way.

Core principles:
1. **Local execution, remote steering** — agents run on the operator's machine with full filesystem/MCP/tool access. Remote surfaces are windows into that, not replacements for it.
2. **Decision support travels** — status dashboard recommendations, approval prompts, and completion notifications should reach the operator on their preferred surface.
3. **Leverage platform primitives** — use each runtime's native remote interaction capabilities (Claude Code's Channels/RC/Agent SDK today, others tomorrow) rather than building parallel infrastructure.
4. **Async-first** — the operator fires off work and checks back later. The system must handle delays between "agent needs a decision" and "operator responds."
5. **Multi-session awareness** — swain already supports swarming. Remote interaction must work across concurrent sessions, not just a single one.

## Scope Boundaries

**In scope:**
- Channel integration for swain notifications and operator commands (Telegram and/or Discord)
- Remote approval flows — forwarding permission/decision prompts to a remote surface
- Surfacing swain-session status/dashboard and swain-do state through remote-accessible interfaces
- Integration patterns between channels and the swain-stage web UI (INITIATIVE-015)
- Headless/Agent SDK patterns for programmatic swain interaction (extending swain-dispatch)
- Multi-session remote awareness — knowing which swarming session needs attention

**Out of scope:**
- Building the swain-stage web UI itself (INITIATIVE-015's domain)
- Making swain run on non-Claude-Code runtimes (INITIATIVE-014's domain)
- Building custom MCP channel servers — we use what Anthropic ships during research preview
- Always-on daemon mode (blocked on Claude Code adding persistent background support)
- Self-hosted infrastructure — outbound-only connections per Claude Code's security model

## Tracks

### Chat Bridge (v1)
Microkernel architecture with host bridge (hub), project bridges (spokes), and operator-replaceable plugins for chat adapters and runtime adapters. Hosted chat platforms (Zulip Cloud) as default — zero ops for adopters. Hub-and-spoke topology with NDJSON over stdio for polyglot plugin system.

### Web Pipe (v2, deferred)
Project-generated web content served via tunnel infrastructure from project hosts. Architecturally separate from the chat bridge.

## Child Epics

- EPIC-070 (Host Bridge Kernel) — hub daemon, session discovery, bridge lifecycle, event routing.
- EPIC-071 (Project Bridge Kernel) — session orchestrator, artifact binding, runtime plugin spawn.
- EPIC-072 (Chat Plugin System) — plugin contract + reference Zulip plugin.
- EPIC-073 (Runtime Plugin System) — plugin contract + reference Claude Code plugin.
- EPIC-074 (Provisioning / swain-stage) — one-command setup.

## Small Work (Epic-less Specs)

_None yet._

## Key Dependencies

- ADR-037 (Chat Platform and Deployment Model) — Zulip Cloud as default.
- ADR-038 (Microkernel Plugin Architecture) — subprocess + NDJSON plugin contract.
- ADR-039 (Hub-and-Spoke Topology) — host bridge as hub.
- INITIATIVE-015 (swain-stage Redesign) — the web UI is a v2 surface for the web pipe track.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | a90ded8 | Initial creation, informed by trove claude-code-remote-interaction@08ec2b5. |
| Active | 2026-04-06 | -- | Scope update: evolved to microkernel architecture, hosted platforms, hub-and-spoke topology. Re-parented under VISION-006. Decomposed into 5 epics. |
