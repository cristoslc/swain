---
title: "Gantt Visualization Options For Swain-Status"
artifact: SPIKE-021
track: status
status: Proposed
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
question: "What is the best rendering approach and library for adding Gantt-style timeline views to swain-status, given swain's terminal-first environment and zero-mandatory-install constraint?"
gate: Pre-development
risks-addressed:
  - Choosing a rendering target (terminal vs browser vs static file) that doesn't fit the operator's workflow
  - Picking a library with a complex install footprint that violates the zero-mandatory-install goal
  - Building a timeline renderer that can't consume swain's existing artifact frontmatter without heavy parsing work
linked-artifacts:
  - EPIC-018
evidence-pool: ""
---

# Gantt Visualization Options For Swain-Status

## Summary

<!-- Populated when transitioning to Complete. -->

## Question

What is the best rendering approach and library for adding Gantt-style timeline views to swain-status, given swain's terminal-first environment and zero-mandatory-install constraint?

## Go / No-Go Criteria

**Terminal rendering (Rich/Textual):**
- Can represent a readable Gantt bar chart in a terminal with color support
- No additional install beyond what swain-status already uses (Rich is already a dep)
- Bars can show phase names and durations legibly at typical terminal widths (80–220 cols)

**Browser-based rendering:**
- Opens in system default browser with no local server required (static HTML file)
- Library is CDN-embeddable or bundleable to a single HTML file (no npm/node required at runtime)
- Renders within 1 second for typical swain project sizes (< 100 artifacts)

**Static file rendering (SVG/PNG):**
- Produces a file that can be linked from artifact docs or committed to the repo
- Generation requires no GUI/display (headless)

## Investigation Areas

### 1. Terminal Gantt options

Evaluate:
- **Rich** (already a swain dep) — `rich.table`, bar rendering via progress columns, or custom renderables
- **Textual** (already used in MOTD) — widget possibilities for a timeline panel
- **plotext** — terminal plotting library; Gantt-style support
- **gantt-chart** CLI tools — any that accept JSON/YAML input and render to terminal?

Evaluate against:
- Can it render a multi-row Gantt (one row per epic/spec) with a shared time axis?
- Install footprint (already installed vs. new dep)
- Readability at 80 and 160 columns

### 2. Browser-based Gantt options

Evaluate:
- **Mermaid** (gantt diagram type) — can be embedded in a static HTML file; no server needed
- **Apache ECharts** — CDN-embeddable; has a Gantt-like custom chart example
- **Chart.js** with a horizontal bar chart — CDN-embeddable; approximate Gantt
- **Frappe Gantt** — open-source, lightweight, purpose-built Gantt library; CDN-embeddable
- **DHTMLX Gantt** (open-source edition) — feature-rich; license check needed for personal use

Evaluate against:
- Single static HTML file generation (no server, no npm)
- CDN-embeddable (renders offline if CDN cached, or needs internet)
- Swain artifact JSON → chart data mapping complexity

### 3. Date data availability in existing artifacts

Audit swain's artifact frontmatter and lifecycle tables to determine what date anchors are reliably present:
- `created` — always present (required frontmatter field)
- `last-updated` — always present
- Lifecycle table phase rows — present in all artifacts; parse `Date` column for phase transition timestamps
- What percentage of active artifacts have a `Complete` phase row (providing a real end date)?
- For in-progress artifacts: use `last-updated` as a soft end anchor, or "now" as the right edge?

### 4. Recommended output mode

Given findings from areas 1–3, recommend:
- Primary output mode for the first implementation (terminal or browser)
- Whether a second output mode is worth adding in the same epic or should be a follow-on

## Findings

<!-- Populated during Active phase. -->

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation; informs EPIC-018 implementation |
