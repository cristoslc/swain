---
id: swa-31se
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
# Research Dev Containers spec as abstraction layer

Does .devcontainer/ spec work across Docker and other runtimes on both macOS and Linux? Would it give IDE integration for free? Evaluate whether it constrains runtime selection or adds useful portability. Check if it handles credential forwarding and state persistence natively.


## Notes

**2026-03-13T02:17:38Z**

Completed: Dev Containers research. Key findings: (1) Microsoft-maintained open spec, mature with VS Code/JetBrains support. (2) Docker-centric despite 'runtime-agnostic' goal; Podman works but second-class. (3) Anthropic publishes reference devcontainer for Claude Code with firewall rules. (4) CLI is incomplete — missing stop/down, no SSH agent forwarding. (5) Cannot target microVMs. (6) Recommendation: use devcontainer.json as configuration format but invoke Docker directly via launcher script rather than depending on devcontainer CLI.
