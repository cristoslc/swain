---
title: "Pre-Commit Security Scanner Landscape"
artifact: SPIKE-015
status: Planned
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
question: "Which pre-commit security scanners should swain support beyond gitleaks, and what configuration surface do they need?"
gate: Pre-MVP
risks-addressed:
  - Secrets accidentally committed to repositories
  - Incomplete coverage with a single scanner
depends-on: []
evidence-pool: ""
---

# Pre-Commit Security Scanner Landscape

## Question

Which pre-commit security scanners should swain support beyond gitleaks, and what configuration surface do they need?

## Go / No-Go Criteria

- **GO:** At least 2 additional scanners identified that cover gaps gitleaks misses (e.g., cloud-specific credential patterns, license compliance, dependency vulnerabilities)
- **NO-GO:** All additional scanners have >80% overlap with gitleaks — stick with gitleaks-only default

## Pivot Recommendation

If no additional scanners add meaningful coverage, simplify the architecture: hardcode gitleaks support in swain-push instead of building a configurable scanner list. Save the abstraction for when there's a real second scanner to support.

## Findings

(Populated during Active phase)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-13 | — | Initial creation |
