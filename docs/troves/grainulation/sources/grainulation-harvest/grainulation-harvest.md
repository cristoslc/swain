---
source-id: "grainulation-harvest"
title: "Harvest — Sprint Analytics and Prediction Calibration"
type: repository
url: "https://github.com/grainulation/harvest"
fetched: 2026-04-06T15:00:00Z
hash: "f0440d1edf7aaa71a682777ef3b2e33a4960f303a5d725ed16586b3af7d9147e"
highlights:
  - "grainulation-harvest.md"
selective: true
notes: "Read-only analytics layer — cross-sprint patterns, prediction scoring, knowledge decay detection"
---

# Harvest — Sprint Analytics and Prediction Calibration

**Tagline:** Are your decisions getting better?

Harvest is the analytics layer for research sprints. It looks across sprints to find patterns, score predictions against actual outcomes, and surface knowledge that has gone stale.

## Install

```bash
npm install -g @grainulation/harvest
```

## What it does

- **Cross-sprint analysis** — claim type distributions, evidence quality, recurring themes.
- **Prediction calibration** — score past estimates against actual outcomes.
- **Decision patterns** — what research approaches lead to better results?
- **Knowledge decay** — which old claims need refreshing before they mislead you?
- **Sprint velocity** — how long do sprints take, where do they stall?
- **Retrospective reports** — dark-themed HTML reports for the team.

## Quick start

```bash
harvest analyze ./sprints/
harvest calibrate ./sprints/
harvest patterns ./sprints/
harvest decay ./sprints/ --days 60
harvest velocity ./sprints/
harvest report ./sprints/ -o retrospective.html
harvest trends ./sprints/ --json
harvest serve --root ./sprints/ --port 9096
harvest connect farmer --url http://localhost:9094
```

## Data format

Harvest reads standard wheat sprint data:

- `claims.json` — array of typed claims with `id`, `type`, `evidence`, `status`, `text`, `created`.
- `compilation.json` — compiled sprint state (optional, enriches analysis).
- Git history on `claims.json` — used for velocity and timing analysis.

## Design principles

- **Reads, never writes** — harvest is a pure analysis tool; it won't modify your sprint data.
- **Git-aware** — uses git log timestamps for velocity analysis when available.
- **Composable** — each module (analyzer, calibration, patterns, decay, velocity) works independently.

## Zero dependencies

Node built-in modules only.

## License

MIT
