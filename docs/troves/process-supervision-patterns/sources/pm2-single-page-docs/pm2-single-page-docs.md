---
source-id: pm2-single-page-docs
type: web
url: "https://pm2.keymetrics.io/docs/usage/pm2-doc-single-page/"
title: "PM2 — Single Page Documentation"
fetched: 2026-04-06T17:02:25Z
---

# PM2 Process Manager

PM2 is a daemon process manager for Node.js (and other languages) with a built-in load balancer, log management, startup scripts, and graceful shutdown.

## Core Features

- Start, stop, restart, delete managed processes.
- Automatic restart on crash.
- Cluster mode for Node.js (multi-core distribution).
- Ecosystem config files for multi-app management.
- Startup script generation for boot persistence.
- Centralized logging with rotation.

## Startup Scripts and Persistence

`pm2 startup` generates init system configuration (supports systemd, upstart, launchd, and others). After starting apps, `pm2 save` preserves the process list for automatic respawn on reboot. This makes PM2 integrate with the host OS init system for daemon survival.

## Logging

PM2 centralizes logs in `~/.pm2/logs/` with real-time streaming via `pm2 logs`. Features:

- Separate stdout and stderr log files per process.
- Custom log formatting and timestamp prefixes.
- Rotation via pm2-logrotate module.
- JSON output mode.
- Flush all logs with `pm2 flush`.

## Ecosystem Files

Configuration files (`ecosystem.config.js`) manage multiple apps with predefined options. They specify environment variables, restart behaviors, logging paths, and execution modes.

```javascript
module.exports = {
  apps: [{
    name: "app",
    script: "./app.js",
    instances: "max",
    exec_mode: "cluster",
    env: { NODE_ENV: "production" }
  }]
};
```

## Graceful Shutdown

Apps intercept SIGINT to close connections and finish work before exit. PM2 waits a configurable duration (default 1600ms) before sending SIGKILL.

## Restart Strategies

- File-watching with `--watch`.
- Memory thresholds via `--max-memory-restart`.
- Cron-based scheduling.
- Exponential backoff delays.
- Custom restart delays.
- Skip auto-restart on specific exit codes.

## Non-Node Support

PM2 manages Python scripts, bash commands, and binary executables through the `interpreter` config option:

```bash
pm2 start script.py --interpreter python3
```

## Relevance to Daemon Supervision

PM2 is a user-space process manager that wraps OS-level init integration. It handles the supervisor-children pattern well: one PM2 daemon manages N app processes, each with its own logging, restart policy, and resource limits. However, PM2 is oriented toward web services (cluster mode, load balancing) and adds Node.js as a dependency.
