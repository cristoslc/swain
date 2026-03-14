---
title: "README Rewrite for New User Onboarding"
artifact: EPIC-003
track: container
status: Complete
author: cristos
created: 2026-03-11
last-updated: 2026-03-11
parent-vision:
  - VISION-001
success-criteria:
  - A new user who has never seen swain can install it, run their first session, and understand the core workflow within 10 minutes of reading the README
  - The README accurately reflects swain's current skill set, artifact model, and operational flow
  - Skill descriptions convey what each skill does for the user, not just what it does internally
  - Installation instructions cover autodetected multi-platform support (not just Claude Code)
  - The README includes a concrete walkthrough showing the first-session experience (doctor → status → design → do cycle)
  - No stale references to removed features, old skill names, or deprecated workflows
addresses: []
evidence-pool: ""
linked-artifacts: []
depends-on-artifacts: []
---

# README Rewrite for New User Onboarding

## Goal / Objective

Rewrite the project README so it serves as the primary onboarding surface for users who have never encountered swain. The current README was written incrementally as skills were added — it reads like a changelog of capabilities rather than a guide for someone asking "what is this and why should I care?"

The new README should answer three questions in order:

1. **What does swain do?** — persistent project state for solo dev + AI agent workflows
2. **What does a session look like?** — the doctor → status → design → do loop, with a concrete example
3. **How do I get started?** — install, init, first session

## Scope Boundaries

**In scope:**
- Complete rewrite of README.md content and structure
- Updated skill table reflecting the current roster (including swain-keys, swain-status, swain-init)
- A "First session" walkthrough section showing the onboarding flow
- Updated install instructions reflecting autodetected platform support
- Updated requirements section (bd is now optional, uv role clarified)
- Accurate configuration section reflecting current settings model
- Architecture/workflow diagram showing the skill interaction model

**Out of scope:**
- Detailed per-skill documentation (belongs in each skill's SKILL.md)
- Tutorial content beyond first-session onboarding (future RUNBOOK or docs site)
- Changes to skill behavior or APIs — documentation only
- Marketing copy or landing page concerns

## Child Specs

To be decomposed after approval. Likely candidates:

- SPEC-NNN: README structure and content (the main rewrite)
- SPEC-NNN: First-session walkthrough (concrete example flow with expected output)
- SPEC-NNN: Architecture diagram (mermaid diagram showing skill interaction model)

Or this may be a single SPEC if the scope stays contained to one file.

## Key Dependencies

- EPIC-002 progress — if the artifact type system changes land before this README ships, the README should reflect the new model. Not a hard blocker, but coordinate timing.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-11 | — | Initial creation |
| Active | 2026-03-11 | ff1dae7 | Scope is one file; implementing directly |
| Complete | 2026-03-12 | d165af2 | All success criteria met; README rewritten |
