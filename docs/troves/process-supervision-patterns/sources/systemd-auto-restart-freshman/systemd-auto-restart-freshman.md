---
source-id: systemd-auto-restart-freshman
type: web
url: "https://freshman.tech/snippets/linux/auto-restart-systemd-service/"
title: "How to automatically restart Linux services with systemd — Freshman"
fetched: 2026-04-06T17:02:22Z
---

# How to Automatically Restart Linux Services with systemd

Practical guide to configuring systemd restart policies.

## Restart Directive Options

The `Restart` option determines when a service restarts after exiting:

- **always**: Restart regardless of exit code or signal.
- **on-failure**: Restart only on non-zero exit code or unclean signal.
- **on-abnormal**: Restart on signal, timeout, or watchdog.
- **on-watchdog**: Restart only on watchdog timeout.
- **on-abort**: Restart only on unclean signal.
- **no**: Never restart (default).

For most daemons, `on-failure` is the best default. Use `always` only for critical services that must never stay down.

## Complete Unit File Example

```ini
[Unit]
Description=Your Daemon Name
StartLimitIntervalSec=300
StartLimitBurst=5

[Service]
ExecStart=/path/to/executable
Restart=on-failure
RestartSec=1s

[Install]
WantedBy=multi-user.target
```

This allows the service to restart up to 5 times within 300 seconds. If it crashes more than 5 times in that window, systemd stops trying.

## Key Configuration

- **RestartSec**: Delay before restart attempt. Default is 100ms. Override to 1s or higher to avoid rapid-crash loops.
- **StartLimitIntervalSec**: Time window for counting restarts.
- **StartLimitBurst**: Maximum restarts within the interval.

## Applying Changes

After modifying the unit file, run `sudo systemctl daemon-reload` to activate changes.
