---
title: "Knowledge Graph Tools — No Native Branching"
source-url: https://obsidian.md
source-type: web-page
fetched: 2026-04-28
transcript-source: web-search-synthesis
---

# Knowledge Graph Tools — Obsidian, Roam Research, Logseq

**Sources:** deepterm.app, scrintal.com, noduslabs.com, medium.com

## Summary

The leading personal knowledge management (PKM) tools — Obsidian, Roam Research, Logseq — use bidirectional linking to build knowledge graphs. None natively supports branching or forking the graph. All maintain a single canonical graph. The "alternative view" primitives they offer are filters and queries on the single canonical graph, not structural forks.

## Obsidian

- **Graph view:** Visual display of all notes and links. Filter by tag or path. No forking.
- **Canvas:** A spatial layout of notes and connections. Multiple canvases can exist, showing different subsets, but the underlying note graph is singular.
- **Dataview plugin:** SQL-like queries over notes. Produces different views of the same graph. No branching.
- **Version control:** Obsidian Sync has version history per note. The Git plugin tracks changes. Neither provides "what would my graph look like if note X had different content?"

## Roam Research

- **Block references:** More granular than Obsidian — references at the paragraph/block level, not page level.
- **Queries/filters:** Roam's native query syntax filters the graph view. Produces different views of the same graph.
- **Multiplayer:** Roam's multiplayer feature shows who edited what, but there are no branches or forks.
- No scenario modeling.

## Logseq

- **Queries:** Similar to Roam. Filters the single canonical graph.
- **Whiteboards:** Spatial canvas view (like Obsidian Canvas). Different display, same graph.
- No branching.

## The Gap

No PKM tool answers: "Show me my knowledge graph under the assumption that note X says Y instead of Z." The graph is always canonical. Alternative views are display filters (tags, queries, path limits), not structural alternatives.

## Why This Matters for swain

PKM tools have deeply explored "multiple views of one graph." They consistently solve it with **filters and queries** rather than branches. This is the "projection" pattern (same data, different display) vs. the "scenario" pattern (different data, same schema).

swain's artifact graph has both use cases:
- **Projection (covered by swain chart lenses):** `swain chart ready`, `swain chart debt` — different views of the same graph.
- **Scenario (uncovered):** "Show me the graph if ADR-046 were active" — structurally different data.

PKM tools don't cover the second use case. This confirms it is genuinely absent from existing tools.

**Key lesson:** The PKM ecosystem has exhausted the "query/filter" solution space for single-graph alternative views. Scenarios (structural alternatives) are genuinely different and require a different primitive.
