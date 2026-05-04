---
title: "Docker Lifecycle and Process Hygiene"
artifact: ADR-049
track: standing
status: Active
author: cristos
created: 2026-04-24
last-updated: 2026-04-24
supersedes: ADR-047
linked-artifacts:
  - ADR-048
  - DESIGN-033
  - VISION-006
  - INITIATIVE-018
  - SPIKE-074
depends-on-artifacts:
  - ADR-048
evidence-pool: ""
---

# Docker Lifecycle and Process Hygiene

## Context

ADR-047 defined a Python asyncio watchdog process that reconciles desired state on a 30-second loop, manages PID files, resolves 1Password credentials at startup, and restarts crashed bridges. After a production incident (115 zombie zulip_chat processes, a runaway `python3 docs` process at 99% CPU, no cascade termination when the watchdog died), the watchdog's process management model has shown structural problems:

1. **No cascade termination.** When the watchdog or bridge terminates, child subprocesses (zulip_chat, runtime adapters) become orphans. `asyncio.subprocess.Process.terminate()` only sends SIGTERM to the direct child — grandchildren survive and accumulate.
2. **No zombie cleanup on startup.** The watchdog's `_reconcile()` only checks PID files. Stale processes from previous runs that lost their PID files survive indefinitely.
3. **Two supervisory layers fight.** Docker restarts the container, the watchdog restarts bridges. When both are active, lifecycle management is duplicated.

Additionally, the container-per-project topology (ADR-048) changes what the watchdog does: credential resolution moves to the entrypoint, and Docker handles restarts. The watchdog's remaining purpose — starting the bridge and opencode serve — is now the entrypoint's job.

## Decision

The watchdog process is eliminated in container deployment. Its responsibilities move to three places:

### 1. Container entrypoint handles startup

The `entrypoint.sh` resolves 1Password references, writes resolved config, and starts the bridge process. If 1Password is unavailable, the entrypoint exits — Docker's `restart: unless-stopped` retries after a delay.

### 2. Bridge process starts opencode serve directly

The ProjectBridge starts opencode serve as a subprocess on container startup (port 4098). If opencode serve dies, the bridge detects it via health check and restarts it. If the bridge dies, Docker restarts the container — killing all descendants.

### 3. Process group hygiene prevents orphan leaks

All subprocess spawns use `os.setpgrp()` in `preexec_fn` to create a new process group. The bridge process is the process group leader. On SIGTERM (Docker stop), SIGTERM is delivered to the bridge, which propagates to the process group via `os.killpg()`. This ensures cascade termination — chat adapters, runtime adapters, and opencode serve all die with the container.

Additionally, on startup, the bridge scans for and kills any stale swain_helm processes from a previous container run (defensive measure against Docker restart policy leaving partial state).

### What the watchdog kept (for local dev)

The watchdog remains available for local development (running natively on macOS without Docker). In local-dev mode, it provides:
- 1Password credential resolution
- Bridge lifecycle management
- opencode serve discovery

In container deployment, the watchdog binary is not included. The entrypoint + bridge process + Docker restart policy replace it entirely.

## Alternatives Considered

- **Keep the watchdog inside containers.** Adds complexity without benefit. Docker already provides restart supervision. The watchdog's PID-file reconciliation is redundant inside a container. Rejected: two supervisory layers fighting was the root cause of the zombie incident.
- **Systemd/launchd inside containers.** Possible but heavyweight. A Python process that manages subprocesses via process groups is simpler and testable. Rejected: Docker restart + process groups is sufficient.
- **In-process adapters only (no subprocesses).** SPIKE-074 evaluated this and concluded the NDJSON-over-stdio contract is a strength for extensibility. Rejected: loses the adapter extensibility point while adding shared-fault-domain risk.
- **Watchdog as health-check sidecar.** A minimal watchdog that only does health checks and reports to Docker. Rejected: the bridge process can do its own health checks. Adding another process for this is unnecessary.

## Consequences

- The watchdog Python module (`watchdog.py`) remains in the codebase for local dev use. It is not invoked in container deployment.
- Zombie process accumulation is impossible inside a container. Container death kills the entire process group.
- Cascade termination on graceful shutdown requires `os.setpgrp()` + `os.killpg()`. This must be added to `PluginProcess.start()` and tested.
- Startup zombie cleanup (`kill_stale_processes()`) must be called at bridge entry as a defensive measure against Docker restart edge cases.
- Local dev workflow changes: `swain-helm host up` still works natively (macOS), but the watchdog must handle process group hygiene on macOS (where `os.setpgrp()` works but `os.killpg()` behavior differs slightly from Linux). This is the local-dev-only path — production runs in Docker.
- Caddy (the reverse proxy) is a separate compose service, not managed by the bridge. It auto-discovers project containers via Docker labels.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-24 | -- | Supersedes ADR-047. Container deployment eliminates the watchdog; process hygiene moves to process groups. |