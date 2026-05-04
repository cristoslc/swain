---
title: "Provisioning (swain-stage)"
artifact: EPIC-074
track: container
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-18
parent-vision: VISION-006
parent-initiative: INITIATIVE-018
priority-weight: medium
success-criteria:
  - `swain-helm host provision` writes ~/.config/swain-helm/helm.config.json with op:// credential references. First-run <5 minutes.
  - `/swain-stage` on self-hosted provisions a VPS, deploys the chat server, and connects bridges.
  - Adding a second project to an existing chat service creates a room and project bridge without re-provisioning.
  - Isolated mode provisions a separate chat service instance for security-sensitive projects.
depends-on-artifacts:
  - EPIC-084
  - EPIC-072
  - ADR-037
addresses: []
evidence-pool: ""
---

# Provisioning (swain-stage)

## Goal / Objective

One-command setup for the swain-helm stack. `swain-helm host provision` registers the Zulip bot, creates streams, and writes helm.config.json.

## Desired Outcomes

The first-run experience is under 5 minutes. Subsequent projects on the same chat service take under 1 minute. The operator never manually edits config files or runs multiple setup commands.

## Scope Boundaries

**In scope:**
- Hosted path: Zulip Cloud bot registration via API, stream creation, bridge config generation, daemon start.
- Self-hosted path: VPS provisioning (via Commodore or manual), chat server deploy, DNS, TLS, bridge config, daemon start.
- Multi-project: add project room to existing chat service.
- Isolated mode: separate chat service instance/workspace.
- Config file generation with security defaults (chmod 600, absolute paths).

**Out of scope:**
- The bridge daemons (EPIC-071, EPIC-084).
- The chat and runtime plugins (EPIC-072, EPIC-073).
- v2 tunnel/ingress provisioning for the web pipe.

## Child Specs

_To be created during implementation planning._

## Key Dependencies

- EPIC-084 (Watchdog) — provisioning starts the daemon.
- EPIC-072 (Chat Plugin System) — provisioning registers the bot.
- ADR-037 (Chat Platform) — determines which provisioning path is default.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | -- | Created from VISION-006 decomposition. |
| Active | 2026-04-18 | -- | Updated for swain-helm architecture. Replaced EPIC-070 with EPIC-084. |
