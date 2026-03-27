---
title: "Progressive disclosure cleanup"
artifact: SPEC-079
track: implementable
status: Active
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
type: enhancement
parent-epic: EPIC-031
linked-artifacts: []
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Progressive disclosure cleanup

## Problem Statement

Several skills inline developer-facing API documentation or long procedural sections that inflate the SKILL.md beyond what an agent needs at runtime:

- **swain-security-check:** External hook API (~50% of file, ~90 lines) is developer documentation for skill authors writing security extensions. An agent running a security scan never needs this.
- **swain-session:** Post-operation bookmark protocol (~25 lines) is documentation for other skill authors, not runtime instructions.
- **swain-doctor:** Lifecycle migration detection, worktree detection awk blocks, and epic-parent guided migration (~120 lines) could be references.
- **swain-init:** Pre-commit config YAML blocks for four scanners could be a reference file.
- **swain-sync:** Gitignore check section (46 lines) and index rebuild section could be references.

## External Behavior

SKILL.md files stay under 300 lines of agent-facing instructions. Developer documentation, long procedural blocks, and configuration templates live in `references/` files with clear pointers from the SKILL.md body.

## Acceptance Criteria

**AC-1:** swain-security-check external hook API moved to `references/external-hook-api.md` with a one-line pointer in SKILL.md.

**AC-2:** swain-session post-operation bookmark protocol moved to `references/bookmark-protocol.md`.

**AC-3:** swain-doctor below 350 lines (from 405) by moving lifecycle migration and worktree detection to references.

**AC-4:** Every extracted section has a clear pointer in the SKILL.md body: "Read [references/X.md] for Y."

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC-1 | File exists, SKILL.md has pointer | |
| AC-2 | File exists, SKILL.md has pointer | |
| AC-3 | Line count of swain-doctor SKILL.md | |
| AC-4 | Grep for reference pointers | |

## Scope & Constraints

**In scope:** Moving existing content to references/ files. Adding pointers. No content changes.

**Out of scope:** Rewriting the extracted content. Changing skill behavior.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | — | Created from audit theme #6: inline API docs |
