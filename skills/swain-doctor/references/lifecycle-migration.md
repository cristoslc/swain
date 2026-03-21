# Lifecycle Directory Migration

Detect old phase directories from before ADR-003's three-track normalization. Old directory names: `Draft/`, `Planned/`, `Review/`, `Approved/`, `Testing/`, `Implemented/`, `Adopted/`, `Deprecated/`, `Archived/`, `Sunset/`, `Validated/`.

## Detection

```bash
OLD_PHASES="Draft Planned Review Approved Testing Implemented Adopted Deprecated Archived Sunset Validated"
for dir in docs/*/; do
  for phase in $OLD_PHASES; do
    if [[ -d "${dir}${phase}" ]]; then
      # Check for non-empty (ignore hidden files)
      if find "${dir}${phase}" -maxdepth 1 -not -name '.*' -print -quit 2>/dev/null | grep -q .; then
        echo "  Old directory: ${dir}${phase}"
      fi
    fi
  done
done
```

## Remediation

1. List each old directory and its artifact count.
2. Explain: "ADR-003 normalized artifact lifecycle phases into three tracks. Old phase directories need migration."
3. Check for the migration script: `$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-design/scripts/migrate-lifecycle-dirs.py' -print -quit 2>/dev/null)`
   - If available: offer to run `uv run python3 "$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-design/scripts/migrate-lifecycle-dirs.py' -print -quit 2>/dev/null)" --dry-run` first, then the real migration.
   - If unavailable: provide manual `git mv` instructions using the phase mapping from ADR-003.
4. After migration, clean up empty old directories.

## Status values

- **ok** — no old directories found
- **repaired** — migration script ran successfully
- **warning** — old directories found, user chose not to migrate now
