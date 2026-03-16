# Trove Redesign Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename "evidence pool" to "trove" across all swain skills and restructure source storage to support hierarchical content mirroring.

**Architecture:** A migration script handles the mechanical work (directory renames, manifest updates, frontmatter rewrites). Skill files are updated to reference "trove" and the new directory-per-source layout. trovewatch gets structural scanning changes. swain-doctor gets migration detection.

**Tech Stack:** Bash (migration script, trovewatch), YAML (manifests), Markdown (skill files, artifacts)

**Spec:** `docs/superpowers/specs/2026-03-15-trove-redesign.md`

---

## File Map

### New files
- `skills/swain-search/scripts/migrate-to-troves.sh` — Migration script
- `skills/swain-search/references/wordlist.txt` — Disambiguator wordlist (~2000 words)

### Modified files (skill logic)
- `skills/swain-search/SKILL.md` — Full rename + structural source creation changes
- `skills/swain-search/references/manifest-schema.md` — Schema field renames and additions
- `skills/swain-search/references/normalization-formats.md` — Example source-id and type updates
- `skills/swain-search/references/trovewatch-guide.md` — Rename references
- `skills/swain-search/scripts/trovewatch.sh` — Directory scanning logic rewrite
- `skills/swain-design/references/evidence-pool-integration.md` — Rename to `trove-integration.md` + update internals
- `skills/swain-design/SKILL.md` — Update reference path from `evidence-pool-integration.md` to `trove-integration.md`
- `skills/swain-doctor/SKILL.md` — Add migration detection section
- `skills/swain-doctor/scripts/swain-preflight.sh` — Add evidence-pool detection check
- `AGENTS.md` — Update swain-search description ("Evidence pools" → "Troves")

### Migrated files (by migration script)
- `docs/evidence-pools/` → `docs/troves/` (3 pools, 27 files)
- 92 artifact files with `evidence-pool:` frontmatter → `trove:`

---

## Chunk 1: Migration Script

### Task 1: Write the migration script

**Files:**
- Create: `skills/swain-search/scripts/migrate-to-troves.sh`

This script is invoked by swain-doctor or run standalone. It performs 4 steps:
1. Rename `docs/evidence-pools/` to `docs/troves/`
2. Restructure flat sources: `sources/NNN-slug.md` → `sources/NNN-slug/NNN-slug.md`
3. Update manifests: `pool` → `trove`, `id` + `slug` → `source-id`, add new fields
4. Update artifact frontmatter: `evidence-pool:` → `trove:`

Each step is idempotent — checks current state before acting.

- [ ] **Step 1: Write the migration script**

```bash
#!/usr/bin/env bash
# migrate-to-troves.sh — Migrate evidence pools to troves
# Idempotent: safe to run multiple times. Non-destructive: moves, never deletes.
#
# Usage: bash skills/swain-search/scripts/migrate-to-troves.sh [--dry-run]
#
# Steps:
#   1. Rename docs/evidence-pools/ → docs/troves/
#   2. Restructure flat sources into directory-per-source layout
#   3. Update manifest.yaml fields (pool→trove, id+slug→source-id, add new fields)
#   4. Update artifact frontmatter (evidence-pool: → trove:)

set -euo pipefail

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
OLD_DIR="$PROJECT_ROOT/docs/evidence-pools"
NEW_DIR="$PROJECT_ROOT/docs/troves"

log() { echo "migrate-to-troves: $*"; }
dry() { if $DRY_RUN; then log "[dry-run] $*"; else log "$*"; fi; }

# ── Step 1: Rename directory ──────────────────────────────────────────────────

if [[ -d "$OLD_DIR" && ! -d "$NEW_DIR" ]]; then
    dry "Renaming $OLD_DIR → $NEW_DIR"
    $DRY_RUN || mv "$OLD_DIR" "$NEW_DIR"
elif [[ -d "$OLD_DIR" && -d "$NEW_DIR" ]]; then
    log "WARNING: Both docs/evidence-pools/ and docs/troves/ exist. Incomplete migration?"
    log "Please manually reconcile before re-running."
    exit 1
elif [[ ! -d "$OLD_DIR" && -d "$NEW_DIR" ]]; then
    log "Step 1 already done: docs/troves/ exists, docs/evidence-pools/ does not."
elif [[ ! -d "$OLD_DIR" && ! -d "$NEW_DIR" ]]; then
    log "No evidence pools or troves directory found. Nothing to migrate."
    # Continue — there may still be frontmatter to update
fi

# ── Step 2: Restructure flat sources ──────────────────────────────────────────

if [[ -d "$NEW_DIR" ]]; then
    for pool_dir in "$NEW_DIR"/*/; do
        sources_dir="${pool_dir}sources"
        [[ -d "$sources_dir" ]] || continue

        for source_file in "$sources_dir"/*.md; do
            [[ -f "$source_file" ]] || continue
            stem="$(basename "$source_file" .md)"
            target_dir="$sources_dir/$stem"
            target_file="$target_dir/$stem.md"

            if [[ -f "$target_file" ]]; then
                # Already restructured
                continue
            fi

            dry "Restructuring $source_file → $target_file"
            if ! $DRY_RUN; then
                mkdir -p "$target_dir"
                mv "$source_file" "$target_file"
            fi
        done
    done
    log "Step 2 complete: sources restructured."
else
    log "Step 2 skipped: no troves directory."
fi

# ── Step 3: Update manifests ──────────────────────────────────────────────────

if [[ -d "$NEW_DIR" ]]; then
    for manifest in "$NEW_DIR"/*/manifest.yaml; do
        [[ -f "$manifest" ]] || continue

        if grep -q '^pool:' "$manifest" 2>/dev/null; then
            dry "Updating manifest: $manifest"
            if ! $DRY_RUN; then
                # Use ruamel.yaml for format-preserving YAML manipulation
                uv run --with ruamel.yaml python3 - "$manifest" <<'PYEOF'
import sys
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True

manifest_path = sys.argv[1]
with open(manifest_path, 'r') as f:
    data = yaml.load(f)

changed = False

# Rename pool → trove
if 'pool' in data:
    # Insert trove at same position, remove pool
    val = data['pool']
    keys = list(data.keys())
    idx = keys.index('pool')
    del data['pool']
    # ruamel preserves insertion order
    data.insert(idx, 'trove', val)
    changed = True

# Update sources
if 'sources' in data and isinstance(data['sources'], list):
    for source in data['sources']:
        # Merge id + slug → source-id
        if 'id' in source and 'slug' in source:
            new_id = f"{source['id']}-{source['slug']}"
            del source['id']
            del source['slug']
            source.insert(0, 'source-id', new_id)
            changed = True
        elif 'id' in source and 'source-id' not in source:
            val = source['id']
            del source['id']
            source.insert(0, 'source-id', val)
            changed = True

        # Add new fields if missing
        if 'highlights' not in source:
            source['highlights'] = []
            changed = True
        if 'selective' not in source:
            source['selective'] = False
            changed = True

        # Standardize hash format (strip sha256: prefix if present)
        if 'hash' in source and isinstance(source['hash'], str):
            if source['hash'].startswith('sha256:'):
                source['hash'] = source['hash'][7:]
                changed = True

if changed:
    with open(manifest_path, 'w') as f:
        yaml.dump(data, f)
    print(f"  Updated: {manifest_path}")
else:
    print(f"  Already up to date: {manifest_path}")
PYEOF
            fi
        else
            log "  Manifest already updated: $manifest"
        fi
    done
    log "Step 3 complete: manifests updated."
else
    log "Step 3 skipped: no troves directory."
fi

# ── Step 4: Update artifact frontmatter ───────────────────────────────────────

docs_dir="$PROJECT_ROOT/docs"
if [[ -d "$docs_dir" ]]; then
    count=0
    while IFS= read -r -d '' file; do
        if grep -q '^evidence-pool:' "$file" 2>/dev/null; then
            if ! $DRY_RUN; then
                # Portable in-place replacement (works on macOS and Linux)
                python3 -c "
import sys; p=sys.argv[1]; t=open(p).read()
open(p,'w').write(t.replace('\nevidence-pool:','\ntrove:'))
" "$file"
            fi
            count=$((count + 1))
        fi
    done < <(find "$docs_dir" -name '*.md' -print0)
    dry "Step 4 complete: updated frontmatter in $count artifact files."
else
    log "Step 4 skipped: no docs directory."
fi

log "Migration complete."
```

- [ ] **Step 2: Make the script executable**

Run: `chmod +x skills/swain-search/scripts/migrate-to-troves.sh`

- [ ] **Step 3: Test with --dry-run against current evidence pools**

Run: `cd /path/to/worktree && bash skills/swain-search/scripts/migrate-to-troves.sh --dry-run`

Expected: Log output showing what would happen, no files changed. Verify:
- "Renaming docs/evidence-pools → docs/troves"
- "Restructuring" messages for each flat source file
- "Updating manifest" for each pool
- "updated frontmatter in N artifact files" where N ≈ 92

- [ ] **Step 4: Commit**

```bash
git add skills/swain-search/scripts/migrate-to-troves.sh
git commit -m "feat: add migrate-to-troves.sh migration script"
```

---

### Task 2: Create the wordlist

**Files:**
- Create: `skills/swain-search/references/wordlist.txt`

Generate a wordlist of ~2000 short (3-7 character), thematically neutral English words. One word per line. No offensive, ambiguous, or software-overloaded terms. Alphabetically sorted for diffability.

Good sources: EFF short wordlist, BIP39 word list (filter to 3-7 chars), or curate from a frequency list.

- [ ] **Step 1: Generate the wordlist**

Use a script to pull from the system dictionary and filter:

```bash
# Works on both macOS and Linux (sort -R is portable)
grep -E '^[a-z]{3,7}$' /usr/share/dict/words | \
  grep -v -E "(death|kill|hate|slave|damn|hell|drug|bomb|virus|toxic|abuse|rape|ass|die|gun|war)" | \
  sort -u | \
  sort -R | head -2000 | \
  sort > skills/swain-search/references/wordlist.txt
```

Verify: `wc -l skills/swain-search/references/wordlist.txt` should show ~2000 lines (minimum 1000 per spec).

- [ ] **Step 2: Spot-check the wordlist**

Run: `head -20 skills/swain-search/references/wordlist.txt && echo "..." && tail -20 skills/swain-search/references/wordlist.txt`

Manually scan for any inappropriate or confusing words. Remove any that look wrong.

- [ ] **Step 3: Commit**

```bash
git add skills/swain-search/references/wordlist.txt
git commit -m "feat: add disambiguator wordlist for trove source IDs"
```

---

## Chunk 2: Skill File Updates

### Task 3: Update swain-search SKILL.md

**Files:**
- Modify: `skills/swain-search/SKILL.md`

This is the largest single file change. All "evidence pool" references become "trove", all path references update, and source creation instructions change from flat `NNN-slug.md` to hierarchical `<source-id>/<source-id>.md`.

**Key changes by line range (approximate — verify line numbers before editing):**

| Line(s) | Current | New |
|---------|---------|-----|
| 3 | `evidence pool collection and normalization` | `trove collection and normalization` |
| 17 | `reusable evidence pools` | `reusable troves` |
| 30 | `Build a new evidence pool` | `Build a new trove` |
| ~77 | `NNN-<slug>.md` naming | `<source-id>/<source-id>.md` naming |
| 110-114 | `docs/evidence-pools/<pool-id>/...` | `docs/troves/<trove-id>/...` |
| 114 | `evidence-pool: <pool-id>@<commit-hash>` | `trove: <trove-id>@<commit-hash>` |
| 150 | `docs/evidence-pools/*/manifest.yaml` | `docs/troves/*/manifest.yaml` |
| 183 | `evidence pools in frontmatter` | `troves in frontmatter` |
| 186 | `evidence-pool: websocket-vs-sse@abc1234` | `trove: websocket-vs-sse@abc1234` |

Also update:
- Create mode Step 2: change sequential numbering (`001`, `002`) to slug-based source IDs
- Create mode Step 3: source directory is `sources/<source-id>/` not `sources/NNN-slug.md`
- Add guidance for `repository` and `documentation-site` source types (mirror hierarchy)
- Add selective ingestion guidance (large sources, `selective: true`)
- Add `highlights` population guidance
- Add wordlist disambiguator instructions (double-underscore separator, fallback to hex)
- Extend mode: sequential numbering → slug-based, same directory structure rules

- [ ] **Step 1: Read the current SKILL.md**

Run: Read `skills/swain-search/SKILL.md` in full.

- [ ] **Step 2: Replace all "evidence pool" / "evidence-pool" with "trove"**

Use find-and-replace across the file. Be careful with:
- `evidence pool` (prose) → `trove`
- `evidence-pool` (frontmatter key, path segment) → `trove`
- `evidence pools` (plural) → `troves`
- `evidence-pools` (directory name) → `troves`
- `pool-id` (in path templates) → `trove-id`
- `pool` (standalone in manifest context) → `trove`

- [ ] **Step 3: Update source creation instructions**

Replace the flat `NNN-slug.md` naming with:
- Source IDs are slugs (lowercase, hyphenated, human-readable)
- Flat sources: `sources/<source-id>/<source-id>.md`
- Hierarchical sources (type `repository`, `documentation-site`): `sources/<source-id>/` with original tree mirrored inside
- Default: mirror full tree. For large sources (thousands of files), ingest selectively and set `selective: true`
- Populate `highlights` array during ingestion
- When slug collides: append `__word1-word2` from wordlist, or `__a3f8` hex fallback

- [ ] **Step 4: Update the report template paths**

Change the Step 5 report template from `docs/evidence-pools/<pool-id>/` paths to `docs/troves/<trove-id>/` paths.

- [ ] **Step 5: Update Discover mode glob**

Change `docs/evidence-pools/*/manifest.yaml` to `docs/troves/*/manifest.yaml`.

- [ ] **Step 6: Update SKILL.md frontmatter description and short-description**

If the SKILL.md frontmatter has `description:` or `short-description:` fields, update them from "evidence pool" to "trove".

- [ ] **Step 7: Verify no "evidence" references remain**

Run: `grep -in "evidence" skills/swain-search/SKILL.md`

Expected: Zero matches (or only in the changelog/comments about the migration).

- [ ] **Step 8: Update AGENTS.md**

In `AGENTS.md`, find the swain-search skill table row:
```
| **swain-search** | Evidence pools — collect, normalize, and cache research sources |
```
Change to:
```
| **swain-search** | Troves — collect, normalize, and cache research sources |
```

- [ ] **Step 9: Commit**

```bash
git add skills/swain-search/SKILL.md AGENTS.md
git commit -m "feat: rename evidence pool to trove in swain-search SKILL.md and AGENTS.md"
```

---

### Task 4: Update swain-search reference docs

**Files:**
- Modify: `skills/swain-search/references/manifest-schema.md`
- Modify: `skills/swain-search/references/normalization-formats.md`
- Modify: `skills/swain-search/references/trovewatch-guide.md`

- [ ] **Step 1: Read all three files**

Read `manifest-schema.md`, `normalization-formats.md`, `trovewatch-guide.md` in full.

- [ ] **Step 2: Update manifest-schema.md**

Key changes:
- Line 3: "evidence pool" → "trove"
- Line 9: `pool:` field → `trove:`
- Lines 36-37: Replace `id:` + `slug:` with single `source-id:` field
- Line 38: Add `repository`, `documentation-site` to type enum (keep `local`)
- Add `highlights: []` field (string array, paths relative to source-id directory)
- Add `selective: false` field (boolean)
- Remove `root:` if present
- Standardize hash description: "Bare hex SHA-256 digest (no sha256: prefix)"
- Update TTL section: add `repository` (30d default), `documentation-site` (7d default)

- [ ] **Step 3: Update normalization-formats.md**

Key changes:
- Line 3: "evidence pool" → "trove"
- All frontmatter examples: `source-id: "001"` → slug-based (e.g., `source-id: "mdn-websocket-api"`)
- Line 13 type enum: add `repository`, `documentation-site`
- Add brief section for `repository` type normalization (preserve tree structure, add frontmatter to each file)
- Add brief section for `documentation-site` type normalization (preserve section hierarchy)

- [ ] **Step 4: Update trovewatch-guide.md**

Key changes:
- Line 3: "evidence pools" → "troves"
- Any path references: `docs/evidence-pools/` → `docs/troves/`

- [ ] **Step 5: Verify no "evidence" references remain in any of the three files**

Run: `grep -in "evidence" skills/swain-search/references/manifest-schema.md skills/swain-search/references/normalization-formats.md skills/swain-search/references/trovewatch-guide.md`

Expected: Zero matches.

- [ ] **Step 6: Commit**

```bash
git add skills/swain-search/references/manifest-schema.md \
      skills/swain-search/references/normalization-formats.md \
      skills/swain-search/references/trovewatch-guide.md
git commit -m "feat: update swain-search reference docs for trove rename"
```

---

### Task 5: Rename and update evidence-pool-integration.md

**Files:**
- Rename: `skills/swain-design/references/evidence-pool-integration.md` → `skills/swain-design/references/trove-integration.md`
- Modify: `skills/swain-design/SKILL.md` (update reference path)

- [ ] **Step 1: Read the current file**

Read `skills/swain-design/references/evidence-pool-integration.md` in full.

- [ ] **Step 2: Rename the file**

Run: `git mv skills/swain-design/references/evidence-pool-integration.md skills/swain-design/references/trove-integration.md`

- [ ] **Step 3: Update all internal references**

In `trove-integration.md`:
- Line 3: "evidence pools" → "troves"
- Line 18: `docs/evidence-pools/*/manifest.yaml` → `docs/troves/*/manifest.yaml`
- Line 20: "evidence pool(s)" → "trove(s)"
- Line 24: "evidence pools" → "troves"
- Line 26: `evidence-pool` frontmatter field → `trove`
- Line 30: `evidence-pool` frontmatter → `trove`
- All other "evidence pool" prose → "trove"

- [ ] **Step 4: Update swain-design SKILL.md reference**

Read `skills/swain-design/SKILL.md` and find the line referencing `evidence-pool-integration.md`. Update to `trove-integration.md`.

- [ ] **Step 5: Verify no "evidence" references remain**

Run: `grep -in "evidence" skills/swain-design/references/trove-integration.md`

Expected: Zero matches.

- [ ] **Step 6: Commit**

```bash
git add skills/swain-design/references/trove-integration.md \
      skills/swain-design/references/evidence-pool-integration.md \
      skills/swain-design/SKILL.md
git commit -m "feat: rename evidence-pool-integration to trove-integration"
```

---

## Chunk 3: trovewatch Structural Changes

### Task 6: Update trovewatch.sh scanning logic

**Files:**
- Modify: `skills/swain-search/scripts/trovewatch.sh`

The scanning logic currently looks for flat `NNN-slug.md` files. It needs to walk `sources/<source-id>/` directories instead. It also needs to handle `selective: true` sources.

- [ ] **Step 1: Read the current trovewatch.sh**

Read `skills/swain-search/scripts/trovewatch.sh` in full. Identify:
- Line 12: `POOLS_DIR="docs/evidence-pools"` — change to `TROVES_DIR="docs/troves"`
- The Python scanning block (~lines 183-211) that constructs filenames as `{id}-{slug}.md`
- The orphan detection logic that expects flat files in `sources/`
- The missing-file check logic

- [ ] **Step 2: Update the directory variable**

Change `POOLS_DIR="docs/evidence-pools"` to `TROVES_DIR="docs/troves"`. Update all references from `$POOLS_DIR` to `$TROVES_DIR` and rename "pools" variables/messages to "troves" throughout.

- [ ] **Step 3: Rewrite the source file discovery**

The Python scanning block needs to:
- Read `source-id` from manifest (not `id` + `slug`)
- Expect source directories: `sources/<source-id>/`
- For flat sources: check `sources/<source-id>/<source-id>.md` exists
- For hierarchical sources: check `sources/<source-id>/` directory exists and is non-empty
- When `selective: true`, skip the "expected files present" check entirely

- [ ] **Step 4: Update orphan detection**

Orphan detection should:
- List directories in `sources/`
- Compare against `source-id` values in manifest
- Flag directories that have no manifest entry (orphan)
- Flag manifest entries whose directory doesn't exist (missing), unless `selective: true`

- [ ] **Step 5: Update user-facing messages**

Replace all "evidence pool" strings in echo/log statements with "trove".

- [ ] **Step 6: Commit (testing deferred to Task 8 Step 7 after migration runs)**

```bash
git add skills/swain-search/scripts/trovewatch.sh
git commit -m "feat: update trovewatch scanning for directory-per-source layout"
```

---

## Chunk 4: Doctor Integration & Migration Execution

### Task 7: Add swain-doctor migration detection

**Files:**
- Modify: `skills/swain-doctor/SKILL.md`
- Modify: `skills/swain-doctor/scripts/swain-preflight.sh`

- [ ] **Step 1: Read swain-doctor/SKILL.md**

Read in full. Find the section listing health checks. Add a new check for evidence pool migration.

- [ ] **Step 2: Add migration detection to SKILL.md**

Add a new check section (after existing checks):

```markdown
### Evidence Pool → Trove Migration

Detect unmigrated evidence pools:
- If `docs/evidence-pools/` exists: warn and offer to run migration
- If any artifact frontmatter contains `evidence-pool:`: warn and offer migration
- If both `docs/troves/` and `docs/evidence-pools/` exist: warn about incomplete migration

Migration script: `bash skills/swain-search/scripts/migrate-to-troves.sh`
Dry run first: `bash skills/swain-search/scripts/migrate-to-troves.sh --dry-run`
```

- [ ] **Step 3: Read swain-preflight.sh**

Read `skills/swain-doctor/scripts/swain-preflight.sh` in full. Understand the check pattern.

- [ ] **Step 4: Add preflight check for evidence pools**

Add a check that sets `NEEDS_DOCTOR=1` if `docs/evidence-pools/` exists:

```bash
# Evidence pool migration check
if [[ -d "$PROJECT_ROOT/docs/evidence-pools" ]]; then
    echo "preflight: docs/evidence-pools/ detected — trove migration needed"
    NEEDS_DOCTOR=1
fi
```

- [ ] **Step 5: Commit**

```bash
git add skills/swain-doctor/SKILL.md skills/swain-doctor/scripts/swain-preflight.sh
git commit -m "feat: add evidence pool migration detection to swain-doctor"
```

---

### Task 8: Execute migration on this project

**Files:**
- Migrate: `docs/evidence-pools/` → `docs/troves/` (3 pools, 27 files)
- Migrate: 92 artifact files (frontmatter update)

- [ ] **Step 1: Run dry-run first**

Run: `bash skills/swain-search/scripts/migrate-to-troves.sh --dry-run`

Review output. Confirm the expected changes match the 3 pools and ~92 artifact files.

- [ ] **Step 2: Run the actual migration**

Run: `bash skills/swain-search/scripts/migrate-to-troves.sh`

- [ ] **Step 3: Verify directory structure**

Run: `ls docs/troves/` — should show 3 trove directories (cognee-meta-skill, security-skill-landscape, work-item-hierarchy).

Note: `work-item-hierarchy` has no `sources/` directory — only manifest.yaml and synthesis.md. The migration script safely skips it in Step 2. Verify it was not corrupted.

Run: `ls docs/troves/cognee-meta-skill/sources/` — should show directories (e.g., `001-cognee-meta-skill-md/`), not flat `.md` files.

Run: `ls docs/troves/cognee-meta-skill/sources/001-cognee-meta-skill-md/` — should contain `001-cognee-meta-skill-md.md`.

- [ ] **Step 4: Verify manifests updated**

Run: `head -5 docs/troves/cognee-meta-skill/manifest.yaml` — should show `trove:` not `pool:`.

Run: `grep 'source-id:' docs/troves/cognee-meta-skill/manifest.yaml | head -3` — should show slug-based IDs like `source-id: 001-cognee-meta-skill-md`.

- [ ] **Step 5: Verify artifact frontmatter updated**

Run: `grep -r '^evidence-pool:' docs/` — should return zero matches.

Run: `grep -r '^trove:' docs/ | head -5` — should show updated frontmatter.

- [ ] **Step 6: Verify old directory is gone**

Run: `ls docs/evidence-pools/ 2>&1` — should show "No such file or directory".

- [ ] **Step 7: Run trovewatch to validate**

Run: `bash skills/swain-search/scripts/trovewatch.sh scan`

Expected: Clean scan, no warnings for the migrated troves.

- [ ] **Step 8: Commit the migration**

```bash
git add docs/
git commit -m "feat: migrate evidence pools to troves (3 pools, 92 artifacts)"
```

Note: `git add docs/` stages both the new `docs/troves/` and the deletion of `docs/evidence-pools/`, plus all artifact frontmatter changes. Verify with `git diff --stat --cached` before committing.

---

## Chunk 5: Verification

### Task 9: Final verification pass

- [ ] **Step 1: Check for any remaining "evidence.pool" references in skills**

Run: `grep -r "evidence.pool\|evidence-pool" skills/`

Expected: Zero matches. If any remain, fix them.

- [ ] **Step 2: Check for any remaining "evidence-pool" frontmatter in artifacts**

Run: `grep -r "^evidence-pool:" docs/`

Expected: Zero matches.

- [ ] **Step 3: Verify the spec's acceptance criteria**

Walk through each AC from the spec:

1. `docs/troves/` exists and is the canonical path — `ls docs/troves/`
2. Source IDs are slug-based — `grep 'source-id:' docs/troves/*/manifest.yaml`
3. (New troves only — verified by reading SKILL.md instructions)
4. (New troves only — verified by reading SKILL.md instructions)
5. Manifest has new fields — `grep -E 'highlights:|selective:' docs/troves/*/manifest.yaml`
6. (Wordlist disambiguator — verified by reading SKILL.md + wordlist exists)
7. Wordlist has 1000+ entries — `wc -l skills/swain-search/references/wordlist.txt`
8. Migration script exists and works — already tested in Task 8
9. Migration is idempotent — run `bash skills/swain-search/scripts/migrate-to-troves.sh` again, verify no-op
10. swain-doctor detects migration — check SKILL.md and preflight.sh
11. All skill references updated — confirmed by grep in Step 1
12. Existing troves functional — trovewatch scan clean

- [ ] **Step 4: Commit any fixes found during verification**

If any issues found, fix and commit:

Stage only the specific files that were fixed, then commit:

```bash
git add <fixed-files>
git commit -m "fix: address issues found during trove migration verification"
```

- [ ] **Step 5: Update the spec status**

Change the spec status from "Draft" to "Implementing" (or "Complete" if all ACs are met):

```bash
# In docs/superpowers/specs/2026-03-15-trove-redesign.md
# Change: **Status:** Draft
# To:     **Status:** Complete
```

- [ ] **Step 6: Final commit**

```bash
git add docs/superpowers/specs/2026-03-15-trove-redesign.md
git commit -m "docs: mark trove redesign spec as complete"
```
