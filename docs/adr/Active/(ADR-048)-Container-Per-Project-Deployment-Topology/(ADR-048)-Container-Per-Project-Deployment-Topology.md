---
title: "Container-Per-Project Deployment Topology"
artifact: ADR-048
track: standing
status: Active
author: cristos
created: 2026-04-24
last-updated: 2026-04-24
supersedes: ADR-046
linked-artifacts:
  - ADR-049
  - DESIGN-033
  - VISION-006
  - INITIATIVE-018
  - SPIKE-074
depends-on-artifacts:
  - SPIKE-074
evidence-pool: ""
---

# Container-Per-Project Deployment Topology

## Context

ADR-046 decided on a per-host topology: one watchdog manages multiple project bridges as subprocesses, sharing a single opencode serve instance. After implementation and a production incident (115 zombie chat-adapter processes, runaway CPU from misinvoked processes, no cascade termination), the per-host model has three structural problems:

1. **Filesystem isolation is impossible.** A shared opencode serve process has host-level filesystem access. Any session in project A can read project B's source — violating the project isolation requirement (no session should touch anything outside its project folder).
2. **Process management fights Docker.** The watchdog reconciles bridge subprocesses, but Docker's `restart: unless-stopped` already provides process supervision. Two layers of lifecycle management creates the exact zombie processes we saw.
3. **Session inspection requires per-project access anyway.** The original rationale for a shared opencode serve (sessions in one place, inspectable) conflicts with isolation — and opencode's API uses root-level paths (`/session`, `/event`), making subpath routing impossible. Hostname-based routing through a reverse proxy is required.

SPIKE-074 confirmed that the NDJSON subprocess plugin model (protocol.py + plugin_process.py) is a strength — it enables multi-engine support and community adapters in any language. This decision preserves that model while changing the deployment topology.

## Decision

Each project runs in its own Docker container. Inside each container, the ProjectBridge microkernel (ADR-046's subprocess topology) is preserved — chat adapter and runtime adapters remain NDJSON-over-stdio subprocesses. What changes is the outer deployment boundary.

```
Host
  ├── Caddy container (reverse proxy, auth)
  │     Listens :443, routes by Host header
  │     swain.localhost    → swain container :4098
  │     other.localhost    → other container :4098
  │
  ├── swain container
  │     ├── opencode serve (port 4098, filesystem-isolated)
  │     ├── ProjectBridge microkernel
  │     │     ├── ChatAdapter subprocess (Zulip, NDJSON over stdio)
  │     │     └── RuntimeAdapter subprocess per session (NDJSON over stdio)
  │     └── WorktreeScanner (async, in-process)
  │     Volume: /path/to/project (read-write, isolated)
  │
  └── other container (same shape, different project)
```

Key properties:

- **One container per project.** Adding a project = adding a compose service. No shared state between containers.
- **Per-project opencode serve.** Each container owns its own opencode serve on port 4098. Sessions cannot escape the project filesystem. Port 4098 avoids conflict with local dev (port 4095/4096).
- **Caddy as reverse proxy and auth gateway.** Caddy routes by hostname (`swain.localhost`, `other.localhost`) and handles basic auth with header injection (workaround for opencode `attach` auth bug). Caddy auto-discovers project containers via Docker labels.
- **Subprocess model preserved inside containers.** NDJSON-over-stdio adapters remain. First-party adapters (Zulip, opencode server) are still subprocesses; third-party adapters can use the same contract. This is the extensibility point SPIKE-074 identified.
- **Docker provides lifecycle management.** `restart: unless-stopped` replaces the watchdog's reconciliation loop. Containers are the isolation boundary; no second layer of process supervision.
- **Local dev works without Docker.** The bridge process can run natively on macOS for development. One project, no routing problem. Production uses containers for isolation.
- **No watchdog process in container deployment.** The container entrypoint is the bridge process itself. Docker restart replaces reconciliation. A lightweight self-health-check replaces the watchdog's health probes.

## Alternatives Considered

- **Shared opencode serve per host (ADR-046 current).** Violates filesystem isolation. Sessions in project A can read project B's files. Rejected: isolation is a hard requirement.
- **Shared serve + filesystem sandboxing (chroot, seccomp).** opencode serve doesn't support chroot per session. Adding OS-level sandboxing around a shared process is complex and fragile. Rejected: containers give us this for free.
- **In-process adapters only (no subprocesses).** SPIKE-074 evaluated this and concluded that the NDJSON-over-stdio contract is a strength — it enables community adapters in any language. Rejected: loses the extensibility point.
- **One watchdog per host, containers for isolation.** The watchdog manages containers instead of processes. Rejected: Docker Compose already does this. Adding a watchdog on top duplicates lifecycle management.

## Consequences

- Project isolation is enforced by the kernel (container filesystem boundaries). No session can see another project's files.
- Caddy provides a single URL space for inspection: `opencode attach http://swain.localhost` for local, `opencode attach https://swain.tail-xxxx.ts.net` for remote via Tailscale.
- The watchdog process is eliminated in container deployment. Its responsibilities (lifecycle, credential resolution) move to Docker Compose and the entrypoint script.
- Adding a project is a compose service addition — no code changes.
- Port 4098 inside containers avoids conflict with local dev at 4095/4096.
- The bridge's subprocess management (PluginProcess) is retained for adapter isolation within a container. Process groups (`os.setpgrp` + `os.killpg`) are added for cascade termination if the bridge process crashes.
- On container crash, Docker restarts the whole container. No orphan processes possible.
- Remote access requires Tailscale on the host (one node) with Caddy listening on the Tailscale interface. Containers are on a Docker bridge network and are not directly reachable.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-24 | -- | Supersedes ADR-046. Container deployment model decided after production incident and SPIKE-074 analysis. |