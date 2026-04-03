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
  - ADR-027
depends-on-artifacts: []
addresses:
  - ADR-027
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Flat artifact migration

## Problem Statement

SPEC-226 writes `verification-log.md` into artifact folders. Flat artifact files have no folder to receive the log. This is not just a swain-source-repo problem — any consumer project using swain could have flat artifacts from older sessions or non-compliant creation. If `swain-test` encounters a flat artifact when trying to record evidence, it must not fail silently and must surface the issue so the project owner can fix it.

There is one known flat file in this repo (`SPEC-183`). But the enforcement and detection mechanism must work in any consumer project.

## Desired Outcomes

1. `swain-doctor` detects flat artifact files in any project it runs against, reports them, and optionally migrates them.
2. The known flat file in this repo (`SPEC-183`) is migrated.
3. The swain-design creation workflow explicitly enforces folder structure so new flat files cannot be created.

## External Behavior

**swain-doctor flat-artifact check (new check, runs in any consumer project):**

```bash
find docs/spec docs/epic -maxdepth 3 -name "*.md" | grep -v '/(' | grep -v "list-"
```

If output is non-empty, doctor reports:

```
WARN: flat artifact files detected — these cannot receive verification-log.md entries:
  docs/spec/Active/SPEC-183-worktree-merge-locally-checkout-fails.md
Run swain-doctor --fix-flat-artifacts to migrate, or migrate manually.
```

**swain-doctor --fix-flat-artifacts (auto-migration):**

For each flat file found:
1. Derive the canonical folder name: parse the artifact ID and title from the filename or frontmatter, normalize to `(TYPE-NNN)-Title/`.
2. `mkdir -p` the folder.
3. `git mv` the file into the folder with the canonical filename.
4. Report the rename; do not commit — leave staging to the operator or swain-sync.

**In this repo — known flat file migration:**
- `docs/spec/Active/SPEC-183-worktree-merge-locally-checkout-fails.md` → `docs/spec/Active/(SPEC-183)-Worktree-Merge-Locally-Checkout-Fails/(SPEC-183)-Worktree-Merge-Locally-Checkout-Fails.md`
- Update cross-references (run specwatch after move to detect broken links).
- Commit.

**Template enforcement (swain-design):**
Add an explicit note to the SPEC and EPIC creation steps in `swain-design/SKILL.md`:

> Artifact folders must always be created as `(TYPE-NNN)-Title/` directories. Flat files are not permitted — SPEC-226 requires a folder to write `verification-log.md`. If `mkdir -p` is not called before writing the file, the artifact is malformed.

## Acceptance Criteria

**Given** a consumer project has a flat artifact file at `docs/spec/Active/SPEC-NNN-title.md`,
**When** `swain-doctor` runs,
**Then** it reports the flat file as a WARN with the path and instructions to fix.

**Given** `swain-doctor --fix-flat-artifacts` runs in a project with flat files,
**When** it completes,
**Then** each flat file is moved into a `(TYPE-NNN)-Title/` folder via `git mv`, leaving the rename staged but not committed.

**Given** SPEC-183 is a flat file at `docs/spec/Active/SPEC-183-*.md` in this repo,
**When** migration runs,
**Then** the file is at `docs/spec/Active/(SPEC-183)-Worktree-Merge-Locally-Checkout-Fails/(SPEC-183)-Worktree-Merge-Locally-Checkout-Fails.md` and git history preserves the rename.

**Given** the doctor check runs after migration in this repo,
**When** output is inspected,
**Then** no flat spec or epic markdown files are found.

**Given** a new spec is created via swain-design,
**When** the folder is created,
**Then** it follows `(SPEC-NNN)-Title/` naming with the primary file inside it.

## Scope & Constraints

- The `--fix-flat-artifacts` flag stages changes but does not commit — the operator or swain-sync handles the commit.
- Per [ADR-027](../../adr/Active/(ADR-027)-All-Artifacts-Must-Be-Foldered/(ADR-027)-All-Artifacts-Must-Be-Foldered.md), all artifact types must be foldered. Doctor's flat-file detection must scan all artifact directories, not just spec and epic.
- This spec does not create or modify verification logs — it only ensures the infrastructure for [SPEC-226](../Active/(SPEC-226)-Verification-Evidence-Recording/(SPEC-226)-Verification-Evidence-Recording.md) exists in any project.
- If additional flat files are discovered during migration, migrate them as part of this spec.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | — | Initial creation |
