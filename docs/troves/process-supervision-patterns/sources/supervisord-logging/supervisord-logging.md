---
source-id: supervisord-logging
type: web
url: "https://supervisord.org/logging.html"
title: "Logging — Supervisor 4.3.0 documentation"
fetched: 2026-04-06T17:02:24Z
---

# Supervisord Logging

Official documentation for supervisord's logging system, covering both the activity log and child process logs.

## Activity Log

The activity log records supervisord's own operational status and subprocess state changes.

- Configured via `logfile` in the `[supervisord]` section.
- Default: `$CWD/supervisord.log`.
- Can route to syslog by setting the value to `syslog`.

## Log Levels (Highest to Lowest)

| Level | Code | Description |
|-------|------|-------------|
| Critical | CRIT | System state changes needing immediate attention. |
| Error | ERRO | Potentially recoverable errors. |
| Warning | WARN | Anomalous but non-error conditions. |
| Info | INFO | Standard operational messages (default). |
| Debug | DEBG | Process configuration and behavior diagnostics. |
| Trace | TRAC | Plugin debugging and HTTP/RPC details. |
| Blather | BLAT | Internal supervisor debugging. |

## Log Rotation

Activity logs rotate based on two parameters:

- **logfile_maxbytes**: Maximum size before rotation.
- **logfile_backups**: Number of backup files to keep.

When the log reaches `logfile_maxbytes`, it gets renamed with a numeric suffix (e.g., `supervisord.log.1`). Setting `logfile_maxbytes=0` disables rotation.

## Child Process Logging

supervisord captures subprocess stdout and stderr to files. Key configuration:

- **childlogdir**: Directory for automatic log file storage.
- **redirect_stderr**: Redirects stderr to stdout.
- **stdout_logfile** / **stderr_logfile**: Explicit file paths.
- **stdout_logfile_maxbytes** / **stderr_logfile_maxbytes**: Size-based rotation.
- **stdout_logfile_backups** / **stderr_logfile_backups**: Backup retention count.
- **nocleanup**: Preserves log files on process exit.
- **stdout_capture_maxbytes** / **stderr_capture_maxbytes**: In-memory buffer limits.

By default, child logs go to temporary files in `AUTO` mode under `childlogdir`.

## Capture Mode

A structured communication feature. Processes emit tokens between `<!--XSUPERVISOR:BEGIN-->` and `<!--XSUPERVISOR:END-->` markers. Data between these markers triggers `PROCESS_COMMUNICATION` events. Event listeners can intercept these for data-driven automation.

## Key Takeaway for Multi-Child Logging

Each child process gets its own stdout and stderr log files. supervisord handles per-process rotation and retention independently. This scales well for a supervisor managing N children, since each child's output is isolated in its own log file with its own rotation policy.
