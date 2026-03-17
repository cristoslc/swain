---
title: "Security Gates in swain-do Execution Flow"
artifact: EPIC-023
track: container
status: Active
author: cristos
created: 2026-03-14
last-updated: 2026-03-17
parent-vision: VISION-001
parent-initiative: INITIATIVE-004
success-criteria:
  - Security guidance is surfaced proactively during task claim — before implementation begins, not only at review time
  - A security gate runs at task completion as part of swain-do's landing-the-plane workflow, equivalent to how tests and lints are run today
  - The gates are lightweight by default and escalate to heavier tooling (EPIC-017 / swain-security-check) only when the task touches a security-sensitive surface
  - Threat surface detection is automated — swain-do infers whether a task is security-relevant from its title, tags, and parent SPEC's acceptance criteria
  - External skill integration points (Trail of Bits differential-review, agamm/owasp-security) are defined as optional hooks, not hard dependencies
  - The execution flow gates do not block tasks that have no security surface — detection must have a low false-positive rate
  - Security findings at task completion are filed as new tk issues, not silently dropped
linked-artifacts:
  - SPIKE-020
depends-on-artifacts:
  - EPIC-017
trove: "security-skill-landscape"
addresses: []
---

# Security Gates in swain-do Execution Flow

## Goal / Objective

Embed security checkpoints directly into the swain-do task lifecycle so that security is a first-class concern during implementation, not only an afterthought at review time.

EPIC-017 (`swain-security-check`) defines a standalone security scanning skill that can be invoked on demand. This Epic is complementary and orthogonal: it defines **when and how security checks are wired into the task execution loop** — the `tk claim` → implement → `tk close` workflow that agents follow when working on SPECs.

The three integration points are:

1. **Pre-implementation (task claim):** When an agent claims a task, swain-do detects whether the task touches a security-sensitive surface (auth, input handling, crypto, external data, agent context files, dependency changes). If so, it surfaces the relevant OWASP/swain-security guidance proactively, before any code is written.

2. **During implementation:** For tasks flagged as security-sensitive, swain-do activates an always-on security co-pilot mode — similar to how `test-driven-development` activates for all implementation tasks, but scoped to security-relevant tasks only. This may invoke `owasp-security` skill guidance or Trail of Bits `sharp-edges`/`insecure-defaults` as optional hooks.

3. **At completion (landing the plane):** Before closing a task, swain-do runs a lightweight security gate. For security-sensitive tasks, this escalates to invoking `swain-security-check` (EPIC-017) in diff-only mode (analogous to how `differential-review` works in the Trail of Bits skill suite). Findings are filed as new tk issues rather than blocking the close.

## Scope Boundaries

**In scope:**
- Threat surface detection heuristic — classifies tasks as security-sensitive based on title, tags, SPEC acceptance criteria keywords, and file paths touched
- Pre-claim security briefing for security-sensitive tasks (surfacing relevant OWASP categories or swain guidance)
- Post-implementation security gate hook in swain-do's completion workflow
- Integration interface for external skill hooks (Trail of Bits `differential-review`, `agamm/owasp-security`) as optional, additive steps
- Automatic tk issue filing for security findings found at task close
- Documentation of which swain-do workflow phases are extended and how

**Out of scope:**
- The security scanning skill itself (EPIC-017 owns `swain-security-check`)
- Runtime prompt injection interception
- Pulling in or vendoring Trail of Bits or OWASP skills — integration points are defined but the skills remain external
- Full SAST / CodeQL integration (that belongs in EPIC-017)
- Changing the tk data model (findings create new tickets, not new fields)

## Design Notes

### Why this is distinct from EPIC-017

EPIC-017 answers: *"What does a security scan look like when explicitly invoked?"*
This Epic answers: *"When should security thinking automatically enter the flow, and what's the minimum viable gate?"*

The analogy in swain's existing flow: `test-driven-development` skill activates automatically for implementation tasks. This Epic creates the equivalent for security — an automatic activation that doesn't require the operator or agent to remember to ask for a security review.

### Skill integration model

The Trail of Bits `trailofbits/skills` marketplace and `agamm/claude-code-owasp` are the two most relevant external skills identified in the evidence pool:

- **Trail of Bits `differential-review`** — best fit for the completion gate (reviews changed files with git history context)
- **Trail of Bits `sharp-edges` + `insecure-defaults`** — best fit for the pre-implementation briefing (flags dangerous APIs/configs in the codebase being modified)
- **agamm/owasp-security** — best fit for the during-implementation co-pilot (20+ language quirks, ASVS 5.0, Agentic AI ASI01-ASI10 risks)

These are integrated as optional hooks — if the skills are not installed, swain-do falls back to built-in guidance from the swain-security context.

## Child Specs

Updated as the threat surface detection algorithm and each lifecycle hook are specced out.

Likely decomposition:
- SPEC: Threat surface detection heuristic for task classification
- SPEC: Pre-claim security briefing injection
- SPEC: Post-implementation security gate hook and finding-to-ticket flow
- SPEC: External skill hook interface (Trail of Bits / owasp-security integration points)

## Key Dependencies

- **EPIC-017** (`swain-security-check`) — the completion gate escalates to EPIC-017's scanner for security-sensitive tasks; EPIC-017 should reach at least Proposed→Active before this Epic's completion-gate SPEC is implemented
- **evidence-pool: security-skill-landscape** — research grounding for the external skill integration design
- **SPIKE-020** (Complete) — security scanning landscape; findings inform the threat surface heuristic

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial filing; depends on EPIC-017 for completion-gate implementation |
| Active | 2026-03-17 | -- | EPIC-017 now Active; ready for child spec decomposition |
