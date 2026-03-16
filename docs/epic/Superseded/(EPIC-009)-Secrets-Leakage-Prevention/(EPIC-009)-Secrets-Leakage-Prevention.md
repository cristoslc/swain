---
title: "Secrets Leakage Prevention"
artifact: EPIC-009
track: container
status: Superseded
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
parent-vision: VISION-001
parent-initiative: INITIATIVE-004
success-criteria:
  - swain-init sets up pre-commit hooks with configurable scanner list (default: gitleaks)
  - swain-push verifies pre-commit hooks ran successfully before committing
  - Existing pre-commit configurations are preserved (swain discusses changes with user)
  - Scanner list is configurable via swain.settings.json
  - Clear error messages when scanners detect secrets, with remediation guidance
addresses: []
trove: ""
source-issue: "github:cristoslc/swain#24"
linked-artifacts: []
depends-on-artifacts: []
---

# Secrets Leakage Prevention

## Goal / Objective

Prevent secrets and credentials from being accidentally committed to repositories managed by swain. The approach uses pre-commit hooks as the enforcement layer, with a configurable scanner list that defaults to gitleaks. swain-init handles setup, swain-push verifies hooks ran, and the scanner list is extensible.

### Decided approach

- **swain-init** sets up pre-commit hooks from a configurable scanner list (default: `[gitleaks]`)
- If an existing `.pre-commit-config.yaml` exists, swain discusses with the user before making changes
- **swain-push** verifies that pre-commit hooks ran successfully before proceeding with commit/push
- Scanner list configurable via `swain.settings.json` under `security.scanners`

## Scope Boundaries

**In scope:**
- Pre-commit hook setup in swain-init
- Pre-commit verification in swain-push
- Configurable scanner list with gitleaks default
- Safe handling of existing pre-commit configurations
- SPIKE-015 to survey available scanners beyond gitleaks

**Out of scope:**
- Runtime secret detection (environment variables, logs)
- Secret rotation or management
- CI/CD pipeline scanner integration (that's the CI system's concern)

## Child Specs

- SPIKE-015: Pre-Commit Security Scanner Landscape (research which scanners to support)
- SPEC: swain-init pre-commit hook setup (depends on SPIKE-015)
- SPEC: swain-push pre-commit verification

## Key Dependencies

- SPIKE-015 informs the scanner list configuration

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-13 | 7b39e3e | Initial creation from GitHub #24 decision |
| Superseded | 2026-03-13 | 34f2d62 | Superseded by EPIC-012 (End-to-End Sync Workflow) |
