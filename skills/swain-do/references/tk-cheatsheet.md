# tk (ticket) CLI cheatsheet

Quick reference for the vendored `tk` script at `bin/tk`.

## Prerequisites

- tk is a single bash script — no runtime dependencies beyond bash + coreutils
- Vendored in the project at `bin/tk`
- Stores tickets as markdown files with YAML frontmatter in `.tickets/`
- Plugins (`ticket-query`, `ticket-migrate-beads`) live in the same `bin/` directory

## Setup

tk requires no explicit initialization. The `.tickets/` directory is created automatically on first `tk create`.

To use tk from anywhere in the project:

```bash
TK_BIN="$(cd bin && pwd)"  # relative to the project root
export PATH="$TK_BIN:$PATH"
```

## ID format

- Hash-based: `nw-5c46`, `ab-3f2e`
- Prefixed with project abbreviation (auto-detected from directory name)
- Partial matching: `tk show 5c4` matches `nw-5c46`
- Never fabricate IDs — capture from `tk create` output

## Ticket format

Each ticket is a markdown file in `.tickets/`:

```markdown
---
id: nw-5c46
status: open
type: task
priority: 2
deps: [nw-a1b2]
tags: [spec:SPEC-003, backend]
parent: nw-f3e9
external-ref: SPEC-003
assignee: agent
created: 2026-03-12T10:30:00Z
---
# Fix login redirect

Description of the task...

## Notes

**2026-03-12T10:30:00Z**

Added JWT middleware; test passes.
```

## Issue types & priority

**Types:** `bug`, `feature`, `task`, `epic`, `chore`

**Priority:** `0`–`4` (numeric only)

| Priority | Meaning |
|----------|---------|
| 0 | Critical (security, data loss, broken builds) |
| 1 | High (major features, important bugs) |
| 2 | Medium (default) |
| 3 | Low (polish, optimization) |
| 4 | Backlog (future ideas) |

## Creating tickets

```bash
# Basic task
tk create "Fix login redirect" -t task -p 2

# With description
tk create "Add export endpoint" -t feature -p 1 -d "REST endpoint for CSV export"

# Epic with external reference
tk create "Implement auth system" -t epic --external-ref SPEC-003

# Child task with tags
tk create "Add JWT middleware" -t task --parent nw-a1b2 -p 1 --tags spec:SPEC-003

# All create flags
#   -t, --type          Type (bug|feature|task|epic|chore) [default: task]
#   -p, --priority      Priority 0-4, 0=highest [default: 2]
#   -d, --description   Description text
#   --design            Design notes
#   --acceptance        Acceptance criteria
#   -a, --assignee      Assignee
#   --external-ref      External reference (e.g., SPEC-003, gh-123)
#   --parent            Parent ticket ID
#   --tags              Comma-separated tags (e.g., --tags ui,backend,spec:SPEC-003)
```

## Finding work

```bash
# Unblocked work (dependency-aware)
tk ready

# Blocked tickets (have unresolved dependencies)
tk blocked

# Filter ready by assignee or type
tk ready -a agent
tk ready -T epic

# Recently closed
tk closed
tk closed --limit=10
```

**WARNING:** `tk ready` evaluates the full dependency graph. It only shows tickets whose deps are all closed.

## Viewing tickets

```bash
# Full details
tk show nw-a1b2

# JSON output (via ticket-query plugin)
ticket-query                                    # All tickets as JSON
ticket-query '.status == "open"'                # Filter open
ticket-query '.type == "epic"'                  # Filter epics
ticket-query '.tags and (.tags | contains("spec:SPEC-003"))'  # By tag
```

## Claiming & updating

```bash
# Atomic claim (mkdir lock + start + assign)
tk claim nw-a1b2
tk claim nw-a1b2 myname    # Specify actor

# Release lock without changing status
tk release nw-a1b2

# Set status directly
tk start nw-a1b2            # → in_progress
tk status nw-a1b2 open      # → open
tk status nw-a1b2 closed    # → closed
```

Valid statuses: `open`, `in_progress`, `closed`

## Closing tickets

```bash
# Close
tk close nw-a1b2

# Close with evidence (add note first)
tk add-note nw-a1b2 "JWT middleware added; test_jwt_validation passes"
tk close nw-a1b2

# Abandon (convention: prefix with "Abandoned:")
tk add-note nw-a1b2 "Abandoned: approach infeasible after testing"
tk close nw-a1b2

# Reopen
tk reopen nw-a1b2
```

## Dependencies

```bash
# Add dependency (child depends on parent)
tk dep nw-child nw-parent

# Remove dependency
tk undep nw-child nw-parent

# View dependency tree
tk dep tree nw-a1b2
tk dep tree --full nw-a1b2   # Disable dedup

# Find cycles
tk dep cycle

# Symmetric links (non-blocking)
tk link nw-a1b2 nw-c3d4
tk unlink nw-a1b2 nw-c3d4
```

## Notes

```bash
# Add timestamped note
tk add-note nw-a1b2 "Discovered edge case in auth flow"

# Pipe note from stdin
echo "Long note content here" | tk add-note nw-a1b2
```

## ticket-query (JSON output)

The `ticket-query` plugin reads all `.tickets/*.md` files and outputs JSON. Pipe through jq for filtering:

```bash
# All tickets
ticket-query

# Open tickets
ticket-query '.status == "open"'

# In-progress tasks
ticket-query '.status == "in_progress"'

# Tickets with specific tag
ticket-query '.tags and (.tags | contains("spec:SPEC-003"))'

# Count open tickets
ticket-query '.status == "open"' | wc -l
```

## ticket-migrate-beads

Converts `.beads/issues.jsonl` to `.tickets/` markdown files:

```bash
ticket-migrate-beads
```

Requires `jq`. Reads from `.beads/issues.jsonl`, writes to `.tickets/`.

## Anti-patterns

| Wrong | Right | Why |
|-------|-------|-----|
| Guessing ticket IDs | Capture from `tk create` output | IDs are hash-based |
| Parsing `tk ready` output programmatically | Use `ticket-query` | Human-readable output may change |
| Omitting `--description` on create | Always use `-d` | Future agents need context |
| Closing without evidence | `tk add-note` then `tk close` | Prevents completion drift |
| Using `tk start` for claiming | Use `tk claim` | `claim` is atomic (mkdir lock) |
| Checking `.beads/` directory | Check `.tickets/` directory | beads is deprecated |

## Plugins

Plugins are scripts named `tk-*` or `ticket-*` in PATH. They receive `TICKETS_DIR` and `TK_SCRIPT` env vars.

Vendored plugins in `bin/` (relative to this skill's directory):
- `ticket-query` — JSON output with jq filtering
- `ticket-migrate-beads` — Import from `.beads/issues.jsonl`

Use `tk super <cmd>` to bypass plugins and run built-in commands directly.
