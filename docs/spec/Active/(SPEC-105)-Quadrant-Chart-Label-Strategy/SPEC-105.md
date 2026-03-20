---
title: "Quadrant chart label strategy"
artifact: SPEC-105
track: implementable
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: enhancement
parent-epic: EPIC-038
parent-initiative: ""
linked-artifacts:
  - SPEC-104
depends-on-artifacts:
  - SPEC-102
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Quadrant chart label strategy

## Problem Statement

The Mermaid `quadrantChart` renders point labels inline next to each dot. When items cluster (especially in the Backlog quadrant where 10+ items share similar coordinates), labels overlap into an unreadable pile. Labels also clip at chart boundaries — items near the right or bottom edge get truncated by the chart frame. The current mitigation (shorter titles, jitter) helped but doesn't solve the fundamental problem: inline labels don't scale past ~8 items.

## External Behavior

**Inputs:** `chart.sh roadmap` with 20+ epics
**Expected output:** A quadrant chart where every item is identifiable without label overlap or clipping

## Acceptance Criteria

- **Given** 20+ epics in the quadrant chart, **When** rendered in Typora or GitHub at default zoom, **Then** no labels overlap or clip at chart boundaries
- **Given** a short label on a point, **When** the user wants full context, **Then** a legend table immediately below the chart maps each label to its full epic title and initiative
- **Given** the Backlog quadrant with 10+ items, **When** rendered, **Then** individual items remain distinguishable (not a text pile)
- The solution must stay within Mermaid's `quadrantChart` capabilities — no external rendering or chart library changes

## Chosen Approach: Pre-rendered PNG + Legend in Markdown Table

Prototyped and validated: render the quadrant chart to PNG via `mmdc` (mermaid-cli), then embed in a markdown table with the legend in the adjacent cell. This achieves true side-by-side layout.

```markdown
| Priority Matrix | Legend |
|:---:|:---|
| ![Priority Matrix](assets/quadrant.png) | **Do First** ... |
```

**Chart rendering:** Use short ID labels (`E31`, `E17`, etc.) as point names in the Mermaid source. Render to PNG via `mmdc -i quadrant.mmd -o assets/quadrant.png -w 800 -b transparent`. The PNG is committed alongside ROADMAP.md.

**Legend format:** Grouped by Eisenhower quadrant (Do First, Schedule, In Progress, Backlog). Each entry is `E{NN} {Epic Title}` with hyperlink. Use markdown line breaks (two trailing spaces), not `<br/>` tags — Typora renders `<br/>` as literal text inside table cells.

**Why this works:**
- Eliminates label collision entirely — 2-3 character labels never overlap on the chart
- Side-by-side layout works in standard markdown tables (image + text)
- Renders in Typora, GitHub (images always work, unlike Mermaid quadrantChart), and VS Code
- Single compiled ROADMAP.md document with assets in a sibling directory

**Dependencies:**
- `mmdc` (mermaid-cli) — must be checked by swain-doctor/swain-init. Graceful degradation: if mmdc is not available, fall back to inline Mermaid block (no side-by-side, but still functional).

**Rejected alternatives:**
- Inline Mermaid + CSS side-by-side — Typora ignores `style` attributes on divs (flex, float, grid all fail)
- Mermaid inside HTML `<td>` — Typora doesn't render Mermaid blocks inside HTML table cells
- Mermaid theming (`pointLabelFontSize`) — reduces text size but doesn't prevent overlap at density
- Longer labels with jitter — doesn't scale past ~8 items in a quadrant

## Scope & Constraints

- Must stay within Mermaid — no SVG post-processing, no image rendering
- Legend table should use the same hyperlink format as the Eisenhower tables (relative links to artifact docs)
- Solution should degrade gracefully if rendered in a context without Mermaid support (GitHub mobile, plain text) — the legend table alone should be informative

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | | Initial creation |
