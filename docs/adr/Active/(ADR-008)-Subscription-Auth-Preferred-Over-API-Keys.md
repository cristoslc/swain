---
title: "Subscription Auth Preferred Over API Keys"
artifact: ADR-008
track: standing
status: Active
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
linked-artifacts:
  - DESIGN-005
  - INITIATIVE-013
  - SPEC-092
  - SPIKE-032
  - SPIKE-034
  - VISION-002
depends-on-artifacts: []
evidence-pool: ""
---

# Subscription Auth Preferred Over API Keys

## Context

swain-box launches AI coding agents in Docker containers and Docker Sandboxes. Each runtime (Claude, Codex, Copilot, Gemini) supports multiple authentication methods:

- **Subscription auth (OAuth):** Operator logs in via a browser flow inside the container. Credentials persist in the container. Flat-rate billing (Max/Pro subscription). No separate API credits needed.
- **API key auth:** Operator provides an API key as an environment variable. Pay-per-token billing. Requires a separate API billing account on top of any subscription.

During VISION-002 development, the initial implementation assumed API key auth was the primary path — SPIKE-032 found Docker Sandboxes' MITM proxy breaks OAuth for Claude, and the code was written to gate on `ANTHROPIC_API_KEY` availability. This led to an API-key-first design that didn't match the operator's actual usage (Max subscription, no API credits).

SPIKE-034 then proved that Docker's sandbox template images work in regular `docker run` containers where OAuth functions correctly (no MITM proxy). This opened the subscription auth path for container mode.

## Decision

swain-box defaults to subscription auth (interactive login inside the container) as the primary authentication method. API key auth is the secondary option, offered as a fallback.

Specifically:
1. The first-run auth menu defaults to "Subscription (login inside container)" — option 1
2. The isolation menu defaults to "Docker Container" (option 2) when the selected runtime has known OAuth issues with Docker Sandboxes (e.g., Claude), because container mode supports subscription login while microVM mode does not
3. API key auth is offered as option 2 in the auth menu for operators who prefer per-token billing or need non-interactive setup

## Alternatives Considered

### API key as default

The approach we started with. Advantages: simpler (just pass `-e ANTHROPIC_API_KEY`), works in non-interactive environments, no browser flow needed. Rejected because: requires a separate billing account with credits, operators with Max subscriptions get "Credit balance too low" errors, and it assumes the operator has API credits — which most personal/Max users don't.

### Mount host credential files into container

Find where each runtime stores OAuth tokens on the host filesystem and mount those paths read-only into the container. Rejected because: credential storage locations vary by runtime and OS, some runtimes store tokens in the system keychain (macOS Keychain, GNOME Keyring) rather than files, and mounting credential files creates a maintenance burden as runtimes change their storage format.

### Skip auth entirely (defer to runtime)

Don't handle auth in swain-box at all — let the runtime prompt for login when it needs credentials. Rejected because: some runtimes (Codex) require login before the TUI starts, meaning the user would get a cryptic failure instead of a guided auth flow. swain-box should handle the known auth requirements rather than letting users hit runtime-specific error messages.

## Consequences

**Positive:**
- Operators with subscriptions (the common case for personal use) get a working launcher without needing API credits
- The default path matches the billing model most operators already have
- Login credentials persist in the container — subsequent runs skip auth entirely
- swain-box handles the auth UX centrally instead of each runtime failing differently

**Accepted downsides:**
- First run requires an interactive session (browser-based OAuth flow)
- Non-interactive environments (CI, dispatched agents) must use API key auth explicitly via `--isolation=microvm` or the API key option in the auth menu
- Each runtime's login command must be maintained in swain-box's known-runtimes table

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | — | Decision adopted during SPEC-092 brainstorming; prompted by SPIKE-032/034 findings |
