---
source-id: "grainulation-orchard"
title: "Orchard — Multi-Sprint Orchestration and Dependency Tracking"
type: repository
url: "https://github.com/grainulation/orchard"
fetched: 2026-04-06T15:00:00Z
hash: "2e3a3bf319fafc7ef3e5e90048a5f8829209d31b95892f5e3349836bcc89d411"
highlights:
  - "grainulation-orchard.md"
selective: true
notes: "Multi-sprint coordinator — dependency graphs, cross-sprint conflict detection, team assignment"
---

# Orchard — Multi-Sprint Orchestration and Dependency Tracking

**Tagline:** Multi-sprint orchestration and dependency tracking.

Orchard coordinates parallel research across teams with dependency graphs, conflict detection, and unified dashboards. One command to see 12 active sprints at once.

## Install

```bash
npm install -g @grainulation/orchard
```

## Quick start

Create `orchard.json` in your project root:

```json
{
  "sprints": [
    {
      "path": "./sprints/auth-scaling",
      "question": "How should we scale auth for 10x traffic?",
      "depends_on": [],
      "assigned_to": "alice",
      "deadline": "2026-03-20",
      "status": "active"
    },
    {
      "path": "./sprints/data-migration",
      "question": "What's the safest migration path for the user table?",
      "depends_on": ["./sprints/auth-scaling"],
      "assigned_to": "bob",
      "deadline": "2026-03-25",
      "status": "active"
    }
  ]
}
```

Then:

```bash
orchard plan        # Show the dependency graph
orchard status      # Check status of all sprints
orchard sync        # Sync status from sprint directories
orchard dashboard   # Generate unified HTML dashboard
```

## What it does

- **Sprint dependency graphs** — "sprint B needs sprint A's results first".
- **Cross-sprint conflict detection** — when two sprints reach opposing conclusions.
- **Team assignment** — who's running which sprint.
- **Unified status dashboard** across all active sprints.
- **Sprint scheduling and deadline tracking**.
- **Topological sort** — determines execution order, flags cycles.

## CLI

| Command | Description |
|---------|-------------|
| `orchard plan` | Show sprint dependency graph |
| `orchard status` | Show status of all tracked sprints |
| `orchard assign <path> <person>` | Assign a person to a sprint |
| `orchard sync` | Sync sprint states from directories |
| `orchard dashboard [outfile]` | Generate unified HTML dashboard |
| `orchard init` | Initialize orchard.json |
| `orchard serve` | Start the portfolio dashboard web server |

## Conflict detection

Orchard flags two types of cross-sprint conflicts:

1. **Opposing recommendations** — two sprints make recommendations on the same topic that contradict.
2. **Constraint-recommendation tension** — one sprint's constraints conflict with another's recommendations.

## Zero dependencies

Node built-in modules only.

## License

MIT
