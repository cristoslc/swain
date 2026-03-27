---
title: "swain-box Multi-Agent Runtime Support"
artifact: EPIC-030
track: container
status: Complete
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
parent-vision: VISION-002
parent-initiative: INITIATIVE-012
priority-weight: medium
success-criteria:
  - swain-box detects installed agent runtimes at startup and presents a selection menu when more than one is available
  - Each supported agent runtime has an auth passthrough mechanism that does not bake credentials into any sandbox image or state
  - Isolation properties for each runtime are verified via a per-runtime test suite
  - The swain-box experience is defined by a DESIGN artifact covering selection flow, error states, and edge cases
depends-on-artifacts:
  - SPEC-067
addresses: []
trove: ""
linked-artifacts:
  - DESIGN-002
  - SPEC-067
  - SPEC-068
  - SPEC-069
  - SPEC-070
---

# swain-box Multi-Agent Runtime Support

## Goal / Objective

swain-box currently hard-codes Claude Code as the only agent runtime (`docker sandbox run claude`). As other agent CLIs (GitHub Copilot, OpenAI Codex) gain Docker Sandboxes support, operators should be able to choose which runtime to launch without editing scripts.

This epic extends swain-box to: (1) detect which agent runtimes are available in the current Docker Sandboxes installation, (2) surface a selection menu when more than one is detected, and (3) provide per-runtime auth passthrough and isolation validation.

## Scope Boundaries

**In scope:**
- Agent runtime detection logic (probe `docker sandbox run <runtime> --version` or equivalent)
- Interactive selection menu when multiple runtimes are available (single runtime auto-selects)
- Per-runtime auth passthrough: ANTHROPIC_API_KEY / CLAUDE_CODE_OAUTH_TOKEN for Claude; GITHUB_TOKEN / COPILOT_* for Copilot; OPENAI_API_KEY for Codex
- Per-runtime isolation test suites (verify sandbox-level process separation, credential non-leakage)
- DESIGN-002 covering the full selection UX

**Out of scope:**
- Custom runtime plugins or third-party CLIs beyond the three named runtimes
- Windows or Linux Docker Sandboxes support (macOS Docker Desktop only for now)
- Model routing inside the runtime (which model the agent uses is the agent's concern)
- Remote/cloud sandbox targets

## Child Specs

- SPEC-068: swain-box Agent Runtime Detection & Selection Menu (Proposed)
- SPEC-069: swain-box GitHub Copilot Runtime Support (Proposed)
- SPEC-070: swain-box OpenAI Codex Runtime Support (Proposed)

## Key Dependencies

- SPEC-067 (Complete): established Docker Sandboxes as the isolation mechanism and the `swain-box` script skeleton
- Docker Sandboxes must expose each agent runtime as a separate named sandbox image (e.g., `docker sandbox run copilot`, `docker sandbox run codex`) — this is the current Docker Desktop trajectory

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-18 | — | Initial creation; extends SPEC-067 to multi-runtime |
| Complete | 2026-03-19 | — | All 3 specs complete — multi-runtime detection, selection, and credential handling |
