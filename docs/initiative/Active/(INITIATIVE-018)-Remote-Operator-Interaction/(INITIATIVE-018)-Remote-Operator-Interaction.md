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

### Notification & Steering
Channel integrations that let the operator receive swain notifications (build results, approval requests, task completions) and send commands back. Builds on Claude Code Channels.

### Remote Approval
Forwarding decision points from unattended/swarming sessions so they don't stall. Requires understanding which sessions are blocked and routing prompts to the operator's active remote surface.

### Status Projection
Making the status dashboard, task state, and artifact progress visible outside the terminal. The swain-stage web UI (INITIATIVE-015) is the primary surface; channels and mobile are secondary.

## Child Epics

_None yet — decomposition pending research spike on channel integration feasibility._

## Small Work (Epic-less Specs)

_None yet._

## Key Dependencies

- **INITIATIVE-015** (swain-stage Redesign) — the web UI is the primary remote interaction surface for rich status and artifact views
- **INITIATIVE-005** (Operator Situational Awareness) — extends the "what needs my decision?" capability to remote contexts (INIT-005 currently scopes OUT external notifications; this initiative picks that up)
- **Claude Code Channels** — research preview; channel protocol and allowlist may change
- **Claude Code Remote Control** — server mode with `--spawn worktree` is directly relevant to multi-session remote access

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | a90ded8 | Initial creation, informed by trove claude-code-remote-interaction@08ec2b5 |
