# Specwatch Guide

Reference for `specwatch.sh` subcommands, log format, and watch mode.

## Subcommands

| Command | What it does |
|---------|-------------|
| `scan` | Run a full stale-reference scan (no watcher needed) |
| `watch` | Start background filesystem watcher (requires `fswatch`) |
| `bd-sync` | Check artifact/bd sync state (open bd items for implemented specs, etc.) |
| `phase-fix` | Move artifacts whose phase directory doesn't match frontmatter status |
| `stop` | Stop a running watcher |
| `status` | Show watcher status and log summary |
| `touch` | Refresh the sentinel keepalive timer |

## Log format

Findings are written to `.agents/specwatch.log` in a structured format. This file is a runtime artifact — add `specwatch.log` to your `.gitignore` if it isn't already.

```
STALE <source-file>:<line>
  broken: <relative-path-as-written>
  found: <suggested-new-path>
  artifact: <TYPE-NNN>

STALE_REF <source-file>:<line> (frontmatter)
  field: <frontmatter-field-name>
  target: <TYPE-NNN>
  resolved: NONE
  issue: unresolvable artifact ID

WARN <source-file>:<line> (frontmatter)
  field: <frontmatter-field-name>
  target: <TYPE-NNN>
  resolved: <relative-path-to-target>
  issue: <target is Abandoned | source is X but target is still Y>
```

## What the scan checks

1. **Markdown link paths** — `[text](path/to/file.md)` links where the target no longer exists. Suggests corrections by artifact ID lookup.
2. **Frontmatter artifact references** — all `depends-on`, `parent-*`, `linked-*`, `addresses`, `validates`, `affected-artifacts`, `superseded-by`, and `fix-ref` fields. For each artifact ID, resolves to a relative file path and checks both existence and semantic coherence (target in Abandoned/Rejected state, phase mismatches where the source is significantly more advanced than the target).

## Watch mode

The background `watch` mode (requires `fswatch`) uses macOS FSEvents for kernel-level file monitoring. It is available for long-running sessions but is not part of the default workflow. The sentinel-based inactivity timeout defaults to 1 hour (`SPECWATCH_TIMEOUT` env var to override).
