---
title: "swain-helm Watchdog Architecture"
artifact: ADR-047
track: standing
status: Active
author: cristos
created: 2026-04-18
last-updated: 2026-04-18
linked-artifacts:
  - VISION-006
  - INITIATIVE-018
  - ADR-038
  - ADR-046
depends-on-artifacts:
  - ADR-046
evidence-pool: ""
---

# swain-helm Watchdog Architecture

## Context

The bridge needs a persistent process that ensures project bridges are running, reconnects to chat on failure, and manages opencode serve availability. The previous architecture used a host bridge kernel for this, but it conflated process management with event routing (ADR-046 removes the routing).

The watchdog must also handle credential resolution. The operator uses 1Password for Zulip and opencode serve credentials. References like `op://Private/Zulip Bot/api_key` require biometric unlock. The operator is only present at startup — credentials must be resolved once and cached for the process lifetime.

OpenCode serve may already be running (the operator uses the TUI), or it may need to be started. Auth credentials are per-port — it is unsafe to spray cached credentials at any server we discover.

Git worktrees are created dynamically by `swain-do` or manual `git worktree add`. The bridge must discover them after startup, not require pre-registration.

## Decision

The watchdog is a Python asyncio process that reconciles desired state against running processes on a 30-second loop. It is a process manager, not an event router.

### Credential resolution

- All `op://` references in config are resolved once at startup via `op read`.
- Resolved values are cached in process-locked memory. Never written to disk, never logged, never printed to stdout.
- Startup fails hard if 1Password is locked. The operator must be present for biometric unlock.
- Log output shows which 1Password items were fetched and success/failure, but never the credential contents.

### Per-port opencode auth

- The global config (`helm.config.json`) maps port numbers to auth credentials.
- Discovery only authenticates against ports with known credentials.
- No credential spraying: if a healthy server is found on an unconfigured port, it is noted but not used.
- If no usable instance is found, the watchdog starts `opencode serve` on the configured default port.

### Continuous worktree discovery

- Each project bridge polls `git worktree list --porcelain` every 15s.
- New worktrees get a topic named after their branch (e.g., `feature-x`).
- Removed worktrees result in session termination and cleanup.
- This is per-project-bridge, not per-watchdog. The watchdog does not manage worktrees.

### One session per worktree

- A project bridge holds exactly one opencode session per git worktree.
- Trunk always has a session (topic: `trunk`). Each worktree gets its own session.
- If a worktree's session dies, it is restarted. No second session is created for the same worktree.
- OpenCode may internally track multiple sessions, but swain-helm only tracks the active one per worktree.

### Desired state reconciliation

- Project configs live in `~/.config/swain-helm/projects/<name>.json`.
- The watchdog reads all configs on each loop iteration.
- For each project: if a bridge process is not running, start one. If crashed, restart it.
- PID files in `~/.config/swain-helm/run/bridges/` track running processes.
- Config removal triggers bridge shutdown on the next reconciliation.

## Alternatives Considered

- **Shell-based supervisor.** A bash script manages PID files and restarts. Simpler but poor async subprocess management, no credential caching, harder error recovery. Rejected: Python asyncio matches the existing codebase.
- **Host bridge as watchdog.** Keep the host bridge but remove routing. Rejected: this creates a hybrid component that does two things poorly. Process management and event routing are separate concerns.
- **No watchdog.** Operator starts each bridge manually. Rejected: the operator wants fire-and-forget. A bridge that stops when the terminal closes is not an untethered operator.
- **Systemd/launchd as supervisor.** Let the OS manage process lifecycle. Viable for production, but does not handle opencode discovery, credential resolution, or per-project bridge management. Deferred to v2.

## Consequences

- The watchdog is a single point of startup — if 1Password is locked, nothing starts. This is intentional: no credentials, no bridge.
- If the watchdog crashes, existing bridges and sessions continue running. They just stop being supervised until the watchdog restarts.
- Per-port auth means adding a new opencode serve instance requires a config change. This is intentional friction for security.
- The 15-second worktree poll means up to 15s delay before a new worktree gets a session. Acceptable: worktree creation is rare relative to session activity.
- The watchdog is a separate concern from project bridges. It can be replaced (e.g., with a systemd unit generator) without changing the bridge architecture.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-18 | -- | Decided during swain-helm architecture refactor. |