---
id: swa-5hyu
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
# Research Docker container isolation guarantees

Investigate Docker isolation on macOS vs Linux. On macOS, Docker Desktop runs a Linux VM — is container-in-VM sufficient? On Linux, containers share host kernel — is that acceptable for running arbitrary agent commands? Document cold/warm startup times on each platform. Assess whether namespace/cgroup isolation is enough for the threat model.


## Notes

**2026-03-13T02:17:38Z**

Completed: Docker isolation research. Key findings: (1) macOS has strong isolation via container-in-VM model, Linux shares kernel but rootless Docker mitigates escape risk. (2) Warm start 0.5-1.9s meets <5s target; cold start on macOS 10-30s exceeds it. (3) VirtioFS is default on macOS, ~3x slower than native but acceptable; DELETE file events broken. (4) Rootless Docker recommended on Linux, 60-80% attack surface reduction. (5) CPU overhead <3%, memory ~150MB daemon + 1-2GB VM on macOS.
