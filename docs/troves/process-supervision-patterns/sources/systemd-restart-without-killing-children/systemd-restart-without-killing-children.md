---
source-id: systemd-restart-without-killing-children
type: forum
url: "https://bbs.archlinux.org/viewtopic.php?id=212380"
title: "Restart a systemd service without killing its children — Arch Linux Forums"
fetched: 2026-04-06T17:02:34Z
---

# Restart a systemd Service Without Killing Its Children

Forum discussion about techniques for upgrading or restarting a daemon while preserving its child processes.

## Problem Statement

When you restart a systemd service, systemd terminates the entire cgroup, including all child processes. This is a problem for supervisor daemons that spawn long-lived children.

## Solutions Discussed

### 1. setsid Approach

Create a new session ID for spawned processes using `setsid`. This detaches children from the parent's process group:

```bash
setsid child-process &
```

Caveat: systemd's cgroup management may still kill children despite `setsid`, depending on the unit's `KillMode` configuration.

### 2. systemd-run Method (Recommended)

Use `systemd-run` when launching child processes. This reparents children to the systemd user instance and tracks them as separate service units:

```bash
systemd-run --user --scope child-process
```

Each child becomes its own systemd scope, independent of the parent service. When the parent restarts, children survive because they are not in the parent's cgroup.

### 3. KillMode Configuration

Set `KillMode=process` in the unit file to only kill the main process, not the entire cgroup:

```ini
[Service]
KillMode=process
```

This lets children survive when the parent is stopped or restarted. But children are no longer tracked by systemd after the parent exits.

### 4. disown Workaround

Shell-level `disown` removes a child from the shell's job table but does not affect cgroup membership. Less robust than systemd-run.

## systemd daemon-reexec

For upgrading systemd itself: `systemctl daemon-reexec` replaces the running systemd binary while preserving all unit states. All services continue undisturbed. This is not directly applicable to user daemons but shows the pattern: replace the supervisor binary while keeping managed state intact.

## Key Insight

The right approach depends on whether you want children tracked:

- **systemd-run**: Children survive parent restart AND remain tracked by systemd.
- **KillMode=process**: Children survive but become untracked orphans.
- **setsid**: Unreliable under cgroup management.
