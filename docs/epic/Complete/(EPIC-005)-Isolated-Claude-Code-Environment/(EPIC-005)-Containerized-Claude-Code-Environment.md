---
title: "Isolated Claude Code Environment"
artifact: EPIC-005
track: container
status: Complete
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
parent-vision: VISION-001
parent-initiative: INITIATIVE-006
success-criteria:
  - A single command in the project root launches Claude Code inside an isolated ephemeral environment
  - The environment has full read/write access to the project directory via filesystem binding
  - Agent state (.claude/, .agents/, .tickets/) persists across environment restarts via filesystem binding
  - Credentials (API keys, git auth) are forwarded without baking them into the image
  - Environment cleanup is automatic — no orphaned instances or volumes accumulate
addresses: []
trove:
linked-artifacts:
  - SPEC-048
  - SPEC-049
  - SPIKE-009

depends-on-artifacts: []
---

# Isolated Claude Code Environment

## Goal / Objective

Provide a one-command workflow to run Claude Code inside an isolated, ephemeral environment instead of directly on the host. This keeps the agent's runtime environment — package installations, tool executions, and side effects — separated from the host system, while preserving full access to the project tree and persistent state through filesystem binding.

The isolation mechanism (Docker container, microVM, or other) is an open question to be resolved by research spikes before implementation.

## Scope Boundaries

**In scope:**
- Launcher script or Makefile target in the project root (e.g., `./claude-isolated` or `make claude`)
- Image or VM selection for running Claude Code CLI
- Filesystem binding for project files, agent state, and credential forwarding
- Ephemeral lifecycle (auto-remove on exit)
- Documentation for setup and usage

**Out of scope:**
- Multi-instance orchestration (docker-compose, k8s)
- CI/CD integration — this is for local interactive use
- Custom Claude Code builds or forks
- GPU passthrough or model hosting inside the environment

## Child Specs

- SPEC-048: `claude-sandbox` launcher — Tier 1 native sandboxing (sandbox-exec / Landlock) ✅
- SPEC-049: `claude-sandbox --docker` — Tier 2 Docker container runner with credential forwarding ✅

## Key Dependencies

- Isolation runtime installed on host (Docker already available; microVM TBD by SPIKE-009)
- Claude Code CLI available as an installable package (npm/npx)
- Valid Anthropic API key or OAuth credentials on host

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-12 | — | Initial creation |
| Active | 2026-03-14 | cded412 | SPIKE-009 complete; decomposed into SPEC-048 and SPEC-049 |
| Complete | 2026-03-14 | 2843b4e | SPEC-048 (Tier 1 sandbox launcher) and SPEC-049 (Tier 2 Docker runner) delivered; all success criteria met |
