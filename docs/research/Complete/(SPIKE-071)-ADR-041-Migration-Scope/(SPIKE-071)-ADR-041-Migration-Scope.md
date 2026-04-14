---
title: "ADR-041 migration scope — what it takes to move all swain skills and scripts from .agents/ to .swain/"
artifact: SPIKE-071
track: container
status: Complete
author: cristos
created: 2026-04-13
last-updated: 2026-04-13
question: "What is the complete inventory of files, path patterns, and migration steps required to bring all swain skills, scripts, SKILL.md prose, and tests into compliance with ADR-041 (runtime state moves from .agents/ to .swain/)?"
gate: Pre-MVP
risks-addressed:
  - Incomplete migration leaves ghost .agents/ references that break at runtime
  - Missed test files cause silent failures in CI
  - SKILL.md prose references become misleading documentation
  - Worktree symlink targets still point at .agents/ after migration
evidence-pool: ""
---

# ADR-041 migration scope — what it takes to move all swain skills and scripts from .agents/ to .swain/

## Summary

**Go.** The migration is feasible as a single ~250-file PR (~1100 refs). A mechanical `sed` pass handles shell, Python, and test files. SKILL.md prose needs a manual review pass using five categorized migration rules. The gitignore model from ADR-041 must be inverted: track `.swain/`, ignore only `.swain/session/`. SPEC-305 has been rescoped accordingly. The next step is decomposing SPIKE-071's findings into an EPIC with implementing SPECs.

## Question

What is the complete inventory of files, path patterns, and migration steps required to bring all swain skills, scripts, SKILL.md prose, and tests into compliance with ADR-041 (runtime state moves from .agents/ to .swain/)?

## Go / No-Go Criteria

- Every `.sh`, `.py`, and `.md` file under `skills/`, `.claude/skills/`, `.agents/skills/`, `.agents/bin/`, `tests/`, and `scripts/` that references `.agents/` is accounted for with a concrete migration action.
- SKILL.md files sorted into prose categories (path examples, code fences, shell one-liners, frontmatter refs) with a rule per category.
- Worktree symlink logic has a migration plan.
- Doctor and preflight scripts have a transition plan.
- File count and diff size support a go/no-go decision.

## Pivot Recommendation

If the migration surface exceeds a safe single-PR threshold (>300 files or >5000 line changes), pivot to a phased approach. Phase 1 introduces a `$SWAIN_DIR` variable (defaulting to `.swain`) so all scripts read the path from one source. Phase 2 does the bulk rename. This cuts blast radius and allows incremental testing.

## Findings

### 1. Raw reference counts

| Category | Files | Approx refs |
|----------|-------|-------------|
| Shell scripts (skills/) | ~50 | ~150 |
| SKILL.md files (skills/) | 16 of 32 | ~250 |
| SKILL.md files (.claude/skills/) | 16 of 16 | ~250 |
| SKILL.md files (.agents/skills/) | 2 of 2 | ~5 |
| Python files | 5 | ~10 |
| Test scripts (tests/) | 12 | ~30 |
| Doc files (docs/) | ~160 | ~400 |
| AGENTS.md | 1 | ~8 |
| bin/swain | 1 | ~11 |
| .agents/bin/ scripts | 3 | — |

Total: **~250 unique files**, **~1100 references**.

### 2. SKILL.md prose categories

SKILL.md references to `.agents/` fall into distinct categories, each requiring a different migration approach:

| Category | Description | Migration rule | Example |
|----------|-------------|----------------|---------|
| **Runtime shell one-liner** | Inline `bash "$REPO_ROOT/.agents/bin/foo.sh"` invoked by the agent at runtime | Hard-replace with `.swain/bin/foo.sh` | `swain-design` SKILL.md: `bash "$(…)/.agents/bin/chart.sh"` |
| **Prose reference** | Explanatory text mentioning `.agents/` as the runtime directory | Hard-replace `.agents/` → `.swain/` | `swain-doctor` SKILL.md: "The `.agents/bin/` directory" |
| **Code fence example** | Example commands in markdown fences | Hard-replace | `swain-init` SKILL.md: `ls .agents/skills/` |
| **Path in variable / pattern** | `.agents/` used inside a regex, glob, or variable assignment | Hard-replace with care for capturing group boundaries | `bin/swain`: `agent_dirs=(".claude" ".agents" …)` |
| **Historical / ADR reference** | Mentions `.agents/` as a historical location or in an ADR quote | Context-dependent: cite as former location or update if the ADR itself is being revised | ADR-041: the ADR that *defines* the migration |

### 3. Script migration by type

#### 3a. Shell scripts that resolve `REPO_ROOT/.agents/bin/`

These use this pattern:
```bash
bash "$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.agents/bin/<script>.sh"
```

Replace `.agents/bin/` with `.swain/bin/`. The symlink farm in either directory points into `skills/*/scripts/`, so the target scripts also need their `.agents/` references updated.

Affected skills (by reference count):
- swain-doctor (15–16 refs per file)
- swain-session (10–24 refs per file)
- swain-design (7–13 refs per file)
- swain-do (10+ refs)
- swain-test (7 refs)
- All other skills with at least 1 ref

#### 3b. `bin/swain` — the worktree router

This is the highest-density single file (~11 refs). It reads `.agents/session.json`, `.agents/bin/swain-lockfile.sh`, `.agents/bin/swain-session-archive.sh`, `.agents/bin/swain-worktree-name.sh`, and walks `.agents/skills/` and `.claude/skills/`. The `agent_dirs` array literal needs `.agents` → `.swain`.

Direct replacement. For backward compat, add symlinks (`.agents/bin/swain` → `.swain/bin/swain`) via the migration script.

#### 3c. `.agents/bin/` scripts — the symlink farm

Currently 3 files:
- `detect-worktree-links.sh`
- `resolve-worktree-links.sh`
- `git-compact`

These are symlinks into `skills/*/scripts/`. The symlink targets don't need changing (they live in `skills/`), but the symlink **directory** moves from `.agents/bin/` to `.swain/bin/`. The auto-repair and bin-bootstrap scripts that create symlinks must be updated.

#### 3d. Tests

12 test files reference `.agents/`:
- `tests/detect-worktree-links/test_*.sh` (5 files)
- `tests/test_lockfile.sh`
- `tests/test_pre_runtime.sh`
- `tests/test_session_archive.sh`
- `tests/test_session_purpose.sh`
- `tests/test_worktree_naming.sh`
- `skills/swain-session/tests/test-*.sh` (3 files)
- `skills/swain-doctor/tests/test-*.sh` (5 files)

Direct replacement in test fixtures and assertions. Tests must also create `.swain/` test directories instead of `.agents/`.

#### 3e. Python files

5 Python files reference `.agents/`:
- `skills/swain-design/scripts/specgraph/session_decisions.py`
- `skills/swain-security-check/scripts/context_file_scanner.py`
- `skills/swain-security-check/scripts/external_hooks.py`
- `tests/test_external_hooks.py`

String replacement of `.agents/` → `.swain/`.

### 4. Worktree symlink logic

The worktree bootstrap (ADR-040, SPEC-305) symlinks runtime directories from the common root into worktrees. Currently it symlinks `.agents/`. After migration it symlinks `.swain/` instead.

Affected components:
- `bin/swain` (`create_session_worktree`)
- `detect-worktree-links.sh`
- `resolve-worktree-links.sh`
- `swain-init` SKILL.md (bootstrap instructions)
- SPEC-305 (the implementing spec for consumer gitignore + hook)

Backward compat: the post-checkout hook should also symlink `.agents/` → `.swain/` during the transition if `.agents/` still exists.

### 5. Doctor / preflight transition plan

`swain-doctor.sh` and `swain-preflight.sh` have the second-highest reference density after SKILL.md files (~14–16 refs each). They need:

1. **Hard path swap**: `.agents/bin/` → `.swain/bin/`, `.agents/session.json` → `.swain/session.json`, etc.
2. **Stale directory check**: a new doctor check that warns if a stale `.agents/` directory still exists.
3. **Auto-repair update**: the existing bin-auto-repair ([SPEC-186](../../../spec/Complete/(SPEC-186)-Doctor-Agents-Bin-Auto-Repair/SPEC-186.md), [SPEC-187](../../../spec/Complete/(SPEC-187)-Init-Agents-Bin-Bootstrap/SPEC-187.md), [SPEC-188](../../../spec/Complete/(SPEC-188)-Doctor-Bin-Auto-Repair/SPEC-188.md)) must recreate symlinks under `.swain/bin/` instead of `.agents/bin/`.

### 6. Doc files

~160 markdown files under `docs/` reference `.agents/`. Most are historical. They fall into two buckets:

| Bucket | Action |
|--------|--------|
| Active/Proposed artifacts | Update to `.swain/` |
| Complete/Superseded artifacts | Leave as-is (historical record) |

### 7. Estimated scope

| Metric | Value |
|--------|-------|
| Files needing change | ~250 |
| Line changes | ~1100 |
| Risk areas | `bin/swain`, `swain-doctor`, `swain-session`, worktree logic |
| Estimated effort | 1 medium-length focused session with a migration script + manual SKILL.md prose review |

The scope is under the 300-file / 5000-line threshold. A single-PR migration is feasible. Use a script for mechanical replacements, then a manual review for prose nuances.

### 8. Gitignore model correction (revises ADR-041)

ADR-041 says: ignore `.swain/` wholesale, allowlist tracked subpaths. This is wrong.

**Correct model: track `.swain/`, denylist session state.**

Everything in `.swain/` except session state is project-level. It belongs in every worktree with zero bootstrap gap. If `.swain/bin/` were gitignored, worktrees would lack scripts between `git worktree add` and doctor running — a bootstrap gap the post-checkout hook can't close because the hook *is* a bin script.

| Path | Tracked? | Why |
|------|----------|-----|
| `.swain/bin/` | Yes | Symlinks into `skills/`. Must exist at checkout. Doctor rebuilds if broken, but should not need to. |
| `.swain/specwatch-ignore` | Yes | Project-local ignore policy. Should be versioned. |
| `.swain/hook-state/` | Yes | Gate markers (e.g., `adr-check-passed`). Same state across all sessions. |
| `.swain/chart-cache/` | Yes | Derived but project-level. Rebuildable, but versioning avoids cold-start cost. |
| `.swain/search-snapshots/` | Yes | Trove cache. Currently tracked in `.agents/`. Project-level. |
| `.swain/session/` | **No** | Per-operator session state (`session.json`, purpose, focus lane). Not versionable. |

The gitignore for consumer projects is:

```
.swain/session/
```

Not `.swain/` wholesale. This is the inverse of ADR-041's original model.

**Skills do not live in `.swain/`.** Skills must load through the agent runtime's discovery path (`.claude/skills/`, `.agents/skills/`, etc.). `.swain/skills/` is not a thing. The current `.agents/skills/` directory holds installed third-party skills; after migration they stay in whatever agent-runtime skill directory the installer targets. `.swain/` is swain plumbing only.

**SPEC-305 scope impact:** SPEC-305 currently plans to add `.swain/` as a full directory ignore. This must be revised to only ignore `.swain/session/`. The rest of SPEC-305 (worktree hook, managed gitignore block) remains valid.

### 9. Recommended migration script capabilities

1. `sed -i` replacement of `.agents/` → `.swain/` across `.sh`, `.py`, `.md` files in `skills/`, `tests/`, `scripts/`, and `AGENTS.md`.
2. Exclude `docs/` Complete/Superseded artifacts.
3. Move `.agents/bin/` symlinks to `.swain/bin/`.
4. Move `.agents/session.json` to `.swain/session/session.json` (the only gitignored path).
5. Move `.agents/hook-state/`, `.agents/chart-cache/`, `.agents/search-snapshots/`, `.agents/specwatch-ignore` to `.swain/` (all tracked).
6. Remove `.agents/` from `.gitignore`. Add `.swain/session/` instead.
7. Create `.agents/` → `.swain/` symlinks for backward compat during transition.
8. Re-run all tests.

### 10. Linked artifacts

- [ADR-041](../../../adr/Active/(ADR-041)-Swain-Runtime-State-Location.md): the decision driving this migration.
- [SPEC-305](../../../spec/Active/(SPEC-305)-Gitignore-Agentic-Runtime-Folders/(SPEC-305)-Gitignore-Agentic-Runtime-Folders.md): gitignore writer (already targets `.swain/`); will need to verify it does *not* gitignore `.agents/`.
- [SPEC-078](../../../spec/Active/(SPEC-078)-State-Location-Migration/(SPEC-078)-State-Location-Migration.md): earlier state-location migration (`.agents/` for session state) — now superseded in scope by ADR-041.
- [ADR-040](../../../adr/Superseded/(ADR-040)-Worktree-Bootstrap-Via-Post-Checkout-Hook.md): worktree hook — symlink targets change from `.agents/` to `.swain/`.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-13 | — | Initial creation |
| Complete | 2026-04-13 | — | All go/no-go criteria met. Gitignore model corrected. SPEC-305 rescoped. |