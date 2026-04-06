# Process Supervision Patterns — Synthesis

Research into daemon management and process supervision across macOS (launchd), Linux (systemd), Docker, and user-space supervisors. The driving question: how should the swain host bridge stay alive reliably without manual babysitting, while managing project bridge children?

## Key Findings

### Keeping a daemon alive is simple on both macOS and Linux.

On macOS, a LaunchAgent plist with `KeepAlive: true` and `RunAtLoad: true` handles automatic start and restart. Place the plist in `~/Library/LaunchAgents/` for user-scoped daemons. launchd restarts the process after any exit, throttled by `ThrottleInterval` (default 10s). Conditional KeepAlive (e.g., `NetworkState`, `PathState`, `SuccessfulExit`) adds nuance without complexity. [apple-creating-launchd-jobs, launchd-info-tutorial]

On Linux, a systemd unit with `Restart=on-failure` and `RestartSec=1s` does the same job. For critical daemons that must never stay down, use `Restart=always` with `StartLimitIntervalSec=0` to disable the crash-burst limit. Drop-in overrides let you apply restart policies without touching vendor unit files. [systemd-indefinite-restarts, systemd-auto-restart-freshman]

Both approaches are declarative, require no code changes in the daemon, and survive reboots.

### A supervisor that spawns children needs explicit signal cascading.

SIGTERM does not automatically cascade to all descendants. The parent must trap SIGTERM, forward it to children, wait for them to exit, then exit itself. Three patterns work:

1. **Kill by job list**: `kill -TERM $(jobs -p)` then `wait`.
2. **Process group signaling**: `kill -TERM -$$` targets the whole group.
3. **File-based IPC**: Children poll a state file, parent sets a shutdown flag. [child-process-graceful-shutdown]

For the host bridge supervising project bridges, pattern 1 (kill by PID list) is the simplest. The host bridge tracks project bridge PIDs and sends SIGTERM to each on shutdown.

### Upgrading a supervisor without killing children is the hardest problem.

On systemd, the default behavior kills the entire cgroup on service restart — children die with the parent. Three workarounds exist:

- **systemd-run --scope**: Launch children as separate systemd scopes. They survive parent restart and remain tracked.
- **KillMode=process**: Only kill the main process. Children survive but become untracked orphans.
- **setsid**: Unreliable under cgroup management. [systemd-restart-without-killing-children]

On macOS, `AbandonProcessGroup: true` in the plist prevents SIGTERM from cascading to children. Children survive parent termination. [apple-creating-launchd-jobs, launchd-info-tutorial]

For the host bridge, the recommended approach is: launch project bridges as independent processes (not direct children), track them by PID file or pidfile convention, and use `AbandonProcessGroup` (macOS) or `KillMode=process` (Linux) in the init system configuration.

### Logging strategy: one file per child, supervisor gets its own.

supervisord demonstrates the pattern well: each child process gets its own stdout and stderr log file with independent rotation. The supervisor logs to a separate activity log. This avoids interleaving and makes per-bridge debugging trivial. [supervisord-logging]

PM2 follows the same model: logs centralized in `~/.pm2/logs/` with per-process files. [pm2-single-page-docs]

For the host bridge: write supervisor logs to one file, each project bridge to `<project>.stdout.log` and `<project>.stderr.log`. Use size-based rotation (e.g., 10MB, 5 backups).

### User-space process managers add value but also dependencies.

PM2 handles restart, logging, startup scripts, and cluster mode. It supports Python and shell scripts via `--interpreter`. But it adds Node.js as a dependency and is oriented toward web services. [pm2-single-page-docs]

supervisord is Python-based, handles per-child logging well, and supports process pools. But it runs indefinitely (no graceful exit mode), which makes it less suitable for containers. [supervisord-logging]

s6 is the lightweight champion: no heap allocation, event-driven, PID 1 capable. But it targets Linux/embedded systems and has a learning curve. [s6-why-another-suite]

For the host bridge's "low maintenance budget" requirement, the OS-native init system (launchd on macOS, systemd on Linux) is the right choice. Adding supervisord or PM2 introduces a dependency for marginal benefit when the host bridge already manages its own children.

## Points of Agreement

- Declarative restart policies (launchd KeepAlive, systemd Restart=always) are the standard approach for daemon reliability.
- SIGTERM is the universal graceful shutdown signal. Every daemon should handle it.
- Per-child logging with rotation is the consensus pattern for supervisor + N children.
- The supervisor should not daemonize itself — let the init system handle backgrounding.

## Points of Disagreement

- **User-space vs OS-native supervision**: PM2 and supervisord offer richer features (cluster mode, web UI, process pools), but at the cost of an extra dependency. s6 advocates argue that the init system should stay minimal and user-space tools should layer on top.
- **Child tracking on upgrade**: systemd-run --scope vs KillMode=process. The former is cleaner (children remain tracked) but requires the daemon to use systemd APIs when spawning children. The latter is simpler but creates orphans.

## Gaps

- **Docker restart policies and health checks**: Docker's `restart: unless-stopped` handles container-level restarts, but Docker does not auto-restart unhealthy containers. Health checks mark containers but require an external orchestrator (Swarm, Kubernetes) to act on them. This matters if the host bridge ever runs in a container.
- **Cross-platform abstraction**: No source covers a clean way to write one daemon that works with both launchd and systemd. The host bridge will need platform-specific init configuration (plist for macOS, unit file for Linux).
- **runit**: Not covered in depth. runit offers a middle ground between s6 and supervisord but is less common on macOS.
- **Watchdog patterns**: systemd's `WatchdogSec` can detect hung (but alive) processes. No macOS equivalent was found. Relevant if the host bridge hangs without crashing.

## Recommendations for the Host Bridge

1. **Init integration**: Ship a LaunchAgent plist for macOS and a systemd user unit for Linux. Use `KeepAlive: true` / `Restart=always` for automatic restart.
2. **Child management**: Track project bridge PIDs in a state file. Send SIGTERM to each on shutdown. Use `AbandonProcessGroup` (macOS) or `KillMode=process` (Linux) so children survive supervisor upgrades.
3. **Logging**: Supervisor log to `~/.swain/logs/host-bridge.log`. Each project bridge to `~/.swain/logs/<project>.log`. Size-based rotation (10MB, 5 backups).
4. **Upgrades**: On restart, the new host bridge process reads the PID state file and adopts existing project bridges rather than restarting them.
5. **No extra dependencies**: Skip PM2/supervisord. The host bridge is its own supervisor using OS-native init for restart.
