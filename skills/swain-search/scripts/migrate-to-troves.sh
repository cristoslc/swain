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
                uv run --with ruamel.yaml python3 - "$manifest" <<'PYEOF'
import sys
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True

manifest_path = sys.argv[1]
with open(manifest_path, 'r') as f:
    data = yaml.load(f)

changed = False

if 'pool' in data:
    val = data['pool']
    keys = list(data.keys())
    idx = keys.index('pool')
    del data['pool']
    data.insert(idx, 'trove', val)
    changed = True

if 'sources' in data and isinstance(data['sources'], list):
    for source in data['sources']:
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

        if 'highlights' not in source:
            source['highlights'] = []
            changed = True
        if 'selective' not in source:
            source['selective'] = False
            changed = True

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
