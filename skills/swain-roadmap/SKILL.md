---
name: swain-roadmap
description: "Refresh and display the project roadmap. Regenerates ROADMAP.md from the artifact graph (quadrant chart, Eisenhower tables, Gantt timeline, dependency graph), creates it if missing, and opens it for review. Use when the user says 'roadmap', 'show roadmap', 'refresh roadmap', 'open roadmap', 'regenerate roadmap', 'update roadmap', 'priority matrix', or 'what does the roadmap look like'. Also use when any skill needs to ensure ROADMAP.md is fresh before consuming it."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Glob
metadata:
  short-description: Roadmap refresh and display
  version: 1.0.0
  author: cristos
  source: swain
---
<!-- swain-model-hint: haiku, effort: low -->

# Roadmap

Regenerates `ROADMAP.md` from the artifact graph and opens it. The heavy lifting is done by `chart.sh roadmap` in swain-design — this skill is the user-facing entry point.

## When invoked

### 1. Locate chart.sh

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
CHART_SH="$(find "$REPO_ROOT" -path '*/swain-design/scripts/chart.sh' -print -quit 2>/dev/null)"
```

If `chart.sh` is not found, tell the user swain-design is not installed and stop.

### 2. Regenerate ROADMAP.md

Always regenerate — the user invoked this skill because they want a fresh roadmap.

```bash
bash "$CHART_SH" roadmap
```

This writes `ROADMAP.md` to the project root with:
- **Quadrant chart** — priority matrix as PNG (falls back to inline Mermaid if `mmdc` is unavailable)
- **Legend** — epics grouped by quadrant with short IDs
- **Eisenhower tables** — Do First / Schedule / In Progress / Backlog with progress, unblock counts, and operator decision needs
- **Gantt timeline** — priority-staggered schedule with dependency links
- **Dependency graph** — blocking relationships across priority boundaries (only if dependencies exist)

### 3. Open ROADMAP.md

Always open the rendered file so the operator gets the full view with charts and diagrams. Never tell the operator to open it themselves — just do it.

```bash
open "$REPO_ROOT/ROADMAP.md"
```

### 4. Show CLI summary

ROADMAP.md contains tables, Mermaid diagrams, and image references that do not render in a terminal. Use the `--cli` flag to get a pre-formatted plain text summary:

```bash
bash "$CHART_SH" roadmap --cli
```

This outputs a deterministic, aligned summary grouped by Eisenhower quadrant (Do First, Schedule, In Progress, Backlog), with all first-degree children (EPICs, SPECs, SPIKEs) nested under their parent initiative. Show this output directly — do not reformat or filter it.

Say "ROADMAP.md refreshed and opened." before the CLI output.

### 6. Focus lane context

If a focus lane is set in `.agents/session.json`, mention it at the end.

```bash
FOCUS="$(bash "$(find "$REPO_ROOT" -path '*/swain-session/scripts/swain-focus.sh' -print -quit 2>/dev/null)" 2>/dev/null)"
```

If focus is set, note: "Focus: {FOCUS}. Use swain-status for focus-scoped recommendations."

## Freshness check (for other skills)

Other skills (like swain-status) can call chart.sh directly for staleness-based regeneration. This skill always regenerates unconditionally — it is the "force refresh" path.

## Error handling

- If chart.sh fails, show the error output and suggest running `swain-doctor`
- If ROADMAP.md exists but chart.sh is unavailable, show the existing (possibly stale) file with a staleness warning
- Never fail hard — show whatever is available
