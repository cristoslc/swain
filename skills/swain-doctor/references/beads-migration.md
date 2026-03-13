# Stale .beads/ Migration

Detects leftover `.beads/` directories from the bd-to-tk migration and migrates automatically.

If `.beads/` does NOT exist → skip (report "ok (not present)").

## Case 1: `.tickets/` already exists

Data already migrated. Remove stale directory:
```bash
rm -rf .beads/
```
Report: "Removed stale `.beads/` directory — migration to `.tickets/` was already complete."

## Case 2: `.tickets/` does NOT exist (migration needed)

1. Locate the migration script:
   ```bash
   MIGRATE="$(find . .claude .agents skills -path '*/swain-do/bin/ticket-migrate-beads' -print -quit 2>/dev/null)"
   ```

2. Locate backup data:
   ```bash
   if [ -f .beads/backup/issues.jsonl ]; then
     cp .beads/backup/issues.jsonl .beads/issues.jsonl
   fi
   ```

3. Run migration (requires `jq`):
   ```bash
   TK_BIN="$(cd "$(dirname "$MIGRATE")" && pwd)"
   export PATH="$TK_BIN:$PATH"
   ticket-migrate-beads
   ```

4. Verify: `ls .tickets/*.md 2>/dev/null | wc -l`

5. If succeeded (count > 0): `rm -rf .beads/`
   Report: "Migrated N tickets from `.beads/` to `.tickets/`."

6. If failed: warn but do not delete. Provide manual migration steps:
   ```bash
   TK_BIN="$(cd skills/swain-do/bin && pwd)" && export PATH="$TK_BIN:$PATH"
   cp .beads/backup/issues.jsonl .beads/issues.jsonl
   ticket-migrate-beads
   ```
   After verifying `.tickets/` data, remove `.beads/` with `rm -rf .beads/`.
