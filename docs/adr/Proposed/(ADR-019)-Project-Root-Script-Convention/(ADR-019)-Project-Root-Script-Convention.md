---
title: "Project-Root Script Convention"
artifact: ADR-019
track: standing
status: Proposed
author: cristos
created: 2026-03-28
last-updated: 2026-03-28
linked-artifacts:
  - SPEC-067
  - SPEC-180
  - SPEC-181
depends-on-artifacts: []
evidence-pool: ""
---

# Project-Root Script Convention

## Context

Swain ships operator-facing scripts that need to be runnable from the project root (e.g., `./swain-box`, `./swain`). These scripts are versioned inside the skill tree and evolve with swain releases. The first instance of this pattern — `swain-box` (SPEC-067) — established an ad-hoc convention: script lives at `skills/swain/scripts/swain-box`, swain-doctor creates a root symlink, and the doctor checks symlink health on every session.

With the `swain` pre-runtime script (SPEC-180) following the same pattern, we need to codify the convention so future project-root scripts are consistent and discoverable.

## Decision

All operator-facing scripts that run from the project root follow a three-part convention:

### 1. Canonical location

The script lives inside the skill tree at:

```
skills/<owning-skill>/scripts/<script-name>
```

For scripts that serve the swain meta-skill (not a specific sub-skill), the location is `skills/swain/scripts/<script-name>`.

The script is executable (`chmod +x`) and committed to the swain repo. Consumer projects receive it via `npx skills add`.

### 2. Root symlink

A symlink at the project root points to the canonical location:

```
./<script-name> -> skills/<owning-skill>/scripts/<script-name>
```

The symlink uses a **relative path** so it works regardless of where the repo is cloned. The symlink is created by either:
- **swain-init** (during onboarding — first-run setup), or
- **swain-doctor** (on subsequent sessions — repair if missing)

### 3. Doctor health check

swain-doctor includes a check for each project-root symlink, using this status model:

| Status | Condition | Action |
|--------|-----------|--------|
| **ok** | Symlink exists and points to the correct target | Silent |
| **missing** | No file at `./script-name` | Auto-create symlink, report "repaired" |
| **stale** | Symlink exists but points to wrong target (e.g., after skill tree restructure) | Auto-repair symlink, report "repaired" |
| **conflict** | A real file (not a symlink) exists at `./script-name` | Warn with manual remediation instructions |

### Naming

Project-root scripts are prefixed with `swain` (e.g., `swain`, `swain-box`) to avoid namespace collisions with other tools. The bare name `swain` is reserved for the primary entry point.

### Gitignore

Root symlinks should be tracked in git for the swain repo itself. In consumer projects, the symlinks are gitignored (vendored skill directories are already gitignored per swain-doctor's skill folder hygiene check; the root symlinks should be added to `.gitignore` alongside them).

## Alternatives Considered

**Script directly in project root.** Simpler, but the script diverges from the vendored version on updates. The symlink ensures the operator always runs the version that shipped with their installed skills.

**Script in `.agents/bin/`.** SPEC-181 mentions this as a fallback search path. Viable, but `.agents/` is a runtime directory (session state, execution tracking), not a distribution directory. Keeping scripts in the skill tree maintains the principle that `npx skills add/update` is the single distribution mechanism.

**No convention — each script decides independently.** The status quo. Works for one script, creates inconsistency at two, becomes confusing at three. The cost of the convention is near zero.

## Consequences

**Positive:**
- Future project-root scripts (e.g., `swain-stage` if it materializes) follow a known pattern with zero design effort.
- swain-doctor's symlink checks are formulaic — each new script adds ~20 lines to the doctor skill using the same detection/remediation template.
- `npx skills update` automatically updates the script content; the symlink doesn't change.

**Accepted downsides:**
- Symlinks can confuse some tools (e.g., some editors resolve symlinks and open the canonical path). This is minor and consistent with standard Unix practice.
- Consumer projects need a `.gitignore` entry per root symlink. swain-doctor can automate this.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-28 | — | Initial creation; codifies pattern established by SPEC-067 (swain-box) |
