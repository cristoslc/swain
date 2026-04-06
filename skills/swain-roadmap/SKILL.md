---
name: swain-roadmap
description: "Refresh and display the project roadmap and status dashboard. Regenerates ROADMAP.md from the artifact graph (quadrant chart, Eisenhower tables, Gantt timeline, dependency graph), creates it if missing, and opens it for review. Also serves as the project status dashboard — shows active epics, progress, actionable next steps, blocked items, and recommendations. Use when the user says 'roadmap', 'show roadmap', 'refresh roadmap', 'status', 'dashboard', 'what's next', 'overview', 'where are we', 'what should I work on', 'show me priorities', 'priority matrix', or 'what does the roadmap look like'. Also use when any skill needs to ensure ROADMAP.md is fresh before consuming it."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Glob
metadata:
  short-description: Roadmap refresh, display, and status dashboard
  version: 2.0.0
  author: cristos
  source: swain
---
<!-- swain-model-hint: haiku, effort: low -->

# Roadmap

<!-- session-check: SPEC-121 -->
Before proceeding with any state-changing operation, check for an active session:
```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/swain-session-check.sh" 2>/dev/null
```
If the JSON output has `"status"` other than `"active"`, inform the operator: "No active session — start one with `/swain-init`?" Proceed if they dismiss.

Regenerates `ROADMAP.md` from the artifact graph and opens it. The heavy lifting is done by `chart.sh roadmap` in swain-design — this skill is the user-facing entry point.

## When invoked

### 1. Locate chart.sh

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
CHART_SH="$REPO_ROOT/.agents/bin/chart.sh"
```

If `chart.sh` is not found, tell the user swain-design is not installed and stop.

### 2. Regenerate roadmap

Parse the argument: if the user provided an artifact ID (e.g., `swain-roadmap VISION-001`), set `SCOPE_ID` to that ID. Otherwise, `SCOPE_ID` is empty.

**If `SCOPE_ID` is set:**

```bash
bash "$CHART_SH" roadmap --scope "$SCOPE_ID"
```

This writes a `roadmap.md` to the scoped artifact's folder.

**If `SCOPE_ID` is empty:**

```bash
bash "$CHART_SH" roadmap
```

This writes `ROADMAP.md` to the project root AND regenerates all per-Vision and per-Initiative `roadmap.md` slices in their respective artifact folders.

The project-wide ROADMAP.md contains:
- **Quadrant chart** — priority matrix as PNG (falls back to inline Mermaid if `mmdc` is unavailable)
- **Legend** — epics grouped by quadrant with short IDs
- **Eisenhower tables** — Do First / Schedule / In Progress / Backlog with progress, unblock counts, and operator decision needs
- **Gantt timeline** — priority-staggered schedule with dependency links
- **Dependency graph** — blocking relationships across priority boundaries (only if dependencies exist)

Each per-artifact slice contains: intent summary, child artifact table with links and progress, aggregate progress bar, recent git commits, and an Eisenhower priority subset.

### 2.5. Post-process intent placeholders

After chart.sh completes, scan the output file(s) for `{{INTENT: <ID>}}` placeholders. For each:

1. Read the source artifact markdown.
2. Extract the first sentence of `## Value Proposition` (for Visions) or `## Goal / Objective` (for Initiatives).
3. Replace the `{{INTENT: <ID>}}` marker with the extracted sentence.
4. Write the file back.

If the section cannot be found, leave the placeholder as-is (the operator can fill it in manually or wait for `brief-description` frontmatter to be populated via SPEC-144).

### 3. Open the roadmap

If `SCOPE_ID` was set, open the scoped slice. Look up the artifact's file path from the graph cache to find its folder:

```bash
ARTIFACT_FILE="$(bash "$CHART_SH" show "$SCOPE_ID" 2>/dev/null | grep -oE 'docs/[^ ]+' | head -1)"
if [ -n "$ARTIFACT_FILE" ]; then
    open "$REPO_ROOT/$(dirname "$ARTIFACT_FILE")/roadmap.md"
fi
```

If no scope, open the project-wide roadmap:

```bash
open "$REPO_ROOT/ROADMAP.md"
```

Always open the rendered file so the operator gets the full view with charts and diagrams. Never tell the operator to open it themselves — just do it.

### 4. Show CLI summary

ROADMAP.md contains tables, Mermaid diagrams, and image references that do not render in a terminal. Use the `--cli` flag to get a pre-formatted plain text summary:

```bash
bash "$CHART_SH" roadmap --cli
```

This outputs a deterministic, aligned summary grouped by Eisenhower quadrant (Do First, Schedule, In Progress, Backlog), with all first-degree children (EPICs, SPECs, SPIKEs) nested under their parent initiative. Show this output directly — do not reformat or filter it.

Say "ROADMAP.md refreshed and opened." before the CLI output. For scoped runs, say "Roadmap slice for {SCOPE_ID} refreshed and opened." instead.

### Context-rich display

When listing roadmap items (Eisenhower quadrants, Gantt timeline), present each artifact as a context line instead of a bare ID:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/artifact-context.sh" <ID> 2>/dev/null
```

Fall back to `<ID> — <title>` if the utility is unavailable.

### 6. Focus lane context

If a focus lane is set in `.agents/session.json`, mention it at the end.

```bash
FOCUS="$(bash "$REPO_ROOT/.agents/bin/swain-focus.sh" 2>/dev/null)"
```

If focus is set, note: "Focus: {FOCUS}. Recommendations are scoped to this lane."

## Freshness check (for other skills)

Other skills can call chart.sh directly for staleness-based regeneration. This skill always regenerates unconditionally — it is the "force refresh" path.

## Status Dashboard (ADR-023, formerly SPEC-122)

When the operator says "status", "what's next", "dashboard", "overview", "where are we", or "what should I work on", run the status script:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
STATUS_SCRIPT="$REPO_ROOT/.agents/bin/swain-status.sh"
[ -f "$STATUS_SCRIPT" ] && bash "$STATUS_SCRIPT" --refresh || echo "status dashboard script not found"
```

For compact mode (MOTD): `bash "$STATUS_SCRIPT" --compact`

### Cache

Status writes to `.agents/status-cache.json` with 120-second TTL. Use `--refresh` to bypass, `--json` for raw output.

### Recommendation

Read `.priority.recommendations[0]` from the JSON cache. When a focus lane is set, recommendations scope to that vision/initiative.

### Mode Inference

1. Both specs in review AND strategic decisions pending -> ask operator
2. Specs awaiting review -> detail mode
3. Focus lane + pending decisions -> vision mode
4. Nothing actionable -> vision mode (master plan mirror)

### Decisions Needed (roadmap integration)

Uses `chart.sh roadmap --json` for Eisenhower classification. Show top 5 items from "Do First" and "Schedule" quadrants that need operator decisions.

## Error handling

- If chart.sh fails, show the error output and suggest running `swain-doctor`
- If ROADMAP.md exists but chart.sh is unavailable, show the existing (possibly stale) file with a staleness warning
- Never fail hard — show whatever is available
