---
title: "Fix swain-update functional bugs"
artifact: SPEC-076
track: implementable
status: Active
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
type: bug
parent-epic: EPIC-031
linked-artifacts: []
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Fix swain-update functional bugs

## Problem Statement

Two high-severity bugs in swain-update:

1. **Unrunnable placeholder:** `SKILL_DIR` is used as a literal string in bash code blocks. The agent is told to "replace" it but no runtime discovery mechanism is provided. Other skills use `find` — this one uses pseudocode.

2. **Wrong install location:** The git-clone fallback copies to `.claude/skills/` only (`cp -r "$tmp/swain/skills/"* .claude/skills/`). If the project uses `.agents/skills/`, the fallback installs to the wrong location.

## Acceptance Criteria

**AC-1:** All bash code blocks use a runtime-discoverable path (via `find` or `$REPO_ROOT`) instead of the `SKILL_DIR` placeholder.

**AC-2:** The git-clone fallback detects the actual skill installation directory (`.claude/skills/` or `.agents/skills/` or `skills/`) and copies there.

**AC-3:** `allowed-tools` is trimmed to tools actually used in the skill text (`Bash` primarily).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC-1 | Grep for SKILL_DIR in swain-update SKILL.md | |
| AC-2 | Review fallback install logic | |
| AC-3 | Compare allowed-tools vs. actual tool usage | |

## Scope & Constraints

**In scope:** `skills/swain-update/SKILL.md` only.

**Out of scope:** Changing the npx primary path. Offline fallback for modified-file detection (medium severity — acceptable for now).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | — | Two high-severity bugs from audit |
