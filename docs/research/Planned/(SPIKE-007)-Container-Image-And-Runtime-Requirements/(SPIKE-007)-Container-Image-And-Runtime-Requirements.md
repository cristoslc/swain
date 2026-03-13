---
title: "Container Image and Runtime Requirements"
artifact: SPIKE-007
status: Planned
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
question: "What base image, dependencies, and runtime configuration are needed to run Claude Code CLI inside a Docker container?"
gate: Pre-MVP
risks-addressed:
  - No official Claude Code Docker image may exist — need to confirm or build one
  - Claude Code may have host-level dependencies (Node.js version, native modules) that complicate containerization
  - Interactive terminal mode (TTY allocation) may behave differently in containers
depends-on:
  - SPIKE-009
evidence-pool:
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

*(To be populated during Active phase)*

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-12 | — | Initial creation |
