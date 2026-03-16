---
title: "End-to-End Sync Workflow"
artifact: EPIC-012
track: container
status: Complete
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
parent-vision: VISION-001
parent-initiative: INITIATIVE-004
success-criteria:
  - swain-push renamed to swain-sync with full fetch/pull-first behavior
  - swain-push skill remains as alias that redirects with deprecation warning
  - swain-init sets up pre-commit hooks with configurable scanner list (default: gitleaks)
  - swain-sync verifies pre-commit hooks ran before committing
  - Existing pre-commit configurations preserved (swain discusses with user before changes)
  - Scanner list configurable via swain.settings.json
  - Migration path documented and enforced by swain-doctor
  - History cleanliness enforced (rebase strategy, clean commits)
addresses: []
trove: ""
source-issue: "github:cristoslc/swain#24"
linked-artifacts:
  - EPIC-009
  - SPEC-013
  - SPEC-023
  - SPEC-024
  - SPIKE-015
  - SPIKE-017

depends-on-artifacts: []
---

# End-to-End Sync Workflow

## Goal / Objective

Replace swain-push with swain-sync — a comprehensive sync skill that handles the full fetch → pull/rebase → scan → commit → push workflow. This absorbs the security scanning concerns from EPIC-009 (Superseded) and adds workflow robustness: always incorporating upstream changes before pushing, enforcing security hygiene, and maintaining clean git history.

### Key behaviors

1. **Fetch/pull first** — always incorporate changes from main/upstream before committing
2. **Security scanning** — pre-commit hooks with configurable scanner list (default: gitleaks), verified before commit
3. **History cleanliness** — rebase strategy, clean commit messages, conflict resolution
4. **Safe pre-commit setup** — swain-init configures hooks; if existing `.pre-commit-config.yaml` exists, discuss with user before modifying
5. **Backward compatibility** — swain-push skill remains as an alias that redirects to swain-sync with a deprecation warning

### Migration path (breaking change)

- swain-push skill file becomes a thin redirector that invokes swain-sync and emits a deprecation warning
- swain-doctor detects old swain-push references in CLAUDE.md/AGENTS.md and suggests updating
- swain router updated to route both `/swain-push` and `/swain-sync`
- AGENTS.md updated to reference swain-sync as the canonical skill

## Scope Boundaries

**In scope:**
- Rename swain-push → swain-sync with alias/deprecation
- Fetch/pull-first behavior in swain-sync
- Pre-commit hook setup in swain-init (absorbed from EPIC-009)
- Pre-commit verification in swain-sync (absorbed from EPIC-009)
- Configurable scanner list with gitleaks default (absorbed from EPIC-009)
- SPIKE-017 to research additional workflow habits worth incorporating
- SPIKE-015 to survey security scanners (reattached from EPIC-009)
- Migration path via swain-doctor

**Out of scope:**
- Runtime secret detection (environment variables, logs)
- Secret rotation or management
- CI/CD pipeline integration

## Child Specs

- SPIKE-015: Pre-Commit Security Scanner Landscape (Complete)
- SPIKE-017: Sync Workflow Best Practices (Complete)
- SPEC-013: Fetch/Pull-First Sync Behavior (Complete — core rename + fetch-first)
- SPEC-023: Pre-Commit Hook Setup in swain-init (Proposed — depends on SPIKE-015)
- SPEC-024: Pre-Commit Verification in swain-sync (Proposed — depends on SPEC-023)

## Key Dependencies

- SPIKE-015 informs the scanner list configuration
- SPIKE-017 may surface additional workflow habits to incorporate

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-13 | 34f2d62 | Initial creation; supersedes EPIC-009 |
| Active | 2026-03-13 | 96acb43 | SPEC-013 completed |
| Complete | 2026-03-13 | 0e54e5e | All child specs complete, all success criteria met |
