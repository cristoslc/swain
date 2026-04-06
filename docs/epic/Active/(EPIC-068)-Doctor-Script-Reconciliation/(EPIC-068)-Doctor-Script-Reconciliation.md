---
title: "Doctor Script Reconciliation"
artifact: EPIC-068
track: container
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
parent-vision: VISION-002
parent-initiative: INITIATIVE-003
success-criteria:
  - swain-doctor.sh is the single authority for all detection checks.
  - SKILL.md is a remediation-only lookup table keyed by check name — no inline detection logic.
  - Every check in swain-doctor.sh has a corresponding remediation entry in SKILL.md and vice versa.
  - Branch model check fires from the script, not from swain-init.
  - Two SPIKEs complete with Go/No-Go verdicts on script simplification and Python migration.
depends-on-artifacts: []
addresses: []
---

# Doctor Script Reconciliation

## Goal / Objective

Eliminate the drift between `swain-doctor.sh` (1,100+ lines of bash) and `swain-doctor/SKILL.md`. The script is authoritative for detection; the SKILL.md should be a remediation lookup table, not a parallel implementation. Then investigate whether the script itself can be simplified or rewritten in Python.

## Desired Outcomes

Operators get consistent health checks regardless of whether the script runs or the agent falls back to SKILL.md instructions. Agents spend fewer tokens parsing redundant detection logic from SKILL.md. Future maintainers have one place to add checks (the script) and one place to document remediation (the SKILL.md).

## Scope Boundaries

**In scope:**
- Reconcile SKILL.md ↔ script drift (both directions).
- Move the branch model recommendation from swain-init to swain-doctor.
- Add missing script functions for SKILL.md-only checks (platform dotfolders, gitignore hygiene, branch model).
- Add missing SKILL.md remediation entries for script-only checks.
- SPIKE: evaluate simplification of the bash script.
- SPIKE: evaluate Python rewrite via uv.

**Out of scope:**
- Changing what the checks do (no new health checks beyond branch model).
- Modifying swain-preflight.sh (that's a separate concern).
- Rewriting the script in this EPIC — that would follow from the SPIKEs if Go.

## Child Specs

- [SPEC-288](../../spec/Active/(SPEC-288)-Reconcile-Doctor-Script-And-Skill/(SPEC-288)-Reconcile-Doctor-Script-And-Skill.md) — reconcile script ↔ SKILL.md drift.
- [SPIKE-061](../../research/Active/(SPIKE-061)-Doctor-Script-Simplification/(SPIKE-061)-Doctor-Script-Simplification.md) — can we simplify the 1,100-line bash script?
- [SPIKE-062](../../research/Active/(SPIKE-062)-Doctor-Python-Migration/(SPIKE-062)-Doctor-Python-Migration.md) — should we rewrite doctor in Python via uv?

## Key Dependencies

SPEC-288 must complete before either SPIKE can begin (they need a stable, reconciled baseline).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | _pending_ | Created from session — branch model move already in progress. |
