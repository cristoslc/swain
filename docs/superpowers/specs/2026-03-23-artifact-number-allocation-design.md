# Centralized Artifact Number Allocation — Design

**Date:** 2026-03-23
**Epic:** EPIC-043
**Specs:** SPEC-156, SPEC-157, SPEC-158, SPEC-159

## Context

Artifact number allocation is ad-hoc — agents scan `docs/<type>/` in their local working tree and pick max+1. In worktree-based workflows each worktree has an isolated copy of `docs/`, so concurrent sessions can allocate the same number. There is no single source of truth.

## Design Decisions

### Scanning strategy: Approach A (filesystem scan all worktrees + git ls-tree trunk)

- Walk each worktree's `docs/<type>/` with `find`, extract numbers from `(<TYPE>-NNN)` patterns
- Also `git ls-tree -r --name-only trunk -- docs/<type>/` to catch committed-but-not-checked-out artifacts
- Silently skip inaccessible worktree paths (stale/deleted) — worktree hygiene is swain-doctor's job
- Performance is negligible (small doc directories, not code trees)
- This is the only approach that catches uncommitted artifacts in other worktrees

### Branch fallback chain

If `trunk` doesn't exist: try `main`, then the current branch's upstream tracking ref.

## Deliverables

### 1. `next-artifact-number.sh <TYPE>` (SPEC-156)

**Location:** `skills/swain-design/scripts/next-artifact-number.sh`

**Interface:**
- Input: TYPE — one of SPEC, EPIC, INITIATIVE, VISION, SPIKE, ADR, PERSONA, RUNBOOK, DESIGN, JOURNEY, TRAIN
- Output: next available number, zero-padded to 3 digits on stdout (e.g., `156`)
- Exit 1 + stderr for invalid type or non-git context
- Returns `001` when no existing artifacts of that type exist

**Algorithm:**
1. Parse & validate TYPE, map to lowercase dir name
2. `git worktree list --porcelain` → collect all worktree paths
3. For each accessible path, `find <path>/docs/<type>/` for `(<TYPE>-NNN)` patterns, extract numbers
4. Silently skip inaccessible worktree paths
5. `git ls-tree -r --name-only trunk -- docs/<type>/` for committed-but-not-checked-out artifacts (with branch fallback chain)
6. Max across all sources + 1, zero-pad to 3 digits

### 2. SKILL.md integration (SPEC-157)

Replace swain-design SKILL.md step 1 with a script invocation:
```
bash "$(find ... -path '*/swain-design/scripts/next-artifact-number.sh' ...)" <TYPE>
```
Include fallback note for environments where the script isn't available.

### 3. Collision detection + resolution tools (SPEC-158)

Three detection layers:
- **specwatch:** post-scan duplicate check across all phase directories
- **pre-commit hook:** check staged files for duplicate artifact numbers
- **swain-sync gate:** pre-commit collision detection with auto-fix offer

Two resolution scripts:

**`renumber-artifact.sh <OLD-ID> <NEW-ID>`** — targeted single-artifact renumber:
- `git mv` the directory `(OLD-ID)-Title/` → `(NEW-ID)-Title/`
- Update `artifact:` frontmatter field in the primary doc
- Rewrite all cross-references across `docs/` (frontmatter fields: `linked-artifacts`, `depends-on-artifacts`, `parent-epic`, `parent-initiative`, `addresses`, `source-issue`; body text hyperlinks)
- Validate NEW-ID doesn't already exist before proceeding
- Stage all changes

**`fix-collisions.sh [TYPE-NNN ...]`** — batch orchestrator:
- No args: scan all `docs/` for duplicates, fix each by renumbering the newer artifact (by `created:` date) to the next available number via `next-artifact-number.sh`
- With args: renumber the specified IDs to next available numbers
- `--dry-run` mode shows what would change without doing it
- Calls `renumber-artifact.sh` for each renumber operation
- Outputs summary of all renames

### 4. Migrate existing callers (SPEC-159)

Replace `get_next_spec_number()` in `migrate-bugs.sh` with a call to `next-artifact-number.sh SPEC`. Grep for any other inline allocation logic and migrate it.

## Non-goals

- Distributed locking or sequence servers — file-level coordination is sufficient
- Changing the numbering scheme (e.g., UUIDs)
- Retroactive renumbering of existing artifacts (fix-collisions.sh handles future collisions only)
- Stale worktree pruning — separate concern for swain-doctor
