---
title: "Scope Progress Visualization Options For Swain-Status"
artifact: SPIKE-021
track: status
status: Proposed
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
question: "What is the best rendering approach and library for adding scope progress visualizations to swain-status, given swain's terminal-first environment and zero-mandatory-install constraint?"
gate: Pre-development
risks-addressed:
  - Choosing a rendering target (terminal vs browser vs static file) that doesn't fit the operator's workflow
  - Picking a library with a complex install footprint that violates the zero-mandatory-install goal
  - Building a progress renderer that can't consume swain's existing specgraph/frontmatter output without heavy parsing work
linked-artifacts:
  - EPIC-018
trove: ""
---

# Scope Progress Visualization Options For Swain-Status

## Summary

<!-- Populated when transitioning to Complete. -->

## Question

What is the best rendering approach and library for adding scope progress visualizations to swain-status, given swain's terminal-first environment and zero-mandatory-install constraint? The visualization should communicate work completed vs. remaining in terms of artifact counts (e.g., "10 of 15 specs done"), not time estimates.

## Go / No-Go Criteria

**Terminal rendering (Rich/Textual):**
- Can represent a multi-epic progress breakdown with per-epic spec counts (done / in-progress / blocked / total)
- No additional install beyond what swain-status already uses (Rich is already a dep)
- Readable at typical terminal widths (80–220 cols)

**Browser-based rendering:**
- Opens in system default browser with no local server required (static HTML file)
- Library is CDN-embeddable or bundleable to a single HTML file (no npm/node required at runtime)
- Renders within 1 second for typical swain project sizes (< 100 artifacts)

**Static file rendering (SVG/PNG):**
- Produces a file that can be linked from artifact docs or committed to the repo
- Generation requires no GUI/display (headless)

## Investigation Areas

### 1. Terminal progress visualization options

Evaluate:
- **Rich** (already a swain dep) — `rich.progress`, `rich.table`, stacked bar columns, or `rich.panel` layouts
- **Textual** (already used in MOTD) — widget possibilities for a live progress panel
- **plotext** — terminal plotting library; horizontal bar or stacked bar support

Evaluate against:
- Can it render a per-epic breakdown showing counts (done / in-progress / blocked) clearly?
- Install footprint (already installed vs. new dep)
- Readability at 80 and 160 columns

### 2. Browser-based progress visualization options

Evaluate:
- **Mermaid** (pie or xychart types) — embeddable in static HTML; no server needed
- **Apache ECharts** — CDN-embeddable; stacked bar and pie/donut support
- **Chart.js** — CDN-embeddable; horizontal stacked bar charts
- **D3.js** — CDN-embeddable; highly flexible but higher authoring cost

Evaluate against:
- Single static HTML file generation (no server, no npm)
- CDN-embeddable (renders offline if CDN cached, or needs internet)
- Swain specgraph JSON → chart data mapping complexity

### 3. Data availability from existing artifacts

Audit what swain's specgraph and frontmatter reliably provide for scope accounting:
- `status` / `phase` fields — present in all artifacts; drives done/in-progress/blocked classification
- `depends-on-artifacts` — present; drives blocked count
- Child spec enumeration via specgraph — is this reliable enough to compute per-epic ratios?
- Edge cases: specs with no parent epic, orphaned specs, specs in multiple phases

### 4. Recommended output mode

Given findings from areas 1–3, recommend:
- Primary output mode for the first implementation (terminal or browser)
- Whether a second output mode is worth adding in the same epic or should be a follow-on

## Findings

<!-- Populated during Active phase. -->

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation; pivoted from Gantt/time-based to scope/count-based; informs EPIC-018 implementation |
