---
title: "Untethered Operator"
artifact: VISION-006
track: standing
status: Active
product-type: personal
author: cristos
created: 2026-04-06
last-updated: 2026-04-18
priority-weight: high
linked-artifacts:
  - VISION-003
  - VISION-004
depends-on-artifacts: []
evidence-pool: ""
---

# Untethered Operator

## Target Audience

Myself — steering swain-governed projects from any surface: phone, tablet, desktop chat app, or browser. The terminal is one option, not the only one. Secondarily, any solo developer who wants agentic sessions reachable from anywhere.

## Value Proposition

Swain's alignment loop (Intent → Execution → Evidence → Reconciliation) requires an operator in the loop. Today that loop breaks when the operator steps away from the terminal. This vision keeps the loop running across devices and locations.

Every agentic coding runtime is a chatbot in a terminal box. The core interaction — send prompts, see output, approve tool use — maps to chat threads. By exposing headless runtimes through a chat interface, the operator can start, steer, and monitor work from anywhere. The terminal becomes backstage, not the front door.

This serves swain's sustainability principle directly. The operator's attention is finite. Chat threads organized by project and session reduce the cost of context-switching, session discovery, and status checks. The operator fires off work and checks back later — no terminal babysitting.

## Problem Statement

Working with swain today means using a terminal. Even at your desk, the TUI is the only way in. Four friction points:

- **Surface lock.** The operator might prefer a chat app over a terminal, even at their desk. The TUI is powerful but heavyweight for simple steering tasks — checking status, approving a tool call, sending a quick prompt.
- **Location lock.** Stepping away means losing the ability to steer, approve, or observe running sessions.
- **Device lock.** Phones can connect via tmux over SSH, but the TUI on a small screen is cramped and fragile.
- **Session discovery.** Finding which tmux session has the work, on which machine, in which project — manual navigation that a chat room hierarchy would make instant.

## Existing Landscape

- **Claude Code Remote Control** — syncs a session to claude.ai on phone/desktop. Claude-Code-only.
- **Claude Code Channels** — event-driven push to Telegram/Discord. Claude-Code-only. Research preview.
- **CloudCLI / claude-web-ui** — community projects wrapping Claude Code in a web UI. Single-runtime.
- **OpenClaw** — persistent AI worker across 15+ messaging platforms. General-purpose, not dev-focused.
- **Remote terminals (tmux + SSH)** — current workaround. Works but poor mobile UX.
- **Hosted chat platforms (Zulip Cloud, Slack, Discord)** — eliminate server ops entirely. The bot registers via API, operator uses existing mobile/desktop clients.
- **Commodore (cristoslc/commodore-infra)** — hexagonal infrastructure platform for self-hosted deployments and v2 tunnel/ingress needs.

No existing solution provides a runtime-agnostic chat interface for agentic development with project-level organization. But the infrastructure pieces exist — the novel work is the orchestration layer, not the chat server.

## Build vs. Buy

Tier 2 (glue existing tools). The components exist:

- Headless runtimes with JSON I/O (validated by [SPIKE-059](../../../spike/Complete/(SPIKE-059)-Agent-Runtime-IO-Compatibility-For-Mobile-Bridge/(SPIKE-059)-Agent-Runtime-IO-Compatibility-For-Mobile-Bridge.md)).
- Hosted chat platforms with bot APIs and mobile clients (Zulip Cloud, Slack, etc.). Self-hosted is an option, not a requirement.
- Commodore-infra for self-hosted deployments and (in v2) tunnel/ingress for the web pipe.

The novel work is the session orchestration layer — managing lifecycles, mapping projects to rooms, translating events between runtimes and chat, and routing sessions by artifact. Trove research on existing chat adapters for agentic runtimes will show how much of the bridge we can reuse.

## Maintenance Budget

Low. One person, hours per month. Components swap without touching the core. The session orchestrator and runtime adapters are custom code. Everything else is off-the-shelf.

The default path uses a hosted chat platform (e.g., Zulip Cloud) — zero server ops, the operator just registers a bot. Self-hosting on a VPS is an option for operators who need full control. Either way, the bot code is identical — the chat adapter speaks to an API regardless of where the server lives. Internal components (host bridges, project bridges, runtime adapters) run natively on project hosts — they need direct access to tmux, the filesystem, and runtime CLIs.

## Two Modalities

**v1: Chat bridge.** Chat threads that spawn, reconnect to, and steer headless agent sessions. Room per project, thread per session, optional artifact binding. This is the highest-return unlock — it works for swain itself and every swain-governed project. Architecture updated: ADR-039 (hub-and-spoke) superseded by ADR-046 (project-level microkernel). Host bridge removed. Each ProjectBridge is now a self-contained microkernel. Watchdog manages process lifecycle. See ADR-046 and ADR-047 for current decisions.

**v2: Web pipe.** Web content that projects produce (sites, dashboards, interactive UIs) served from project hosts via tunnel infrastructure. Links posted in chat threads. Architecturally separate from the chat bridge — this is where tunnels become necessary, since the content lives on machines behind NAT.

## Success Metrics

- Start an agent session on any swain project from a phone in under 30 seconds.
- Reconnect to a running session by tapping a chat thread.
- See pending approvals and recent output without opening a terminal.
- Support at least two runtimes (Claude Code + one other) from the same interface.

## Non-Goals

- Replacing the terminal — the TUI stays as the power-user interface for deep work.
- Building a custom chat protocol or client — we use existing servers and their mobile apps.
- Multi-user collaboration — single-operator system.
- Feature parity with the terminal — chat is for steering and monitoring, not deep debugging.
- Always-on cloud hosting for agents — agents run on the operator's machines. The chat service is hosted (or self-hosted on a VPS), but agents never leave the operator's hardware.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | db33601d | Created from brainstorming. Informed by SPIKE-059, INITIATIVE-018, trove claude-code-remote-interaction, commodore-infra. |
| Active | 2026-04-18 | -- | Architecture refactor: hub-and-spoke replaced by project-level microkernel (ADR-046, ADR-047). |
