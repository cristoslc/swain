---
id: swa-ebgy
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
# Research Nix and platform-native sandboxing

Could nix develop or platform-native sandboxing (sandbox-exec on macOS, namespaces on Linux) provide sufficient isolation without a full VM/container? Assess whether process/filesystem namespace isolation meets the threat model. Document limitations — sandbox-exec is deprecated on macOS.


## Notes

**2026-03-13T02:26:04Z**

Completed: Nix/sandboxing research. Key findings: (1) Nix provides dependency isolation only, zero security isolation at runtime. (2) macOS sandbox-exec is deprecated but actively used by Anthropic (sandbox-runtime) and OpenAI (Codex CLI) — the only viable CLI sandboxing on macOS. (3) bubblewrap on Linux: ~3k lines C, unprivileged, full namespace isolation, ~10ms startup. Landlock adds filesystem/network ACLs without namespaces (kernel 5.13+). (4) Apple Containers v0.1.0 — compelling but not current solution. (5) No single cross-platform tool exists; proven pattern is unified config that compiles to sandbox-exec on macOS + bubblewrap/Landlock on Linux. (6) These approaches are 'good enough' for accidental damage prevention with native filesystem perf and ~10ms startup.
