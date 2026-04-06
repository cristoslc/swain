# Untethered Operator — Child Artifacts

**For:** VISION-006 (Untethered Operator)
**Date:** 2026-04-06

Planned child artifacts for the vision. These are created as separate numbered artifacts under the swain artifact system, not as supporting docs in this folder.

---

## Re-parenting

These existing artifacts move under VISION-006:

| Artifact | Current parent | Action |
|----------|---------------|--------|
| INITIATIVE-018 (Remote Operator Interaction) | VISION-001 (superseded) | Re-parent under VISION-006. Scope aligns: remote steering, approval flows, status projection. |

---

## Troves (research)

| Trove ID (proposed) | Topic | Why |
|---------------------|-------|-----|
| `chat-server-features` | Self-hostable chat servers — threads, rooms, bot APIs, mobile clients, resource footprint, self-hosting weight. | Chat protocol selection is an ADR that needs evidence. Campfire has no threads, Matrix has heavyweight homeservers, Zulip has streams+topics. The trove informs the trade-off. |
| `agentic-runtime-chat-adapters` | Existing projects that adapt agentic runtimes to web/chat UIs (CloudCLI, OpenClaw, claude-web-ui, etc.). What they built, what works, build-vs-buy assessment. | The personal product priority stack says find existing solutions first. If someone already built a runtime-to-chat bridge, we should use it. |
| `tunnel-proxy-provisioning` | Tools that automate DNS + TLS + reverse proxy + tunnel as a composable stack. Includes assessment of Commodore (cristoslc/commodore-infra). | v2 concern — tunnels are needed for the web pipe (content on project hosts behind NAT), not for the v1 chat bridge (chat server on VPS, directly reachable). |
| `process-supervision-patterns` | Daemon management across macOS (launchd), Linux (systemd), Docker (restart policies). | The orchestrator is swain's first persistent daemon. The maintenance budget demands reliability without manual babysitting. |

---

## Journeys

| ID (proposed) | Title | Scenario |
|---------------|-------|----------|
| JOURNEY-next | Phone check-in | Operator opens the chat thread on their phone and scrolls the live feed — tool calls, output, and progress post continuously. The bot `@`s the operator only when input is needed (approval, decision). The operator reads, optionally responds, and closes the app. No message required to check in. |
| JOURNEY-next | Fire and forget | Operator messages from phone: "in swain, work on SPEC-142." Bot spawns a session, binds to artifact, starts work. Operator checks back later. |
| JOURNEY-next | New project from phone | Operator wants to start a fresh project or clone a repo that doesn't exist on any host yet. Bot clones, initializes swain, provisions a room. |
| JOURNEY-next | Reconnect to existing session | Operator opens the project room. A status thread shows all active sessions (continuously updated by the bridge). Operator taps into a session thread and reads the live feed. |
| JOURNEY-next | Adopt terminal session into chat | Operator started a tmux session at their laptop (normal TUI workflow). The bridge polls for unmanaged tmux sessions and posts them to a status thread in the project room. Operator sees the session listed, replies to adopt it. The bridge attaches a runtime adapter and starts posting to a new thread. Operator walks away from the terminal and picks up in chat. |
| JOURNEY-next | Share web output | Agent builds something (Astro site, report). Operator taps a link in chat, sees it in browser. The session-scoped web output path. |

---

## Designs

| ID (proposed) | Domain | Title | Scope |
|---------------|--------|-------|-------|
| DESIGN-next | interaction | Chat interface interaction design | The operator's experience in the chat interface. **Design Intent — Context:** The chat interface is the operator's primary surface for steering agentic sessions across devices. **Goals:** Passive check-in requires zero typing (open thread, read feed). Active steering is low-friction and discoverable. Session/project navigation is instant via room hierarchy. Works equally on phone and desktop. **Constraints:** Must use chat protocol's native primitives (rooms, threads, messages, reactions) — no custom client. Single-operator. Bot posts continuously — design must handle high volume without overwhelming. Graceful failure when the bridge encounters an unrecognized runtime interaction (e.g., new prompt format) — unknown states surface as warnings, not fatal errors. **Non-goals:** Custom chat client for v1. Rich media beyond native chat support. Terminal-equivalent power. **Key patterns:** Each project room has a **control thread** where the host bridge lives — operator drops commands here to spawn sessions, discover existing ones, kill stuck sessions, restart work. This thread has agentic capability: assignment scheduling, session discovery, lifecycle management. Per-session threads are live feeds (bot posts continuously, `@`s operator only for input). Room-level status (pinned or top-level) shows all active/adoptable sessions. |
| DESIGN-next | system | Deployment topology | Where each component runs, connection directions, provisioning sequences, isolation modes. The full stack diagram with concrete deployment choices. |
| DESIGN-next | data | Orchestrator event schema | Full specification of the published language — all domain events and commands, field types, serialization format. The contract that all adapters conform to. |

---

## ADRs

| ID (proposed) | Decision | Context |
|---------------|----------|---------|
| ADR-next | Chat platform and deployment model | Hosted (Zulip Cloud, Slack, Discord) vs. self-hosted (Zulip, Conduwuit). Includes protocol selection and deployment model as one decision — they're coupled. Zulip Cloud is the leading candidate: best threading, same API as self-hosted, seamless migration path. Informed by `chat-server-features` trove. |
| ADR-next | Supported providers for stack components (v2) | Which tunnel, proxy, DNS, and cert tools are supported for the web pipe. Informed by `tunnel-proxy-provisioning` trove. Deferred — not needed for v1. |
| ADR-next | Chat adapter deployment location | Colocated with orchestrator on project host vs. colocated with chat service vs. standalone. Trade-offs: latency, security, operational complexity. |

---

## Spikes

| ID (proposed) | Question | Context |
|---------------|----------|---------|
| SPIKE-next | How does the orchestrator recover sessions after a host restart? | The orchestrator is a persistent daemon. When the host reboots, tmux sessions may or may not survive. The orchestrator needs to reconcile its registry with reality, report dead sessions, and offer respawn. |

---

## Specs

| ID (proposed) | Title | Context |
|---------------|-------|---------|
| SPEC-next | Provisioning commands | The `/swain` commands that provision infrastructure: bootstrap full stack (first project), register bridge (subsequent projects), provision isolated stack (security-sensitive). What they automate, what requires manual steps. |

---

## Relationship to VISION-003

VISION-003 (Swain Everywhere) should be renamed to reflect its actual scope: runtime portability, not operator access. Suggested rename: "Runtime Portability" or "Agent Runtime Agnosticism."

SPIKE-059 (Agent Runtime I/O Compatibility) stays under VISION-003 — it is about which runtimes swain can run on, not about how the operator reaches them. VISION-006 consumes SPIKE-059's adapter interface as infrastructure.
