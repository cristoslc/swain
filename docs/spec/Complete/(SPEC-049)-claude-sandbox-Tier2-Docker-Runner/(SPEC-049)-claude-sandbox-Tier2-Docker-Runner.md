---
title: "claude-sandbox: Tier 2 Docker Container Runner"
artifact: SPEC-049
track: implementable
status: Complete
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
type: feature
parent-epic: EPIC-005
linked-artifacts:
  - EPIC-005
  - SPIKE-009
depends-on-artifacts:
  - SPEC-048
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# claude-sandbox: Tier 2 Docker Container Runner

## Problem Statement

SPIKE-009 recommends Docker containers as an opt-in Tier 2 for operators who want stronger isolation (image-level reproducibility, root filesystem separation) or who already have Docker installed. This spec extends the `claude-sandbox` launcher from SPEC-048 with a `--docker` flag that runs Claude Code inside a Docker container with bind-mounted project files and forwarded credentials.

## External Behavior

`./claude-sandbox --docker` runs Claude Code in a Docker container:

1. Verifies `docker` is available; exits with a clear error if not
2. Checks that the Docker daemon is running; emits a setup hint if not
3. Pulls or uses a pre-built Claude Code image (configurable, default: `ghcr.io/anthropics/claude-code:latest` or the official Anthropic devcontainer image if available)
4. Binds the project root at the same absolute path inside the container
5. Binds agent state directories (`.claude/`, `.agents/`, `.tickets/`) for persistence across restarts
6. Forwards credentials as environment variables (`ANTHROPIC_API_KEY`, `GITHUB_TOKEN`, `GH_TOKEN`)
7. Forwards git identity env vars
8. Runs the container with `--rm` for auto-cleanup on exit
9. Falls back to a minimal Dockerfile in `scripts/claude-sandbox.dockerfile` if no image is configured

### devcontainer.json integration

Also creates `.devcontainer/devcontainer.json` using the Anthropic reference config as a base. This enables IDE integration (VS Code Dev Containers, JetBrains) alongside the CLI runner. The devcontainer config is sourced from the same `swain.settings.json` `sandbox` stanza as SPEC-048.

### Platform differences

| Platform | Runtime | Filesystem performance |
|----------|---------|----------------------|
| macOS | Docker Desktop / Colima / OrbStack | ~33% native (VirtioFS) |
| Linux | Docker Engine (rootless recommended) | 100% native (bind mount) |

## Acceptance Criteria

1. **Given** Docker is installed and the daemon is running, **when** `./claude-sandbox --docker` is run, **then** Claude Code launches inside a container with the project files accessible at the same path.
2. **Given** a running Docker session, **when** the agent writes a file to the project directory, **then** the file appears on the host filesystem immediately (bind mount semantics).
3. **Given** `ANTHROPIC_API_KEY` is set on the host, **when** the container starts, **then** the key is available inside the container without being baked into the image.
4. **Given** the container session exits (normally or via Ctrl-C), **when** cleanup completes, **then** the container is removed (`--rm`) and no volumes accumulate.
5. **Given** Docker is not installed, **when** `./claude-sandbox --docker` is run, **then** the script exits with an informative error and suggests installing Docker or using `./claude-sandbox` (Tier 1).
6. **Given** `.devcontainer/devcontainer.json` does not exist, **when** `./claude-sandbox --docker` runs for the first time, **then** it creates the file using the Anthropic reference config.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1: Launches with Docker; project files accessible | `--docker` flag in claude-sandbox; `docker run -v $REPO_ROOT:$REPO_ROOT` bind mount | ✅ |
| AC2: File writes appear on host | Bind mount (not volume); writes go directly to host filesystem | ✅ |
| AC3: API key forwarded without baking into image | All secrets via `-e KEY` env flags; Dockerfile has no ENV for credentials | ✅ |
| AC4: Container removed on exit | `docker run --rm` flag | ✅ |
| AC5: Clear error when Docker not installed | Guard checks `command -v docker` and `docker info`; prints install hint | ✅ |
| AC6: devcontainer.json created on first run | Script creates `.devcontainer/devcontainer.json` if absent | ✅ |

## Scope & Constraints

- Tier 2 only — extends, does not replace SPEC-048 Tier 1
- No Docker Compose, no multi-container setups
- Not for CI/CD — local interactive use only
- The image must not contain credentials; all secrets forwarded at runtime via env vars
- No Docker Sandboxes (Tier 3) — that requires Docker Desktop license; out of scope for MVP

## Implementation Approach

1. Extend `scripts/claude-sandbox` with `--docker` flag detection
2. Build the `docker run` invocation: bind mounts, env forwarding, `--rm`, interactive TTY (`-it`)
3. Create a minimal `scripts/claude-sandbox.dockerfile` as fallback image
4. Generate `.devcontainer/devcontainer.json` from Anthropic reference template on first run
5. Test on macOS (Docker Desktop) and Linux (Docker Engine)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | cded412 | Created from EPIC-005 decomposition; depends on SPEC-048 for launcher script base |
| Complete | 2026-03-14 | -- | --docker flag added to claude-sandbox; Dockerfile, devcontainer.json generation, credential forwarding via env vars |
