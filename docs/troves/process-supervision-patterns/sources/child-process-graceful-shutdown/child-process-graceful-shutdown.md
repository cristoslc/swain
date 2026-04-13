---
source-id: child-process-graceful-shutdown
type: web
url: "https://medium.com/@muhammedsaidkaya/child-process-graceful-shutdown-in-shell-scripting-8827ea45982a"
title: "Child Process Graceful Shutdown in Shell Scripting — Muhammed Said Kaya"
fetched: 2026-04-06T17:02:00Z
notes: "Direct export failed (403). Content from WebFetch fallback."
---

# Child Process Graceful Shutdown in Shell Scripting

Practical patterns for propagating shutdown signals from a parent daemon to its child processes.

## Core Problem

When a parent process receives SIGTERM, its child processes may not receive the signal automatically. Without explicit handling, children become orphaned or left in inconsistent states.

## Signal Handling with trap

The `trap` command intercepts signals and runs custom functions:

```bash
trap _term SIGTERM
trap _int SIGINT
```

## Propagating Signals to Children

### Method 1: Kill with Job Control

Use `jobs -p` to get child PIDs, then send signals explicitly:

```bash
function _term() {
    kill -TERM $(jobs -p)
    wait $(jobs -p)
}
```

This sends SIGTERM to all background children, then waits for them to finish.

### Method 2: Process Group Signaling

Send signals to the entire process group for bulk termination. The parent's PID is the process group ID when it leads the group:

```bash
kill -TERM -$$  # Negative PID targets the process group
```

### Method 3: File-Based Signaling (IPC)

Use shared state files to communicate shutdown intent:

1. Create a global state file.
2. Child processes check file status in loops.
3. Parent modifies file when shutdown is needed.

This resembles Go's cancelable contexts, where a flag controls process termination.

### Method 4: Named Pipes

Keep processes alive while awaiting shutdown signals via named pipes. The parent writes to the pipe to signal children.

## Key Takeaways

- If you run jobs as child processes, you must handle graceful shutdown explicitly.
- SIGTERM does not automatically cascade to all descendants.
- The safest pattern is: trap SIGTERM in parent, send SIGTERM to children, wait for children to exit, then exit parent.
- For complex trees (supervisor -> children -> grandchildren), consider process groups or explicit cascading.
