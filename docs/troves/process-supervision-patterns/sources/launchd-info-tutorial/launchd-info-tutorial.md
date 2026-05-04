---
source-id: launchd-info-tutorial
type: web
url: "https://www.launchd.info/"
title: "A launchd Tutorial — launchd.info"
fetched: 2026-04-06T17:02:20Z
---

# A launchd Tutorial

Comprehensive community reference for launchd configuration on macOS. Covers all plist keys with examples.

## Job Definition Storage

Jobs are stored as XML property lists (.plist files):

- **User Agents**: `~/Library/LaunchAgents`.
- **Global Agents**: `/Library/LaunchAgents`.
- **Global Daemons**: `/Library/LaunchDaemons`.
- **System Agents**: `/System/Library/LaunchAgents`.
- **System Daemons**: `/System/Library/LaunchDaemons`.

Agents run on behalf of the logged-in user and have GUI access. Daemons run as root or a specified user and lack GUI access.

## KeepAlive Conditional Dictionary

Beyond the simple boolean, KeepAlive accepts a dictionary of conditions:

- **SuccessfulExit** (bool): When true, restarts until the job fails. When false, restarts until the job succeeds.
- **Crashed** (bool): True = restart after crash. False = restart unless crashed.
- **NetworkState** (bool): True = launch when network available. False = launch when offline.
- **PathState** (dict): Keys are file paths, values are booleans. Maintains the job while a path exists (true) or does not exist (false).
- **OtherJobEnabled** (dict): Keys are job labels, values are booleans. Starts when a referenced job is unloaded.
- **AfterInitialDemand** (bool): Delays applying run conditions until the job is started manually.

## ThrottleInterval

Delay in seconds between job invocations. Useful with KeepAlive for throttling restarts. Default is 10 seconds. If a job exits and restarts faster than ThrottleInterval, launchd delays the restart.

## ExitTimeOut

Seconds to wait after SIGTERM before sending SIGKILL. Default is 20 seconds. Critical for graceful shutdown.

## Resource Limits

SoftResourceLimits and HardResourceLimits constrain CPU, file size, file count, core dumps, data memory, memory locks, process count, resident set size, and stack.

## ProcessType

Hints to the system about the kind of work the job performs. Values include `Background`, `Standard`, `Adaptive`, `Interactive`. Affects scheduling priority.

## LowPriorityIO

When true, reduces IO priority. Good for background maintenance tasks.

## AbandonProcessGroup

When true, prevents SIGTERM propagation to child processes on job termination. Children survive the parent's death.

## Environment Variables

EnvironmentVariables sets env vars as key-value pairs. Shell globbing and variable expansion do not work.

## Loading vs Starting

Loading a plist is not the same as starting the job. Only RunAtLoad and KeepAlive trigger automatic execution. Use `launchctl load` / `launchctl bootstrap` to load, and `launchctl start` to manually start.

## Permissions

- Job definitions: readable by owner, not writable by group/other (0644 recommended).
- Directories: searchable by owner, not writable by group/other (0755 recommended).
- Agents owned by their user. Daemons owned by root.
