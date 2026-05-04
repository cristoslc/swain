---
source-id: apple-creating-launchd-jobs
type: web
url: "https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html"
title: "Creating Launch Daemons and Agents — Apple Developer Documentation"
fetched: 2026-04-06T17:02:19Z
---

# Creating Launch Daemons and Agents

Apple's official guide to creating launchd-managed daemons and agents on macOS.

## Overview

`launchd` is the preferred method for launching system daemons and per-user background processes (agents) on macOS. It provides on-demand launching, better performance, and centralized daemon management.

- **Daemon**: System-level service running at boot.
- **Agent**: Per-user service running only when user is logged in.

## Directory Locations

### LaunchDaemons (system-wide)

| Path | Purpose |
|------|---------|
| `/System/Library/LaunchDaemons/` | Apple-provided. |
| `/Library/LaunchDaemons/` | Third-party, installed globally. |

Requirements: Owned by root, no group/world write permissions (600 or 400).

### LaunchAgents (per-user)

| Path | Purpose |
|------|---------|
| `/System/Library/LaunchAgents/` | Apple-provided. |
| `/Library/LaunchAgents/` | Global user agents. |
| `~/Library/LaunchAgents/` | Individual user agents. |

Requirements: Owned by target user, no group/world write permissions (600 or 400).

## Essential plist Keys

### Required

- **Label**: Unique identifier for daemon (reverse-domain format recommended).
- **ProgramArguments**: Array containing program path and arguments.

### Common Keys

| Key | Description | Default |
|-----|-------------|---------|
| `KeepAlive` | If true, daemon always runs; if false, launches on-demand. | false |
| `RunAtLoad` | Launches job immediately upon loading. | false |
| `StandardOutPath` | Redirect stdout to file. | N/A |
| `StandardErrorPath` | Redirect stderr to file. | N/A |
| `WorkingDirectory` | Set daemon's working directory. | N/A |
| `UserName` | User to run daemon as. | N/A |
| `Debug` | Enable launchd debug logging. | false |

## Scheduling and Triggering

- **StartInterval**: Run job at fixed intervals (seconds).
- **StartCalendarInterval**: Run at specific calendar times. Omitted keys act as wildcards.
- **WatchPaths**: Launch job when monitored paths change.
- **QueueDirectories**: Launch and keep running while directories contain files.
- **Sockets**: Monitor well-known ports for incoming connections.

## KeepAlive Conditional Options

- **SuccessfulExit**: Restart based on exit status. True = restart until failure; false = restart until success.
- **Crashed**: Restart after crashes.
- **NetworkState**: True = launch when network available; false = launch when offline.
- **PathState**: Maintain job while a path exists (true) or does not exist (false).
- **OtherJobEnabled**: Start when a referenced job is unloaded.

## Complete Example (Always-Running Daemon)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.example.hello</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/libexec/hello</string>
        <string>world</string>
    </array>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

## Critical Requirements for launchd Daemons

Do NOT daemonize (no fork/exec, no `daemon()` call). If the process forks and exits, launchd thinks it crashed and may suspend relaunching.

Do NOT shut down within 10 seconds of launch. launchd may interpret this as a crash.

Provide a SIGTERM handler for graceful shutdown. On system shutdown or user logout, launchd sends SIGTERM to all managed processes.

## Recommended Behaviors

- Wait for full initialization before processing requests.
- Register sockets and file descriptors in the plist.
- Check in with launchd during initialization.
- Let launchd handle: user/group IDs, working directory, chroot, stdio redirection, resource limits, and priority.

## Shutdown

On system shutdown, launchd sends SIGTERM to all managed daemons. On user logout, launchd sends SIGTERM to all managed agents. If a daemon does not exit after SIGTERM, launchd sends SIGKILL after `ExitTimeOut` seconds (default: 20).

## AbandonProcessGroup

When set to true, prevents SIGTERM propagation to child processes, letting children survive parent termination. This is relevant for supervisor daemons that manage child processes independently.
