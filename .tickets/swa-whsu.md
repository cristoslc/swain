---
id: swa-whsu
status: closed
deps: []
links: []
created: 2026-03-14T06:07:57Z
type: task
priority: 2
assignee: cristos
parent: swa-ozi4
tags: [spec:SPIKE-007]
---
# Research Claude Code Node.js and system dependencies

Does Anthropic publish an official image? What base image works (node:lts-slim, alpine)? What system deps beyond Node.js are required (git, ripgrep, bash, python)?


## Notes

**2026-03-14T06:11:29Z**

Completed: Official base image is node:20. Deps: git, less, procps, sudo, fzf, zsh, unzip, gnupg2, gh, jq. No ripgrep or python needed — bundled via npm. CLAUDE_CONFIG_DIR=/home/node/.claude, NODE_OPTIONS=--max-old-space-size=4096, DEVCONTAINER=true.
