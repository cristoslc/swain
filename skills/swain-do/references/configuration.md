# Configuration

The skill stores persistent project-level configuration in `.agents/execution-tracking.vars.json`. This file is created on first run and checked on every subsequent invocation.

## First-run setup

If `.agents/execution-tracking.vars.json` does not exist, create it by asking the user the questions below (use sensible defaults if the user says "just use defaults"):

| Key | Type | Default | Question |
|-----|------|---------|----------|
| `tk_path` | string | `"skills/swain-do/bin/tk"` | "Path to the vendored tk script (relative to project root)" |
| `fallback_format` | `"jsonl"` \| `"markdown"` | `"jsonl"` | "If tk is unavailable, use JSONL or Markdown for the fallback ledger?" |

Write the file as pretty-printed JSON:

```json
{
  "tk_path": "skills/swain-do/bin/tk",
  "fallback_format": "jsonl"
}
```

On subsequent runs, read the file and apply its values — don't re-ask.

## Applying config

- **`tk_path`**: Resolve this path relative to the project root to find the vendored tk script. Add its directory to PATH for plugin resolution.
- **`fallback_format`**: Controls the format used by the Fallback section.

## Bootstrap workflow

1. **Load config:** Read `.agents/execution-tracking.vars.json`. If missing, run first-run setup above.
2. **Resolve tk:** The vendored tk script lives at the configured `tk_path` (default: `skills/swain-do/bin/tk`). Verify it exists and is executable.
3. **Set up PATH:** Export `PATH` with tk's directory prepended so plugins (`ticket-query`, `ticket-migrate-beads`) are found:
   ```bash
   TK_BIN="$(cd "$(dirname "$tk_path")" && pwd)"
   export PATH="$TK_BIN:$PATH"
   ```
4. **Check for existing data:** look for `.tickets/` directory.
5. **If no `.tickets/`, first use:** tk creates `.tickets/` automatically on first `tk create`.
6. **Verify:** `tk ready` should run without error.
