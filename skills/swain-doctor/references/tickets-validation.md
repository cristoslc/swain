# Tickets Directory Validation

Runs every session after governance checks. Idempotent. **Skip entirely if `.tickets/` does not exist.**

## Step 1 — Validate ticket YAML frontmatter

```bash
for f in .tickets/*.md; do
  [ -f "$f" ] || continue
  if ! head -1 "$f" | grep -q '^---$'; then
    echo "invalid: $f (missing frontmatter open)"
  elif ! sed -n '2,/^---$/p' "$f" | tail -1 | grep -q '^---$'; then
    echo "invalid: $f (missing frontmatter close)"
  fi
done
```

If invalid files found → warn: "Found N ticket(s) with invalid YAML frontmatter. tk may not be able to read these."
If all valid → silent.

## Step 2 — Detect stale lock files

```bash
if [ -d .tickets/.locks ]; then
  find .tickets/.locks -type f -mmin +60 2>/dev/null
fi
```

If stale locks found (> 1 hour old) → warn and list files. **Do not auto-delete** — ask the user first.

## Extended tk health checks

### Vendored tk availability

```bash
TK_BIN="$SKILLS_ROOT/swain-do/bin/tk"
if [ ! -x "$TK_BIN" ]; then
  echo "warning: vendored tk not found or not executable at $TK_BIN"
fi
```

If missing → warn: "Reinstall swain skills to restore it."

### Stale lock files (same as Step 2)

Check `.tickets/.locks/` for files older than 1 hour. Ask before deleting.
