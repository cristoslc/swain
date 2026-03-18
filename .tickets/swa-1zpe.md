---
id: swa-1zpe
status: open
deps: []
links: [swa-govf]
created: 2026-03-16T03:44:31Z
type: epic
priority: 2
assignee: Cristos L-C
external-ref: SPEC-052
---
# Vision-Rooted Chart Implementation Plan

Ingested from docs/superpowers/plans/2026-03-15-vision-rooted-chart.md. Goal: Create `swain chart` — a unified, vision-rooted hierarchy display that subsumes specgraph and provides lens-based filtering across all artifact views.. Architecture: New `VisionTree` renderer in the specgraph package renders vision-rooted trees from any node set. A `Lens` abstraction defines node selection, annotation, sort order, and default depth. `chart.sh` is the new shell entry point; `specgraph.sh` becomes a deprecated alias. The existing specgraph Python package (`graph.py`, `parser.py`, `priority.py`, etc.) is reused as-is for graph building and queries..

