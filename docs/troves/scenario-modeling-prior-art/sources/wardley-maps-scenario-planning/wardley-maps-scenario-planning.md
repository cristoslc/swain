---
title: "Wardley Maps — Strategic Landscape with Assumption Visualization"
source-url: https://wardleymaps.com
source-type: web-page
fetched: 2026-04-28
transcript-source: web-search-synthesis
---

# Wardley Maps — Strategic Scenario Planning

**Sources:** wardleymaps.com, wardleyleadershipstrategies.com, theuncertaintyproject.org, lethain.com

## Summary

A Wardley Map plots a value chain (user needs → components → commodities) on a two-axis grid: value chain (Y) and evolution stage (X: Genesis → Custom → Product → Commodity). It makes strategic assumptions visible and comparable. "Red arrows" indicate expected future movement. Multiple maps model alternative strategic scenarios.

## The Primitives

### Single Map as Shared Assumption Set

A Wardley Map represents the team's shared situational awareness and assumptions. Every element's position on the evolution axis is a claim about how evolved/commoditized that component is. The map is wrong by definition — it is a *hypothesis*, not a fact. This makes disagreement legible: "I think payments is a product; you think it's custom. Let's draw both and see what downstream choices change."

### Red Arrows (Future State Overlay)

Red arrows on a Wardley Map indicate expected future movement. "This component will evolve from custom to product in 18 months." Multiple arrows create a future-state scenario overlay on the current-state map. This is structurally identical to Kustomize overlays — same base, different delta annotations.

### Multiple Maps as Scenario Comparison

Strategic scenario analysis with Wardley Maps produces multiple maps:
- Map A: "if competitor X enters the market" — their presence shifts the evolution stage of several components.
- Map B: "if we build capability Y" — different components appear, dependencies shift.

Teams compare maps side by side to identify where strategic choices diverge. The comparison is visual, not automated.

## Operator Invocation

1. Start with the current-state map (what we know now).
2. Add red arrows for expected future state.
3. Clone the map and modify specific components for each alternative scenario.
4. Compare maps to find where decisions "branch" — where different assumptions produce meaningfully different strategic positions.

Tools: Miro, OWM (Online Wardley Maps), Wardley Maps in Figma. No tool automates the comparison — it is always visual/manual.

## Relevance to swain Scenario Modeling

Wardley Maps are the most conceptually aligned prior art:
- The **current-state map = swain's canonical artifact graph**.
- **Red arrows = swain's phase transitions or pending ADR changes**.
- **Alternative maps = swain's named scenarios**.
- The comparison question ("where do strategic choices diverge?") maps directly to swain's "how does the artifact tree change between scenarios?"

The Wardley community's lesson: maps are most useful when they make *disagreements* legible. swain scenarios should surface where alternative ADR states produce materially different artifact trees — not just show a different tree, but highlight the divergence.

**Key lesson:** Model disagreement, not just alternatives. A scenario feature is most valuable when it shows *where* two scenarios diverge, not just *what* each scenario contains.
