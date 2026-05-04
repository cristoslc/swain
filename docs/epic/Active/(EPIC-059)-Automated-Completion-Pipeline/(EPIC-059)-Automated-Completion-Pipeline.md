---
title: "Automated Completion Pipeline"
artifact: EPIC-059
track: container
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-vision: VISION-001
parent-initiative: INITIATIVE-002
priority-weight: high
success-criteria:
  - swain-do runs BDD, smoke, and retro on its own after all tasks close
  - swain-teardown finds skipped steps and runs them before sync
  - A state file tracks which steps ran so both skills can read it
  - The operator never types the post-done checklist again
depends-on-artifacts: []
addresses: []
evidence-pool: ""
---

# Automated Completion Pipeline

## Goal / Objective

Stop making the user type "BDD, smoke, retro, merge, push" after each SPEC. Bake that into the skills. "Done" should mean done.

## Desired Outcomes

The user wraps up a SPEC and the rest runs on its own. Tests, smoke, and retro fire in order. If a crash breaks the chain, teardown runs what was missed. Think about what to build, not what to run.

## Progress

<!-- Auto-populated from session digests. See progress.md for full log. -->

## Scope Boundaries

**In scope:**
- swain-do runs BDD, smoke, and retro after all tasks close
- A state file tracks which steps ran
- Teardown checks the file and runs missed steps

**Out of scope:**
- Sync itself (same as before)
- Merge and push (still a user choice)
- CI/CD (local only)

## Child Specs

- [SPEC-257](../../../spec/Active/(SPEC-257)-Consolidate-swain-init-inline-bash-into-a-single-preflight-script/(SPEC-257)-Consolidate-swain-init-inline-bash-into-a-single-preflight-script.md) — swain-do completion chain (BDD → smoke → retro)
- [SPEC-258](../../../spec/Active/(SPEC-258)-Swain-Teardown-Completion-Guardrail/(SPEC-258)-Swain-Teardown-Completion-Guardrail.md) — swain-teardown completion guardrail (verify & invoke)

## Key Dependencies

- [DESIGN-018](../../../design/Active/(DESIGN-018)-Completion-Pipeline-State-Tracking/(DESIGN-018)-Completion-Pipeline-State-Tracking.md) — state tracking contract
- swain-test skill (SPEC-220/221) — BDD test gate
- swain-retro skill — already works

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | 683a04e6 | Initial creation — operator requested |
