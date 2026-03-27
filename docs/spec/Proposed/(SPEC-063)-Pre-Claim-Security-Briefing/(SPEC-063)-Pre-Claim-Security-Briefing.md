---
title: "Pre-Claim Security Briefing"
artifact: SPEC-063
track: implementable
status: Proposed
author: cristos
created: 2026-03-17
last-updated: 2026-03-17
type: feature
parent-epic: EPIC-023
linked-artifacts:
  - SPEC-062
  - SPEC-065
depends-on-artifacts:
  - SPEC-062
addresses: []
trove: "security-skill-landscape"
source-issue: ""
swain-do: required
---

# Pre-Claim Security Briefing

## Problem Statement

When an agent claims a security-sensitive task, it should receive relevant security guidance *before* writing any code. Currently swain-do's `tk claim` flow has no security awareness — the agent starts implementing immediately. Surfacing OWASP categories, common pitfalls, and swain-specific guidance at claim time reduces the chance of introducing vulnerabilities.

## External Behavior

**Trigger:** After `tk claim <id>`, when the threat surface heuristic (SPEC-062) classifies the task as security-sensitive.

**Behavior:** swain-do emits a security briefing block before the agent begins implementation:

```
Security briefing for task <id> (categories: auth, input-validation):

- OWASP A07:2021 — Identification and Authentication Failures
  - Never store passwords in plaintext; use bcrypt/scrypt/argon2
  - Session tokens must be regenerated on privilege change

- OWASP A03:2021 — Injection
  - Validate and sanitize all user input at system boundaries
  - Use parameterized queries, never string concatenation for SQL

- swain guidance:
  - Agent context files (AGENTS.md, CLAUDE.md) are trust boundaries — do not write user-controlled data into them
```

**Guidance sources (priority order):**
1. Built-in swain security guidance (bundled with the skill)
2. Optional: `agamm/owasp-security` skill if installed
3. Optional: Trail of Bits `sharp-edges` / `insecure-defaults` if installed

## Acceptance Criteria

- Given a task classified as `auth`-sensitive, when claimed, then OWASP authentication guidance is surfaced
- Given a task classified as `input-validation`-sensitive, when claimed, then OWASP injection guidance is surfaced
- Given a task classified as `agent-context`-sensitive, when claimed, then swain-specific agent trust boundary guidance is surfaced
- Given a non-security-sensitive task, when claimed, then no security briefing is emitted
- Built-in guidance works with zero external skill installs

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Advisory only — briefing does not block task execution
- Built-in guidance covers OWASP Top 10 2021 categories mapped to the detection heuristic categories
- External skill integration is additive, not required
- Guidance content is static (bundled reference data), not dynamically generated

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | b32f7db | Decomposed from EPIC-023 |
