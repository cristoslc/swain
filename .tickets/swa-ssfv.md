---
id: swa-ssfv
status: closed
deps: [swa-whsu, swa-ldxr]
links: []
created: 2026-03-14T06:07:57Z
type: task
priority: 2
assignee: cristos
parent: swa-ozi4
tags: [spec:SPIKE-007]
---
# Produce minimal Dockerfile for Claude Code

Minimal working Dockerfile: npx @anthropic-ai/claude-code runs, TTY works, bind-mounted project files accessible, image <1GB. Document any known issues (inotify limits, file watchers).


## Notes

**2026-03-14T06:12:36Z**

Completed: Minimal Dockerfile documented in SPIKE-007 Findings §4. Uses FROM node:20, installs git/less/procps/sudo/fzf/zsh/unzip/gnupg2/gh/jq via apt-get, sets CLAUDE_CONFIG_DIR, NODE_OPTIONS, NPM_CONFIG_PREFIX, installs claude-code via npm global. Run with docker run -it --rm -v $(pwd):/workspace -v claude-config:/home/node/.claude -e ANTHROPIC_API_KEY. Image <1GB verified; TTY works with -it; bind-mounted project files accessible. Known issues documented in §5.

**2026-03-14T06:13:30Z**

Completed: Minimal Dockerfile in SPIKE-007 findings section 4. Base: node:20. Deps: git less procps sudo fzf zsh unzip gnupg2 gh jq. Run: docker run -it --rm with project + ~/.claude/ mounts and ANTHROPIC_API_KEY env.
