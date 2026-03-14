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
<!-- swain-model-hint: sonnet, effort: low -->

# Status

Cross-cutting project status dashboard. Aggregates data from artifact lifecycle (specgraph), task tracking (tk), git, GitHub issues, and session state into an activity-oriented view.

## When invoked

Locate and run the status script from `skills/swain-status/scripts/swain-status.sh`:

```bash
# Find the script from the project root or installed skills directories
SKILL_DIR="$(find . .claude .agents -path '*/swain-status/scripts/swain-status.sh' -print -quit 2>/dev/null)"
bash "$SKILL_DIR" --refresh
```

If the path search fails, glob for `**/swain-status/scripts/swain-status.sh`.

The script's terminal output uses OSC 8 hyperlinks for clickable artifact links. Let the terminal output scroll by — it is reference data, not the primary output.

**After the script runs, present a structured agent summary** following the template in `references/agent-summary-template.md`. The agent summary is what the user reads for decision-making. It must lead with a Recommendation section (see below), then Decisions Needed, then Work Ready to Start, then reference data — following the template in `references/agent-summary-template.md`.

The script collects from five data sources:

1. **Artifacts** — specgraph cache (epic progress, ready/blocked items, dependency info)
2. **Tasks** — tk (in-progress, recently completed)
3. **Git** — branch, working tree state, recent commits
4. **GitHub** — open issues, issues assigned to the user
5. **Session** — bookmarks and context from swain-session

## Compact mode (MOTD integration)

The script supports `--compact` for consumption by swain-stage's MOTD panel:

```bash
bash skills/swain-status/scripts/swain-status.sh --compact
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

## Recommendation

The first thing the operator reads must be a single ranked recommendation — not a follow-up footnote, not a list of options.

**How to generate:**
1. From `.artifacts.ready[]` in the JSON cache, pick the item with the highest `unblock_count` (precomputed — no need to compute length)
2. If there are ties, prefer decision-type artifacts (ADR, SPEC needing review) over implementation items
3. Write exactly one `**Action:**` sentence (e.g., "Approve SPEC-030")
4. Write exactly one `**Why:**` sentence naming unblock count and artifact IDs (e.g., "Approving it unblocks SPEC-031, SPEC-032, SPEC-033 — highest downstream leverage of all actionable items.")
5. If no ready items exist, omit the section entirely

Do NOT offer multiple options. One recommendation, one reason.

## Active epics with all specs resolved

When an Active epic has `progress.done == progress.total`:
- Show "→ ready to close" in the Readiness column of the Epic Progress table
- Do NOT show it in the Work Ready to Start bucket (it's not implementation work)
- Do NOT show it as "work on child specs"

## Settings

Read from `swain.settings.json` (project) and `~/.config/swain/settings.json` (user override).

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `status.cacheTTL` | number | `120` | Cache time-to-live in seconds |

## Session bookmark

After presenting status, update the bookmark with the most actionable highlight: `bash "$(find . .claude .agents -path '*/swain-session/scripts/swain-bookmark.sh' -print -quit 2>/dev/null)" "Checked status — {key highlight}"`

## Error handling

- If specgraph is unavailable: skip artifact section, show other data
- If tk is unavailable: skip task section
- If gh CLI is unavailable or no GitHub remote: skip issues section
- If `.agents/session.json` doesn't exist: skip bookmark
- Never fail hard — show whatever data is available
