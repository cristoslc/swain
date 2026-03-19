---
title: "Cross-Runtime Documentation"
artifact: EPIC-032
track: container
status: Proposed
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
parent-vision: VISION-003
parent-initiative: INITIATIVE-014
priority-weight: medium
success-criteria:
  - Per-runtime compatibility matrix documented (what works, what degrades)
  - Swain tested on current versions of Gemini CLI and OpenCode
  - Copilot experience documented (already confirmed working)
  - AGENTS.md and .agents/skills/ coverage verified across runtimes
  - User-facing "getting started on X" guide for 3+ runtimes
depends-on-artifacts:
  - SPIKE-029
addresses: []
evidence-pool: ""
---

# Cross-Runtime Documentation

## Goal / Objective

Document and verify swain's existing cross-runtime compatibility. Swain's AGENTS.md and `.agents/skills/` conventions are already compatible with multiple runtimes — this epic captures the current state, tests on latest runtime versions, and produces user-facing documentation.

This is largely documentation work, not code. Swain already works in Copilot (confirmed by operator). Gemini CLI and OpenCode need retesting on current versions.

## Scope Boundaries

**In scope:**
- Test swain discovery and skill loading in Gemini CLI, OpenCode (current versions), and Copilot (verify current state)
- Document what works, what degrades, and what's unavailable per runtime
- Create a compatibility matrix in the VISION-003 supporting docs
- Write per-runtime "getting started" notes
- Document the AGENTS.md + CLAUDE.md dual-file strategy

**Out of scope:**
- Building runtime-specific adapters or bundles (that's Phase 4)
- MCP server development (EPIC-033)
- Any code changes to swain skills

## Child Specs

_To be created. Expected specs:_
- Cross-runtime compatibility testing (Gemini CLI, OpenCode, Cursor, Windsurf)
- Compatibility matrix document
- Per-runtime quick-start guide

## Key Dependencies

- SPIKE-029 (Cross-Runtime Portability Substrate) — findings inform what to test
- Access to Gemini CLI, OpenCode, Cursor for testing

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-18 | | Initial creation |
