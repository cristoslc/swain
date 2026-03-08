# bd (beads) CLI Cheatsheet

Quick reference for agents using `bd` (beads) — a git-backed issue tracker with first-class dependency support.

**Full docs:** https://github.com/steveyegge/beads

## Prerequisites

bd works with SQLite by default. It can optionally use a **Dolt SQL server** (port 3307, fallback 3306) for remote sync — this is controlled by the `use_dolt` setting in `.agents/execution-tracking.vars.json`.

**If `use_dolt` is `true`** and commands fail with connection errors, check the server:

```bash
bd dolt start          # Start the server
bd dolt stop           # Stop the server
bd doctor              # Diagnose issues
bd doctor --fix        # Auto-repair
```

**If `use_dolt` is `false`** (default), skip all `bd dolt *` commands — bd uses SQLite and needs no server.

## ID format

Issues use **hash-based IDs**: `bd-a1b2`, `bd-f3e9`. Children use dot notation: `bd-a1b2.1`, `bd-a1b2.2`.

- IDs are assigned by bd on create — never fabricate them.
- Use `--json` to capture the ID programmatically after creation.

## Initialization

```bash
bd init                # Standard init (creates .beads/)
bd init --stealth      # (NOT RECOMMENDED) Invisible to git collaborators
```

> **Note:** `--stealth` adds `.beads/` to `.git/info/exclude`, making issue data invisible to version control. This causes problems for downstream consumers — `.beads/README.md` (which contains ephemeral-file remediation instructions) is never committed, and hooks/config are lost on clone. Use plain `bd init` instead. If you already used `--stealth`, see AGENTS-SETUP.md section 5 for remediation steps.

If `.beads/` already exists, bd is already initialized — do not re-init.

## Issue types and priority

**Types:** `bug`, `feature`, `task`, `epic`, `chore`, `decision`

**Priority:** `0`–`4` (or `P0`–`P4`). 0 = critical, 4 = backlog. Default is 2.
- Do NOT use words like "high", "medium", "low" — bd expects numeric values.

## Creating issues

```bash
# Basic task
bd create "Fix login redirect" -t task -p 2 --json

# With description (ALWAYS include --description for context)
bd create "Add export endpoint" \
  -t feature -p 1 \
  -d "REST endpoint for CSV export of user data" \
  --json

# Epic (implementation plan container)
bd create "Implement auth system" -t epic --external-ref SPEC-003 --json

# Child task under an epic
bd create "Add JWT middleware" -t task --parent bd-a1b2 -p 1 \
  --labels spec:SPEC-003 --json

# With dependencies
bd create "Write tests" -t task --deps bd-a1b2 --json

# Link discovered work to parent
bd create "Found edge case" -t bug -p 1 \
  --deps discovered-from:bd-a1b2 --json
```

**Flags reference:**

| Flag | Purpose |
|------|---------|
| `-t, --type` | Issue type (default: task) |
| `-p, --priority` | Priority 0-4 (default: 2) |
| `-d, --description` | Description text |
| `-a, --assignee` | Assignee name |
| `-l, --labels` | Comma-separated labels |
| `--parent` | Parent issue ID (hierarchical child) |
| `--deps` | Dependencies (`type:id` or just `id`) |
| `--external-ref` | External reference (e.g., `SPEC-003`) |
| `--json` | Output as JSON (use this for scripting) |
| `--silent` | Output only the issue ID |

## Finding work

```bash
bd ready               # Unblocked work (blocker-aware, the RIGHT way)
bd ready --json        # Same, as JSON for parsing
bd ready -n 20         # Show up to 20 items
bd ready -l spec:SPEC-003  # Filter by label
```

**WARNING:** `bd list --ready` is NOT equivalent to `bd ready`. `bd list --ready` only filters by status=open. `bd ready` evaluates actual dependency chains to find truly claimable work. Always use `bd ready`.

## Viewing issues

```bash
bd show bd-a1b2        # Full details with deps, comments, audit trail
bd show bd-a1b2 --json # As JSON

bd list                     # Open issues (default limit 50)
bd list --status=open       # Explicit open filter
bd list --status=in_progress  # Active work
bd list --all               # Include closed
bd list --parent bd-a1b2    # Children of an epic
bd list --pretty            # Tree view with status/priority symbols
bd list -l spec:SPEC-003    # Filter by label
bd list -n 0                # Unlimited results
```

## Claiming and updating

```bash
# Atomic claim (sets assignee + status=in_progress in one operation)
bd update bd-a1b2 --claim --json

# Manual status change
bd update bd-a1b2 --status=in_progress
bd update bd-a1b2 --status=open           # Unclaim / release

# Update fields
bd update bd-a1b2 --title="Better title"
bd update bd-a1b2 -d "Updated description"
bd update bd-a1b2 --notes="Progress note: auth layer complete"
bd update bd-a1b2 --append-notes="Additional finding"
bd update bd-a1b2 -p 0                    # Escalate priority

# Labels
bd update bd-a1b2 --add-label spec:SPEC-007  # Add cross-spec tag
bd update bd-a1b2 --remove-label stale
```

**Valid statuses:** `open`, `in_progress`, `blocked`, `closed`

## Closing issues

```bash
bd close bd-a1b2                          # Close single issue
bd close bd-a1b2 bd-c3d4 bd-e5f6          # Close multiple at once
bd close bd-a1b2 --reason "Deployed to prod"
bd close bd-a1b2 --suggest-next           # Shows newly unblocked work
```

## Dependencies

```bash
# Add dependency: child depends on parent (parent blocks child)
bd dep add bd-child bd-parent

# Shorthand: bd-blocker blocks bd-blocked
bd dep bd-blocker --blocks bd-blocked

# Bidirectional relation (non-blocking)
bd dep relate bd-a1b2 bd-c3d4

# View
bd blocked                  # All blocked issues (evaluates dep chains)
bd dep list bd-a1b2         # Dependencies of a specific issue
bd dep tree bd-a1b2         # Full dependency tree visualization
bd dep cycles               # Detect circular dependencies
```

**WARNING:** `bd blocked` (evaluates actual dependency chains) is different from `bd list --status=blocked` (only checks the stored status field). Use `bd blocked` for accurate results.

## Epics and structure

```bash
# Create epic as implementation plan container
bd create "Auth System" -t epic --external-ref SPEC-003 --json

# Create children under the epic
bd create "Design token schema" -t task --parent bd-epic-id -p 1 --json
bd create "Implement middleware" -t task --parent bd-epic-id -p 1 --json
bd create "Add integration tests" -t task --parent bd-epic-id -p 2 --json

# Set up ordering
bd dep add bd-middleware bd-schema      # middleware depends on schema
bd dep add bd-tests bd-middleware       # tests depend on middleware

# View epic structure
bd list --parent bd-epic-id --pretty
bd children bd-epic-id
```

## Querying and searching

```bash
bd search "authentication"               # Full-text search
bd query "status=open AND priority<=1"    # Complex filter
bd count --status=open                    # Count matching issues
bd stale                                  # Issues not updated recently
```

## Diagnostics

```bash
bd doctor              # Full health check
bd doctor --fix        # Auto-repair issues
bd doctor --agent --json  # AI-facing diagnostics (structured output)
bd status              # Database overview and statistics
bd info                # Database information
```

## Anti-patterns (do NOT do these)

| Anti-pattern | Correct approach |
|-------------|-----------------|
| `bd list --ready` | `bd ready` (blocker-aware) |
| `bd list --status=blocked` to find blocked work | `bd blocked` (evaluates dep chains) |
| `bd edit <id>` | `bd update <id> --field=value` (edit opens $EDITOR, blocks agents) |
| Priority words ("high", "low") | Numeric: `-p 0` through `-p 4` |
| Guessing issue IDs | Use `--json` or `--silent` on create to capture IDs |
| `bd sync` | `bd dolt push` / `bd dolt pull` (sync is deprecated) |
| Omitting `--description` on create | Always provide `-d` for context |
| Creating issues without `--json` | Use `--json` to capture the assigned ID |
| `bd init` when `.beads/` exists | Check first; re-init can cause data loss |

## Global flags (available on all commands)

| Flag | Purpose |
|------|---------|
| `--json` | JSON output (use for programmatic access) |
| `--actor` | Override actor name for audit trail |
| `--quiet` | Suppress non-essential output |
| `--sandbox` | Disable auto-sync |
| `--allow-stale` | Skip staleness checks |

## Dynamic context

bd provides built-in agent context commands:

```bash
bd prime     # Full AI-optimized workflow context (run at session start)
bd onboard   # Minimal AGENTS.md snippet
```

`bd prime` output is dynamic and reflects the current project state. Consider running it when bootstrapping a new session.
