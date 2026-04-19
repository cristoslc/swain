---
title: "OpenCode Serve Integration"
artifact: EPIC-085
track: container
status: Active
author: cristos
created: 2026-04-18
last-updated: 2026-04-18
parent-vision: VISION-006
parent-initiative: INITIATIVE-018
priority-weight: high
success-criteria:
  - OpenCodeServerAdapter rewritten as a subprocess plugin speaking NDJSON over stdio.
  - Adapter connects to shared opencode serve instance with HTTP basic auth.
  - Cancel support via `POST /session/{id}/abort`.
  - Approval support via `POST /session/{id}/permissions/{permissionID}`.
  - Discovery finds running opencode instances, starts new ones when needed.
  - Bridge-started instances track session metadata for later export.
  - Auth credentials are per-port — no spraying at unknown servers.
depends-on-artifacts:
  - ADR-038
  - ADR-047
  - EPIC-073
addresses: []
evidence-pool: ""
---

# OpenCode Serve Integration

## Goal / Objective

Make the OpenCode runtime adapter a true subprocess plugin and integrate with opencode serve's shared instance model. The adapter must handle authentication, session abort, permission approval, and discovery of running instances.

## Desired Outcomes

The bridge coexists with the operator's TUI usage. If opencode serve is already running, the bridge attaches to it. If not, the watchdog starts one. Sessions started via the bridge use the same server the operator uses locally. Cancel and approval work from Zulip without a terminal.

## Scope Boundaries

**In scope:**
- OpenCodeServerAdapter as subprocess plugin (NDJSON over stdio).
- HTTP basic auth on all requests.
- Session abort via `/session/{id}/abort`.
- Permission response via `/session/{id}/permissions/{pid}`.
- Session metadata export to `.swain/swain-helm/sessions/opencode/`.
- Discovery and instance tracking (collaboration with watchdog).

**Out of scope:**
- Watchdog reconciliation loop (EPIC-084).
- Other runtime adapters — Claude Code (EPIC-073), Tmux (EPIC-073).
- Chat adapter (EPIC-072).
- Full session export pipeline (v2).

## Child Specs

- SPEC-321: OpenCode Serve Discovery and Auth

## Key Dependencies

- ADR-038 (Microkernel Plugin Architecture) — defines the subprocess plugin contract.
- ADR-047 (swain-helm Watchdog Architecture) — defines per-port auth and discovery.
- EPIC-073 (Runtime Plugin System) — parent epic for runtime adapters.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-18 | -- | Extracted from EPIC-073 to focus on opencode-specific concerns. |