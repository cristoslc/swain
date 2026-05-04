---
title: "Dual version display — show release and skill versions together"
artifact: SPEC-287
track: implementable
status: Active
author: Cristos L-C
created: 2026-04-06
last-updated: 2026-04-06
priority-weight: medium
type: enhancement
parent-epic: ""
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Dual version display — show release and skill versions together

## Problem Statement

Swain has two independent version schemes: the **release version** from git tags (e.g., `v0.29.0-alpha`) and **skill versions** in SKILL.md frontmatter (e.g., `4.0.0`). Users only see skill versions in init messages and update reports, while releases use git tag versions. This creates confusion — "why is the release 0.x but init thinks it's 4.0.0?"

## Desired Outcomes

Operators see both versions in context whenever swain reports version info. The relationship is clear: the release version identifies the swain package; the skill version identifies the internal contract. No more "which version am I on?" confusion.

## External Behavior

**Inputs:** Git tags (`git tag --sort=-v:refname`), SKILL.md frontmatter `version:` fields, `.swain-init` marker file.

**Outputs — changed user-facing messages:**

| Location | Current | New |
|---|---|---|
| swain-init Phase 0 delegate | `Project already initialized (swain 4.0.0).` | `Project already initialized (swain v0.29.0-alpha, init v4.0.0).` |
| swain-init Phase 0 upgrade | `Project was initialized with swain 4.0.0 (current: 4.0.0).` | `Project was initialized with swain v0.28.0-alpha (init v3.0.0). Current: v0.29.0-alpha (init v4.0.0).` |
| swain-update report | Skill list only | Release version header line before skill list. |
| .swain-init marker | `{"version": "4.0.0", ...}` | `{"version": "4.0.0", "release": "v0.29.0-alpha", ...}` |

**Unchanged:** Shell launchers (internal routing only), swain-release (already works with git tags directly).

**Preconditions:** At least one git tag matching a semver pattern must exist. If no tags exist, fall back to `(unreleased)` for the release version.

## Acceptance Criteria

- **AC1:** Given a project with git tag `v0.29.0-alpha` and swain-init SKILL.md version `4.0.0`, when swain-init runs on an already-initialized project (delegate path), then the message includes both `v0.29.0-alpha` and `init v4.0.0`.
- **AC2:** Given a `.swain-init` marker with `"release": "v0.28.0-alpha"` and current git tag `v0.29.0-alpha`, when swain-init detects an upgrade, then the message shows old and new release versions alongside old and new skill versions.
- **AC3:** Given a fresh init, when the `.swain-init` marker is written, then the history entry includes a `"release"` field with the current git tag.
- **AC4:** Given swain-update completes, when the report is displayed, then a release version line appears above the skill version list.
- **AC5:** Given no git tags exist, when any version display fires, then the release version shows as `(unreleased)` and the skill version still displays normally.
- **AC6:** The `swain-init-preflight.sh` script outputs a `marker.release_version` field in its JSON.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Do NOT change shell launcher version-comparison logic — launchers route on major skill version, not release version. Adding release version there adds complexity for no user benefit.
- Do NOT change swain-release — it already uses git tags as its source of truth.
- The release version is read-only context derived from `git tag`; it is never bumped by this spec.
- Backward compatible: old `.swain-init` markers without a `"release"` field display the release field as `(unknown)` until next init/upgrade writes it.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | | Initial creation — design explored in conversation. |
