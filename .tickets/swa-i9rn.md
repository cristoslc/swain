---
id: swa-i9rn
status: closed
deps: []
links: []
created: 2026-03-13T02:06:43Z
type: task
priority: 1
assignee: cristos
parent: swa-rosx
tags: [spec:SPIKE-009]
---
# Research microVM options (Firecracker, QEMU/Lima/Orbstack)

Investigate microVM startup latency. Evaluate filesystem sharing (virtiofs, 9p, sshfs) vs bind-mount performance for interactive use. Firecracker is Linux-only — document macOS equivalents. Compare resource overhead vs containers.


## Notes

**2026-03-13T02:25:10Z**

Completed: MicroVM research. Key findings: (1) Firecracker is Linux-only, no virtiofs (deliberate), <125ms VM boot but 1-7s total cold start. (2) Lima/vz boots 3-5s on Apple Silicon with virtiofs at 70-90% native read perf; 9p is 7x slower. (3) Cloud Hypervisor/crosvm not practical for desktop use, no macOS. (4) inotify does NOT work across any VM filesystem boundary. (5) Docker Sandboxes are purpose-built for AI agent sandboxing (Claude Code), use microVMs on macOS/Windows but container-only fallback on Linux. (6) Apple Containers (macOS 26) are promising but v0.6.0, not production-ready until late 2026+. (7) Recommendation tier: Docker Sandboxes > Docker via Colima/OrbStack > OrbStack alone.
