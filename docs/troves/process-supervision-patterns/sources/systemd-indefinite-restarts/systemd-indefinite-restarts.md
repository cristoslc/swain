---
source-id: systemd-indefinite-restarts
type: web
url: "https://michael.stapelberg.ch/posts/2024-01-17-systemd-indefinite-service-restarts/"
title: "systemd: enable indefinite service restarts — Michael Stapelberg"
fetched: 2026-04-06T17:02:21Z
---

# systemd: Enable Indefinite Service Restarts

Michael Stapelberg explains how to override systemd's default restart limits so that a service restarts forever after a crash.

## Default Settings (systemd 255)

- `DefaultRestartSec=100ms` — delay between restart attempts.
- `DefaultStartLimitIntervalSec=10s` — time window for burst limits.
- `DefaultStartLimitBurst=5` — maximum restarts allowed within the interval.

With defaults, if a service crashes more than 5 times in 10 seconds, systemd gives up and stops restarting it.

## Enabling Indefinite Restarts

### Drop-in Configuration Method

Create a reusable drop-in at `/etc/systemd/system/restart-drop-in.conf`:

```ini
[Unit]
StartLimitIntervalSec=0

[Service]
Restart=always
RestartSec=1s
```

Apply to individual services by symlinking into their `.d/` directory. This avoids editing vendor unit files.

### System-wide Defaults

Modify `/etc/systemd/system.conf.d/restartdefaults.conf`:

```ini
[Manager]
DefaultRestartSec=1s
DefaultStartLimitIntervalSec=0
```

## Key Parameters

- **StartLimitIntervalSec=0**: Disables the time-window restriction. systemd will never give up restarting.
- **Restart=always**: Restart regardless of exit code.
- **RestartSec**: Delay between consecutive restart attempts. Set to at least 1s to avoid CPU spin on rapid-crash loops.

## Rationale

The defaults protect against resource exhaustion from crash loops. Setting `StartLimitIntervalSec=0` with an appropriate `RestartSec` trades that protection for automatic self-healing. This is the right tradeoff for server environments where the service must recover without human intervention.
