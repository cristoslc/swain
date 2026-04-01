---
title: "Doctor Warn-Only Check Auto-Repair Audit"
artifact: SPEC-222
track: implementable
status: Complete
author: cristos
created: 2026-03-31
last-updated: 2026-03-31
priority-weight: medium
type: enhancement
parent-epic: ""
parent-initiative: ""
linked-artifacts:
  - SPEC-214
  - SPEC-186
  - SPEC-188
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Doctor Warn-Only Check Auto-Repair Audit

## Problem Statement

swain-doctor has a two-tier pattern: checks that auto-repair (Check 20 `.agents/bin/` symlinks, now Check 15 operator `bin/` symlinks via [SPEC-214](../../../spec/Complete/(SPEC-214)-Operator-Bin-Symlink-Auto-Repair/(SPEC-214)-Operator-Bin-Symlink-Auto-Repair.md)) and checks that only warn. The warn-only tier is appropriate when repair is destructive, ambiguous, or requires operator input. But some warn-only checks are safe to auto-repair: the fix is deterministic, reversible, and has no side effects on project state. These sit in warn-only mode for no good reason, requiring the operator to manually act on findings that swain-doctor could resolve itself.

Identified in the [SPEC-214](../../../spec/Complete/(SPEC-214)-Operator-Bin-Symlink-Auto-Repair/(SPEC-214)-Operator-Bin-Symlink-Auto-Repair.md) retrospective as a recurring pattern.

## Desired Outcomes

Each warn-only check is evaluated against a repair-safety rubric. Safe candidates are promoted to auto-repair. The audit produces a clear record of which checks were promoted, which were ruled out, and why — so future checks are added with an explicit repair-or-warn decision rather than defaulting to warn.

## External Behavior

**Rubric for safe auto-repair:**
- Repair is idempotent (running it twice produces the same result)
- Repair does not discard operator-authored content
- Repair does not require network access or external credentials
- Repair is reversible (or the non-repaired state was already broken)
- Repair does not mask a deeper problem that the operator should investigate

**Candidates from the current check list:**

| Check | Current | Candidate? | Rationale |
|-------|---------|-----------|-----------|
| `memory_directory` | warn | **yes** | `mkdir -p` — purely additive, no content risk |
| `script_permissions` | warn | **yes** | `chmod +x` on swain-owned scripts — idempotent, no content change |
| `commit_signing` | warn | **maybe** | `git config commit.gpgsign true` + `gpg.format ssh` — local config only; safe if signing key is confirmed present |
| `governance` (stale block) | warn | **maybe** | Update governance block to match canonical — safe if block boundaries are clear, risky if operator has local edits |
| `lifecycle_dirs` | warn | **maybe** | Run `migrate-lifecycle-dirs.py` — deterministic migration, but touches many files |
| `crash_debris` (git locks only) | warn | **maybe** | `.git/index.lock` removal is safe; other debris types (uncommitted changes, dangling worktrees) are not |
| `agents_directory` | warn | **no** | Already creates the dir in Check 20 path; the standalone warning is redundant |
| `tk_health` | warn | **no** | Missing tk binary requires operator to run install |
| `superpowers` | warn | **no** | External install, operator decision |
| `tools` | warn | **no** | System tool installation not in scope |
| `ssh_readiness` | warn | **no** | SSH config is operator-specific |
| `readme` | warn | **no** | Cannot generate a README |
| `worktrees` (stale) | warn | **no** | Removing a stale worktree discards potential work |
| `crash_debris` (uncommitted changes, dangling worktrees) | warn | **no** | Destructive — requires operator confirmation |

**Implementation for promoted candidates:**
Each promoted check follows the same pattern as [SPEC-214](../../../spec/Complete/(SPEC-214)-Operator-Bin-Symlink-Auto-Repair/(SPEC-214)-Operator-Bin-Symlink-Auto-Repair.md): attempt repair, report what was done in the check result, use `advisory` status on success (not `warning`), and use `warning` only for conflicts or unresolvable cases.

## Acceptance Criteria

1. **Given** the `memory_directory` check finds the memory dir missing, **when** doctor runs, **then** the directory is created and the check reports `advisory` with "created".

2. **Given** the `script_permissions` check finds swain-owned scripts without execute permission, **when** doctor runs, **then** `chmod +x` is applied to each and the check reports `advisory` with the count fixed.

3. **Given** `commit_signing` is not configured **and** a valid swain signing key exists at the path configured in git config, **when** doctor runs, **then** `commit.gpgsign=true` and `gpg.format=ssh` are set locally and the check reports `advisory`. If no signing key is detected, the check remains `warning`.

4. **Given** the `governance` block in AGENTS.md differs from the canonical source, **when** doctor runs, **then** the block is updated to match canonical and the check reports `advisory`. If AGENTS.md has no governance block markers at all, the check remains `warning` (cannot determine where to insert).

5. **Given** `crash_debris` detects only `.git/index.lock` (and no other debris types), **when** doctor runs, **then** the lock file is removed and the check reports `advisory`. Other debris types still warn.

6. **Given** all auto-repairs have been applied, **when** doctor runs again, **then** all promoted checks report `ok` (idempotent).

7. **Given** a conflict exists (e.g., `script_permissions` on a non-swain-owned script), **when** doctor runs, **then** a `warning` is emitted and the file is not modified.

8. A decision record exists in this spec's Implementation Approach documenting which candidates were ruled out and why — implementors do not need to re-evaluate the rubric.

## Scope & Constraints

**In scope:**
- `memory_directory` — auto-create
- `script_permissions` — auto-chmod swain-owned scripts only (in `skills/*/scripts/`)
- `commit_signing` — auto-configure if signing key is detectable
- `governance` (stale block) — auto-update block content between markers
- `crash_debris` git lock only — auto-remove `.git/index.lock`
- Tests for each promoted check's repair and idempotency

**Out of scope:**
- `lifecycle_dirs` migration — touching many docs files in an automated repair is high-blast-radius; leave as warn
- `crash_debris` uncommitted changes / dangling worktrees — operator decision always required
- Any check not in the candidates table above

## Implementation Approach

For each promoted check, the change is the same: detect the repairable condition, attempt repair, report `advisory` on success and `warning` on conflict. The existing `agents_bin_symlinks` (Check 20) and `operator_bin_symlinks` ([SPEC-214](../../../spec/Complete/(SPEC-214)-Operator-Bin-Symlink-Auto-Repair/(SPEC-214)-Operator-Bin-Symlink-Auto-Repair.md)) checks are the reference implementations.

**Ruling out `lifecycle_dirs`:** Migration touches doc files across many directories. A silent auto-migration could rename paths that other artifacts reference, causing specwatch noise and broken links. Requires operator awareness.

**Ruling out `governance` (missing entirely):** Inserting a governance block requires knowing the correct insertion point in AGENTS.md. Without block markers, there is no deterministic anchor — the repair would have to guess structure, which is too risky.

**`commit_signing` key detection:** Check `git config gpg.ssh.allowedSignersFile` or `~/.ssh/swain_signing` (the project's conventional signing key path). Only auto-configure if a usable key is found; otherwise warn as before.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | | From SPEC-214 retro, learning 3 |
| Complete | 2026-03-31 | ee81e05 | 5 checks promoted: memory_directory, script_permissions, commit_signing, governance stale block, crash_debris git lock. 25/25 tests pass. |
