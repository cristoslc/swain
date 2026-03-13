---
id: swa-r37l
status: closed
deps: []
links: []
created: 2026-03-13T02:06:43Z
type: task
priority: 2
assignee: cristos
parent: swa-rosx
tags: [spec:SPIKE-009]
---
# Research Orbstack for macOS-specific path

Orbstack is macOS-only. Does it simplify the macOS story enough to justify a platform-specific path? Compare startup time, filesystem performance, and resource usage vs Docker Desktop and Lima. Check if it supports both Docker and Linux VM modes.


## Notes

**2026-03-13T02:17:38Z**

Completed: OrbStack research. Key findings: (1) macOS-only, closed-source, free for personal use. (2) 2s cold start vs Docker Desktop's 30s; ~60% less memory. (3) Docker API compatible drop-in replacement. (4) CRITICAL: No docker sandbox support (issue #2295, 144+ upvotes). (5) Apple Containers (WWDC 2025, macOS 26) may supersede it within 12-18 months. (6) Recommendation: use as optional performance optimization, not required dependency.
