---
title: "Worktree Path Link Safety on Merge"
artifact: EPIC-051
track: container
status: Complete
author: cristos
created: 2026-03-31
last-updated: 2026-03-31
parent-vision: VISION-002
parent-initiative: INITIATIVE-013
priority-weight: high
success-criteria:
  - A script deterministically identifies suspicious worktree-specific relative path links in any file set
  - Detected links are resolved to correct repo-relative equivalents before or during merge
  - The worktree completion workflow runs detection and resolution automatically — no manual step required
  - A linked DESIGN documents the detection algorithm, resolution strategy, and integration contract
depends-on-artifacts: []
addresses: []
evidence-pool: ""
---

# Worktree Path Link Safety on Merge

## Goal / Objective

When an agent completes work in a worktree and merges back to trunk, files committed in the worktree may contain relative path links that were valid in the worktree context but break in the main repo. This epic adds deterministic detection and auto-resolution of such links as a gate in the worktree completion workflow.

## Desired Outcomes

Operators and agents can trust that a merged worktree branch leaves no broken path artifacts on trunk. Relative links in docs, skill files, and scripts always resolve correctly regardless of where the worktree was mounted. The detection script gives any agent or operator a fast, deterministic way to audit a file set for suspicious links before committing.

## Scope Boundaries

**In scope:**
- Relative symlinks that resolve differently depending on worktree base path
- Markdown relative links (`[text](../path)`) that embed worktree-specific depth assumptions
- Absolute paths baked into committed files (hardcoded `/tmp/worktree-*` or similar)
- Integration into the worktree completion step (`finishing-a-development-branch` / `swain-sync`)

**Out of scope:**
- Link validation for files outside the repo (external URLs, docs sites)
- Real-time link checking during worktree work (lint-as-you-edit)
- Rewriting links in binary files

## Child Specs

- [SPEC-216](../../../spec/Complete/(SPEC-216)-Worktree-Relative-Link-Detection-Script/(SPEC-216)-Worktree-Relative-Link-Detection-Script.md) — Worktree-Relative Link Detection Script
- [SPEC-217](../../../spec/Complete/(SPEC-217)-Worktree-Link-Resolution-on-Merge/(SPEC-217)-Worktree-Link-Resolution-on-Merge.md) — Worktree Link Resolution on Merge
- [SPEC-218](../../../spec/Complete/(SPEC-218)-Link-Safety-Worktree-Completion-Integration/(SPEC-218)-Link-Safety-Worktree-Completion-Integration.md) — Link Safety Worktree Completion Integration

## Key Dependencies

- [ADR-011](../../../adr/Active/(ADR-011)-Worktree-Landing-Via-Merge-With-Retry.md) defines the current merge workflow; the integration spec hooks into this step
- [DESIGN-007](../../../design/Active/(DESIGN-007)-Worktree-Path-Link-Detection-and-Resolution/(DESIGN-007)-Worktree-Path-Link-Detection-and-Resolution.md) — System design for the detection and resolution contract

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | — | Initial creation |
| Complete | 2026-03-31 | — | All tests passing; EPIC-051 work done; All 3 child SPECs complete; 38 tests passing; integrated into swain-sync and finishing-a-development-branch |
