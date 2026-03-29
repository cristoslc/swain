---
name: swain-status
description: "Cross-cutting project status dashboard. Shows active epics with progress ratios, actionable next steps, blocked items, in-progress tasks, GitHub issues, and session context. Produces rich terminal output with clickable links. Triggers on: 'project status', 'swain status', 'what's next', 'dashboard', 'overview', 'where are we', 'what should I work on', 'am I blocked', 'what needs review', 'show me priorities'."
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

Cross-cutting project status dashboard. Aggregates data from artifact lifecycle (`swain chart`), task tracking (tk), git, GitHub issues, and session state into an activity-oriented view.

## Roadmap freshness

The status script includes a staleness check that regenerates ROADMAP.md if it is missing or older than any doc artifact. This runs automatically — no separate invocation needed.

For a full roadmap refresh (unconditional regeneration), use `swain-roadmap` instead.

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

1. **Artifacts** — `swain chart` vision-rooted hierarchy (epic progress, ready/blocked items, dependency info). Use `bash "$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-design/scripts/chart.sh' -print -quit 2>/dev/null)" recommend` for ranked artifact view; respects focus lane automatically.
2. **Tasks** — tk (in-progress, recently completed)
3. **Git** — branch, working tree state, recent commits
4. **GitHub** — open issues, issues assigned to the user
5. **Session** — bookmarks and context from swain-session

## Compact mode

The script supports `--compact` for concise output:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
STATUS_SCRIPT="$(find "$REPO_ROOT" -path '*/swain-status/scripts/swain-status.sh' -print -quit 2>/dev/null)"
[ -n "$STATUS_SCRIPT" ] && bash "$STATUS_SCRIPT" --compact || echo "swain-status.sh not found"
```

This outputs 4-5 lines: branch, active epic progress, current task, ready count, assigned issue count.

## Cache

The script writes a JSON cache to the project-local agents directory:

```
.agents/status-cache.json
```

- **TTL:** 120 seconds (configurable via `status.cacheTTL` in settings)
- **Force refresh:** `--refresh` flag bypasses TTL
- **JSON access:** `--json` flag outputs raw cache for programmatic use

The MOTD can read this cache cheaply between full refreshes.

**Migration:** If `.agents/status-cache.json` does not exist but `~/.claude/projects/<project-path-slug>/memory/status-cache.json` does, read the old location once and write to the new location going forward.

## Recommendation

The recommendation uses a scoring formula:

```
score = unblock_count × vision_weight
```

Where `vision_weight` is inherited from the artifact's Vision ancestor (high=3, medium=2, low=1, default=medium). Read `.priority.recommendations[0]` from the JSON cache for the top-ranked item.

Tiebreakers (applied in order):
1. Higher decision debt in the artifact's vision
2. Decision-type artifacts over implementation-type
3. Artifact ID (deterministic fallback)

When a focus lane is set, recommendations are scoped to that vision/initiative. Peripheral visions are summarized separately (see Peripheral Awareness).

If attention drift is detected for the recommended item's vision, include it as context in the recommendation.

## Mode Inference

swain-status infers the operating mode from context (first match wins):

1. Both specs in review AND strategic decisions pending → ask: "Steering or reviewing?"
2. Specs awaiting operator review (agent finished, needs sign-off) → **detail mode**
3. Focus lane set with pending strategic decisions → **vision mode** within that lane
4. No specs in review, decisions piling up → **vision mode**
5. Nothing actionable in either mode → **vision mode** (show the master plan mirror)

Once the operator answers, swain remembers for the session via swain-session bookmark.

## Focus Lane

The operator can set a focus lane via swain-session to scope recommendations to a single vision or initiative:

```bash
bash "$(find . .claude .agents -path '*/swain-session/scripts/swain-focus.sh' -print -quit 2>/dev/null)" set VISION-001
```

When set, `.priority.recommendations` only includes items under that vision. Non-focus visions appear in the Peripheral Awareness section.

## Peripheral Awareness

When a focus lane is set, non-focus visions with pending decisions are summarized:
"Meanwhile: [Vision] has N pending decisions (weight: W)"

This is a mirror, not a recommendation — the operator decides when accumulation warrants redirection.

## Active epics with all specs resolved

When an Active epic has `progress.done == progress.total`:
- Show "→ ready to close" in the Readiness column of the Epic Progress table
- Do NOT show it in the Work Ready to Start bucket (it's not implementation work)
- Do NOT show it as "work on child specs"

## Decisions Needed (roadmap integration)

After the existing status output sections, surface top decision items from the roadmap. This section uses the Eisenhower classification from `chart.sh roadmap --json`.

### Data collection

```bash
bash "$(find . -path '*/swain-design/scripts/chart.sh' -print -quit)" roadmap --json
```

### Filtering

1. **Focus lane scoping:** If a focus lane is set, filter items to that Vision only.
2. **Eisenhower quadrant filter:** Show items from "Do First" and "Schedule" quadrants. Classification criteria:
   - **Important:** weight >= 3
   - **Urgent:** active status or score > 0
3. **Operator decision filter:** Show items that need operator decisions:
   - Status "Proposed" — needs activate or drop decision
   - `children_total == 0` — needs decomposition into child specs
   - `children_complete == children_total` and `children_total > 0` — ready to complete/close

### Display

- Limit to top 5 items, ordered by weight descending then score descending.
- Format each as an actionable prompt, not a passive list entry. Examples:
  - `EPIC-038 PR-Only Agent Guardrails — **needs decomposition** (0 specs, high priority)`
  - `EPIC-024 GitHub Issue Polling — **activate or drop?** (Proposed, high priority)`
  - `EPIC-012 Session Atomization — **ready to complete** (4/4 specs done)`
- If no items match, omit the section entirely — do not show an empty heading.

### Degradation

If `chart.sh roadmap --json` fails or returns empty data, skip the Decisions Needed section silently and continue with the rest of the status output.

## Settings

Read from `swain.settings.json` (project) and `~/.config/swain/settings.json` (user override).

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `status.cacheTTL` | number | `120` | Cache time-to-live in seconds |

## Session bookmark

After presenting status, update the bookmark with the most actionable highlight: `bash "$(find . .claude .agents -path '*/swain-session/scripts/swain-bookmark.sh' -print -quit 2>/dev/null)" "Checked status — {key highlight}"`

## Error handling

- If chart.sh / specgraph is unavailable: skip artifact section, show other data
- If tk is unavailable: skip task section
- If gh CLI is unavailable or no GitHub remote: skip issues section
- If `.agents/session.json` doesn't exist: skip bookmark
- Never fail hard — show whatever data is available
