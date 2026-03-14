---
title: "Container Image and Runtime Requirements"
artifact: SPIKE-007
status: Active
author: cristos
created: 2026-03-12
last-updated: 2026-03-14
question: "What base image, dependencies, and runtime configuration are needed to run Claude Code CLI inside a Docker container?"
gate: Pre-MVP
risks-addressed:
  - No official Claude Code Docker image may exist — need to confirm or build one
  - Claude Code may have host-level dependencies (Node.js version, native modules) that complicate containerization
  - Interactive terminal mode (TTY allocation) may behave differently in containers
evidence-pool:
linked-artifacts: []
---

# Container Image and Runtime Requirements

**Note:** This spike is conditional on SPIKE-009 selecting containers as the isolation mechanism. If SPIKE-009 recommends microVMs, this spike may be abandoned or adapted.

## Question

What base image, dependencies, and runtime configuration are needed to run Claude Code CLI inside a Docker container?

Sub-questions:
1. Does Anthropic publish an official Claude Code container image? If not, what base image (node:lts-slim, alpine, etc.) works?
2. What are Claude Code's runtime dependencies beyond Node.js/npm? (git, ripgrep, bash, python, etc.)
3. How does `npx @anthropic-ai/claude-code` behave in a container — does it require TTY allocation (`-it`), and does it handle terminal resize?
4. What is the minimum viable Dockerfile to get a working Claude Code session?
5. Are there any known issues with running Claude Code in containers (file watchers, inotify limits, etc.)?

## Go / No-Go Criteria

- **Go**: A Dockerfile that successfully runs `claude` interactively with TTY, can read/write bind-mounted project files, and exits cleanly. Total image size under 1GB.
- **No-Go**: Claude Code requires host-level access (e.g., macOS-specific APIs, Keychain, GUI) that cannot be satisfied in a Linux container.

## Pivot Recommendation

If Claude Code cannot run in a standard Docker container, investigate:
1. Docker-in-Docker or sysbox for deeper isolation
2. Lima/colima VM-based approach instead of pure containers
3. Dev Containers specification (`.devcontainer/`) which handles many of these concerns natively

## Findings

### 1. Base Image

**Official answer: `node:20`**

Anthropic publishes a first-party reference Dockerfile at `anthropics/claude-code/.devcontainer/Dockerfile`. It uses `node:20` (full Debian-based image, not slim or alpine). `node:18` is the minimum per the README; `node:20` is the officially supported version.

The full (non-slim) image is required — the dependency list needs Debian's `apt-get` and several system tools absent from slim variants.

### 2. System Dependencies

The official Dockerfile installs via `apt-get`:

```
less git procps sudo fzf zsh man-db unzip gnupg2
gh iptables ipset iproute2 dnsutils aggregate jq nano vim
```

Additionally: `git-delta` v0.18.2 from GitHub releases (architecture-aware: `amd64` + `arm64`).

Claude Code is installed as:
```
npm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}
```
into a custom npm global prefix at `/usr/local/share/npm-global`.

**Notable absences**: `ripgrep` is not in the apt list — Claude Code bundles its own search tooling via npm. `python` is not required.

Key environment variables the devcontainer sets:
- `NODE_OPTIONS=--max-old-space-size=4096` (4 GB heap cap)
- `CLAUDE_CONFIG_DIR=/home/node/.claude`
- `DEVCONTAINER=true`

### 3. TTY Behavior

**`-it` is required for interactive mode.** Non-interactive (`claude -p "..."`) works without TTY.

Evidence:
- Issue #12084: Claude Code 2.0.43+ exits immediately after the welcome screen on RHEL8 — the TUI event loop requires a proper TTY. `claude -p` is unaffected.
- Issue #30369: `claude auth login` inside Docker does not show the authorization code prompt. Workaround: run `claude` directly while unauthenticated, or pass `ANTHROPIC_API_KEY` to skip OAuth entirely.
- Issue #16135: Killing a background process spawned by Claude (via `docker exec -it`) also kills Claude — shared process group. `docker run --init` does not help for `docker exec` sessions.

**SIGWINCH / terminal resize**: No specific issues found. Standard terminal resize signals should propagate normally via `docker exec -it` with `zsh` and `xterm-256color`.

### 4. Minimal Dockerfile

```dockerfile
FROM node:20

ARG CLAUDE_CODE_VERSION=latest
ENV DEVCONTAINER=true

RUN apt-get update && apt-get install -y --no-install-recommends \
  git less procps sudo fzf zsh unzip gnupg2 gh jq \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/local/share/npm-global && chown -R node:node /usr/local/share
RUN mkdir -p /workspace /home/node/.claude && chown -R node:node /workspace /home/node/.claude

WORKDIR /workspace
USER node

ENV NPM_CONFIG_PREFIX=/usr/local/share/npm-global
ENV PATH=$PATH:/usr/local/share/npm-global/bin
ENV NODE_OPTIONS=--max-old-space-size=4096
ENV CLAUDE_CONFIG_DIR=/home/node/.claude

RUN npm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}
```

Run with:
```bash
docker run -it --rm \
  -v "$(pwd)":/workspace \
  -v claude-config:/home/node/.claude \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  <image> claude
```

The `claude-config` named volume persists auth state across container restarts. The official devcontainer also adds `--cap-add=NET_ADMIN --cap-add=NET_RAW` for iptables-based network filtering, but that is optional for non-sandboxed use.

### 5. Known Issues

| Issue | Severity | Detail |
|-------|----------|--------|
| Atomic rename breaks bind mounts | Medium | Claude Code's Edit/Write use `os.replace(tmp, target)` — a new inode. Docker bind mounts cache the old inode; other containers watching the same bind-mounted files won't see updates. Does **not** affect Claude-inside-container editing host-bind-mounted files (the intended use case). Issue #25438. |
| Background process SIGKILL crash | Medium | Killing a background process via `docker exec -it` also kills Claude — shared process group. Issue #16135. |
| OAuth auth login prompt missing | Low | `claude auth login` doesn't show code entry in Docker. Workaround: pass `ANTHROPIC_API_KEY` via env, or run `claude` directly while unauthenticated. Issue #30369. |
| API key ignored at login screen | Low | In Docker Compose devcontainers, if OAuth fails first, env `ANTHROPIC_API_KEY` is not detected until after OAuth. Fix: ensure `~/.claude` is a named volume so auth state persists. Issue #34141. |
| Memory usage | High | Claude Code processes have reached 50–129 GB RAM in long sessions. The `NODE_OPTIONS=--max-old-space-size=4096` cap mitigates this. |

### 6. Verdict

**Go.** Anthropic publishes a first-party, production-quality Dockerfile and devcontainer.json in `anthropics/claude-code`. The dependency list is concrete and complete. Interactive TTY works with `-it`; non-interactive scripted use works without it. Auth is cleanly handled via `ANTHROPIC_API_KEY` env var, bypassing OAuth entirely. The bind-mount inode issue affects _other_ containers watching Claude-edited files, not Claude-inside-container — not a blocker.

The background process signal propagation issue (#16135) matters if Claude spawns long-running dev servers but is not a blocker for the core isolated-session use case.

### 7. Sources

| Source | Reference |
|--------|-----------|
| Official Dockerfile | `github.com/anthropics/claude-code/blob/main/.devcontainer/Dockerfile` |
| Official devcontainer.json | `github.com/anthropics/claude-code/blob/main/.devcontainer/devcontainer.json` |
| init-firewall.sh | `github.com/anthropics/claude-code/blob/main/.devcontainer/init-firewall.sh` |
| Issue #25438 — bind mount inode bug | `github.com/anthropics/claude-code/issues/25438` |
| Issue #16135 — background process crash | `github.com/anthropics/claude-code/issues/16135` |
| Issue #30369 — auth login prompt missing | `github.com/anthropics/claude-code/issues/30369` |
| Issue #34141 — API key ignored in Docker Compose | `github.com/anthropics/claude-code/issues/34141` |
| Issue #12084 — TUI exits immediately (TTY) | `github.com/anthropics/claude-code/issues/12084` |

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-12 | — | Initial creation |
| Active | 2026-03-14 | 257ea9c | Transition to Active |
