---
title: "Flat artifact migration"
artifact: SPEC-225
track: implementable
status: Active
author: operator
created: 2026-03-31
last-updated: 2026-03-31
priority-weight: medium
type: enhancement
parent-epic: EPIC-052
parent-initiative: ""
linked-artifacts:
  - EPIC-052
  - SPEC-226
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Flat artifact migration

## Problem Statement

SPEC-226 writes `verification-log.md` into artifact folders. One artifact is a flat file: `docs/spec/Active/SPEC-183-worktree-merge-locally-checkout-fails.md`. If it remains flat, it has no folder to receive its verification log. Additionally, spec templates must enforce folder creation going forward to prevent new flat files.

## Desired Outcomes

All existing artifact flat files are converted to folder-based layout. The swain-design spec creation workflow enforces folder creation for all new artifacts.

## External Behavior

**Known flat files:**
- `docs/spec/Active/SPEC-183-worktree-merge-locally-checkout-fails.md` → `docs/spec/Active/(SPEC-183)-Worktree-Merge-Locally-Checkout-Fails/(SPEC-183)-Worktree-Merge-Locally-Checkout-Fails.md`

**Migration steps for each flat file:**
1. Create the folder: `mkdir -p "docs/spec/Active/(SPEC-183)-Worktree-Merge-Locally-Checkout-Fails/"`
2. Move the file: `git mv "docs/spec/Active/SPEC-183-worktree-merge-locally-checkout-fails.md" "docs/spec/Active/(SPEC-183)-Worktree-Merge-Locally-Checkout-Fails/(SPEC-183)-Worktree-Merge-Locally-Checkout-Fails.md"`
3. Update any cross-references pointing to the old path (run specwatch to detect them).
4. Commit.

**Template enforcement:**
The swain-design SKILL.md already instructs agents to create the folder with `mkdir -p` before writing the artifact file. This spec confirms that instruction is being followed and adds an explicit note:

> Spec and Epic folders must always be created as `(TYPE-NNN)-Title/` directories containing the primary markdown file. Flat files are not permitted — SPEC-226 requires a folder to write `verification-log.md`.

**swain-doctor check:**
After migration, verify no flat spec or epic files remain:
```bash
find docs/spec docs/epic -maxdepth 3 -name "*.md" | grep -v '/(' | grep -v "list-"
```
This command should return no output if all artifacts are foldered.

## Acceptance Criteria

**Given** SPEC-183 is a flat file at `docs/spec/Active/SPEC-183-*.md`,
**When** migration runs,
**Then** the file is at `docs/spec/Active/(SPEC-183)-Worktree-Merge-Locally-Checkout-Fails/(SPEC-183)-Worktree-Merge-Locally-Checkout-Fails.md` and git history preserves the rename.

**Given** cross-references point to the old flat path,
**When** specwatch scans after migration,
**Then** no broken references are reported for SPEC-183.

**Given** the doctor check command runs after migration,
**When** output is inspected,
**Then** no flat spec or epic markdown files are found.

**Given** a new spec is created via swain-design after this spec completes,
**When** the folder is created,
**Then** it follows `(SPEC-NNN)-Title/` naming and the primary file is inside it.

## Scope & Constraints

- Only spec and epic artifact types are known to have flat files. Other types (ADR, initiative, vision, etc.) are already fully foldered.
- This spec does not create or modify any verification logs — it only ensures the infrastructure for SPEC-226 is in place.
- If additional flat files are discovered during migration, migrate them as part of this spec.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | — | Initial creation |
