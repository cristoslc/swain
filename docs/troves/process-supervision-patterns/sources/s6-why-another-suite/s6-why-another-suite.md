---
source-id: s6-why-another-suite
type: web
url: "https://skarnet.org/software/s6/why.html"
title: "s6: why another supervision suite — skarnet.org"
fetched: 2026-04-06T17:02:23Z
---

# s6: Why Another Supervision Suite

Laurent Bercot explains why s6 was created and how it compares to daemontools, runit, supervisord, and integrated init systems.

## Design Criteria

s6 was built around five criteria that existing suites failed to meet:

### 1. Energy Efficiency (Event-Driven)

daemontools and original runit wake up every 5 seconds to check for new services. s6-svscan never wakes up unless it receives a command via s6-svscanctl. The `-t` option allows configurable timeout, with infinite timeout as default.

### 2. Process 1 Capability

s6-svscan was designed from the start to run as process 1 (PID 1), though it does not have to. daemontools was never designed for this role. runit uses a separate init/supervision chain.

### 3. Code Simplicity and Stability

s6-svscan and s6-supervise do not allocate heap memory. Main source files are under 500 lines each. This contrasts with integrated systems:

- Upstart uses ptrace and libdbus linking.
- launchd requires XML parsing and Mach IPC.
- systemd adds exponential complexity.

### 4. Notification Framework

Unlike daemontools and runit (which rely on manual polling), s6 provides an event notification library with command-line tools. This enables higher-level service management without embedding it in process 1.

### 5. Asynchronous Reliability

s6-supervise operates as a full deterministic finite automaton. Pipes between daemons and loggers are never lost when run as process 1, matching daemontools' design while exceeding runit's guarantees.

## Design Philosophy

The core principle is separation of concerns: process supervision and machine management are two different functions. Integrated init systems (systemd, launchd, Upstart) violate this by combining incompatible responsibilities in PID 1, the system's most critical process.

## Comparison Summary

| Feature | daemontools | runit | s6 |
|---------|-------------|-------|----|
| Event-driven scan | No (5s poll) | No (5s poll) | Yes |
| PID 1 capable | No | Separate chain | Yes (optional) |
| Heap allocation in supervisor | Yes | Yes | No |
| Notification framework | No | No | Yes |
| Pipe reliability as PID 1 | N/A | Weaker | Strong |
