---
title: "Pre-Commit Hook Setup in swain-init"
artifact: SPEC-023
status: Complete
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
implementation-commits:
  - c70bfb0
type: feature
parent-epic: EPIC-012
linked-artifacts:
  - SPIKE-015
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: "github:cristoslc/swain#24"
swain-do: required
---

# Pre-Commit Hook Setup in swain-init

## Problem Statement

swain currently has no mechanism to enforce security scanning before commits. SPIKE-015 identified gitleaks as the default scanner with TruffleHog, Trivy, and OSV-Scanner as opt-in alternatives. swain-init should configure pre-commit hooks during project onboarding so secrets and vulnerabilities are caught before they reach git history.

## External Behavior

When `swain-init` runs (or when invoked explicitly), it:

1. Checks if a `.pre-commit-config.yaml` already exists
   - If yes: presents the existing config and asks the user whether to merge swain's scanners or leave it unchanged
   - If no: creates `.pre-commit-config.yaml` with gitleaks enabled by default
2. Checks if `pre-commit` framework is installed; if not, installs it via `uv tool install pre-commit` (or warns if uv is unavailable)
3. Runs `pre-commit install` to register the git hook
4. Writes scanner configuration to `swain.settings.json` under `sync.scanners`:
   ```json
   {
     "sync": {
       "scanners": {
         "gitleaks": { "enabled": true },
         "trufflehog": { "enabled": false },
         "trivy": { "enabled": false, "scanners": ["vuln", "license"], "severity": "HIGH,CRITICAL" },
         "osv-scanner": { "enabled": false }
       }
     }
   }
   ```

### Scanner adapter

Each scanner is represented by an adapter with:
- `check_installed()` — verify binary availability
- `get_pre_commit_hook()` — return the YAML block for `.pre-commit-config.yaml`
- `get_default_config()` — return the default `swain.settings.json` entry

### Enabling optional scanners

Users can enable opt-in scanners via:
```
/swain-init --scanner trufflehog --scanner trivy
```
Or by editing `swain.settings.json` directly and re-running `/swain-init`.

## Acceptance Criteria

- **Given** a fresh project with no `.pre-commit-config.yaml`, **when** swain-init runs, **then** it creates the config with gitleaks hook and installs the pre-commit framework
- **Given** an existing `.pre-commit-config.yaml`, **when** swain-init runs, **then** it presents the existing config and asks before modifying (does not silently overwrite)
- **Given** `pre-commit` is not installed, **when** swain-init runs, **then** it installs via `uv tool install pre-commit` or warns if uv is unavailable
- **Given** optional scanners are requested via `--scanner` flag, **when** swain-init runs, **then** those scanners are added to `.pre-commit-config.yaml` and enabled in `swain.settings.json`
- **Given** the scanner configuration in `swain.settings.json`, **when** a scanner is disabled, **then** its hook is not included in `.pre-commit-config.yaml`

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Only configures hooks; does not run scans (that's SPEC-024's job)
- Respects existing `.pre-commit-config.yaml` — never silently overwrites
- Scanner binaries are NOT installed by swain-init (user responsibility); swain-init only configures the hooks
- Uses `uv` for pre-commit installation per project convention (no pip)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-13 | 8ec761d | Initial creation |
| Complete | 2026-03-13 | PENDING | Phase 3 added to swain-init, scanner settings in swain.settings.json |
