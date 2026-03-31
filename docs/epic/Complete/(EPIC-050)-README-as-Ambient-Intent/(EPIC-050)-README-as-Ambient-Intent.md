---
title: "README as Ambient Intent"
artifact: EPIC-050
track: container
status: Complete
author: operator
created: 2026-03-31
last-updated: 2026-03-31
parent-vision: VISION-004
parent-initiative: INITIATIVE-005
priority-weight: ""
success-criteria:
  - README.md is checked at session start, retro, and release — drift surfaces automatically
  - swain-init seeds a README when missing and proposes artifacts from README content
  - swain-doctor flags missing README on every session
  - Release gate blocks on unresolved README drift and untested README promises
  - Reconciliation is bidirectional — operator decides which side to update
depends-on-artifacts: []
addresses: []
evidence-pool: ""
---

# README as Ambient Intent

## Goal / Objective

Make README.md a first-class input to swain's alignment loop. The README is the most public statement of what a project claims to do, yet swain currently ignores it. This epic weaves README awareness into existing skills — init, doctor, session, retro, release, and design — so that drift between README promises and project reality surfaces automatically.

## Desired Outcomes

The operator never ships a release where the README contradicts the artifact tree or promises untested behavior. New projects get a useful README from day one, and swain can bootstrap artifacts from it. Mature projects catch README rot before it reaches users.

## Progress

<!-- Auto-populated from session digests. See progress.md for full log. -->

## Scope Boundaries

**In scope:**
- README seeding and artifact proposals in swain-init
- README existence check in swain-doctor
- Session-start reconciliation checkpoint (firm elbow with deferral)
- Retro reconciliation checkpoint
- Release gate (alignment + verification)
- Design transition nudge and brainstorming context from README
- Semantic extraction of claims from README prose

**Out of scope:**
- README is not a lifecycle artifact — no frontmatter, no phases, no specgraph entry
- Swain never silently rewrites the README — all changes go through the operator
- Swain does not auto-generate tests — it identifies untested promises
- Swain does not impose README structure or templates

## Child Specs

- SPEC-207 — README seeding and artifact proposals in swain-init
- SPEC-208 — Flag missing README in swain-doctor
- SPEC-209 — README reconciliation at focus lane selection
- SPEC-210 — README drift check in swain-retro
- SPEC-211 — Two-part release gate for README alignment and verification
- SPEC-212 — Soft nudge on artifact transitions + brainstorming context

## Key Dependencies

None. Each child spec modifies an existing skill — no new skills or file formats required.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | 184576e | Initial creation from design doc |
| Complete | 2026-03-31 | — | All 6 child SPECs implemented and verified |
