---
name: swain-status
description: "Cross-cutting project status dashboard. Shows active epics with progress ratios, actionable next steps, blocked items, in-progress tasks, GitHub issues, and session context. Produces rich terminal output with clickable links. Triggers on: 'status', 'progress', 'what's next', 'dashboard', 'overview', 'where are we', 'what should I work on'."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Glob, Grep
metadata:
  short-description: Cross-cutting project status dashboard
  version: 1.0.0
  author: cristos
  source: swain
---

# Status

Cross-cutting project status dashboard. Aggregates data from artifact lifecycle (specgraph), task tracking (bd), git, GitHub issues, and session state into an activity-oriented view.

## When invoked

Run the status script and present its output verbatim (it contains OSC 8 terminal hyperlinks for clickable file paths and GitHub URLs):

```bash
bash scripts/swain-status.sh --refresh
```

The script collects from five data sources:

1. **Artifacts** — specgraph cache (epic progress, ready/blocked items, dependency info)
2. **Tasks** — bd (in-progress, recently completed)
3. **Git** — branch, working tree state, recent commits
4. **GitHub** — open issues, issues assigned to the user
5. **Session** — bookmarks and context from swain-session

## Output structure

The output is ordered by actionability, not by data source:

1. **Session bookmark** — if one exists, show it first ("where you left off")
2. **Pipeline** — branch, dirty state, last commit
3. **Active Epics** — each epic with progress ratio (e.g., 4/7 specs resolved) and child spec status
4. **Actionable Now** — unblocked artifacts ready for work, with clickable file links
5. **Blocked** — artifacts waiting on dependencies
6. **Tasks** — in-progress and recently completed bd tasks
7. **GitHub Issues** — assigned issues first, then open issues, with clickable links
8. **Artifact counts** — summary footer

## Clickable links

The script emits OSC 8 hyperlinks that work in iTerm2 and other modern terminals:

- **File paths** → `file:///path/to/doc` — opens in default application
- **GitHub issue URLs** → `https://github.com/owner/repo/issues/N` — opens in browser
- **Artifact IDs** → linked to their source file on disk

Present the script output directly — do not reformat or strip escape sequences.

## Compact mode (MOTD integration)

The script supports `--compact` for consumption by swain-stage's MOTD panel:

```bash
bash scripts/swain-status.sh --compact
```

This outputs 4-5 lines suitable for the MOTD box: branch, active epic progress, current task, ready count, assigned issue count.

## Cache

The script writes a JSON cache to the Claude Code memory directory:

```
~/.claude/projects/<project-slug>/memory/status-cache.json
```

- **TTL:** 120 seconds (configurable via `status.cacheTTL` in settings)
- **Force refresh:** `--refresh` flag bypasses TTL
- **JSON access:** `--json` flag outputs raw cache for programmatic use

The MOTD can read this cache cheaply between full refreshes.

## Follow-up actions

After presenting status, suggest relevant next steps based on what the data shows:

| Condition | Suggestion |
|-----------|------------|
| Actionable items exist | "Ready to pick one up? Tell me which artifact to work on." |
| Blocked items exist | "Want to look at what's blocking {ID}?" |
| GitHub issues assigned | "Want to triage your assigned issues?" |
| No active tasks | "No tasks in progress. Want to start one from the ready list?" |
| Session bookmark exists | "Want to pick up where you left off?" |

Offer one or two suggestions, not all of them.

## Settings

Read from `swain.settings.json` (project) and `~/.config/swain/settings.json` (user override).

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `status.cacheTTL` | number | `120` | Cache time-to-live in seconds |

## Error handling

- If specgraph is unavailable: skip artifact section, show other data
- If bd is unavailable: skip task section
- If gh CLI is unavailable or no GitHub remote: skip issues section
- If session.json doesn't exist: skip bookmark
- Never fail hard — show whatever data is available
