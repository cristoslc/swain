---
source-id: "grainulation-silo"
title: "Silo — Reusable Knowledge for Research Sprints"
type: repository
url: "https://github.com/grainulation/silo"
fetched: 2026-04-06T15:00:00Z
hash: "5b47000dbe913b723e5b491c04a515d234e6e8f0ed955337bf3eb9f44089deca"
highlights:
  - "grainulation-silo.md"
selective: true
notes: "Persistent knowledge packs — 11 built-in packs with 131 curated claims"
---

# Silo — Reusable Knowledge for Research Sprints

**Tagline:** Reusable knowledge for research sprints.

Silo stores battle-tested constraint sets, risk patterns, and decision templates as reusable claim libraries. Pull a starter pack into any sprint with one command instead of starting from scratch.

## Install

```bash
npm install -g @grainulation/silo
```

## Quick start

```bash
silo pull compliance --into ./claims.json
silo pull compliance --into ./claims.json --type constraint
silo search "encryption at rest"
silo store "q4-migration-findings" --from ./claims.json
silo list
```

## Built-in packs (11 packs, 131 curated claims)

| Pack | Claims | Contents |
|------|--------|----------|
| `api-design` | 13 | REST conventions, versioning, pagination, error formats, GraphQL tradeoffs |
| `architecture` | 12 | Monolith vs micro, build vs buy, SQL vs NoSQL decision claims |
| `ci-cd` | 12 | CI/CD pipeline patterns, caching, rollback strategies |
| `compliance` | 14 | HIPAA, SOC 2, GDPR constraint sets with regulatory citations |
| `data-engineering` | 12 | ETL patterns, data quality, warehouse design |
| `frontend` | 12 | Frontend architecture, performance, accessibility patterns |
| `migration` | 10 | Database/cloud/framework migration risks and patterns |
| `observability` | 12 | Logging, metrics, tracing, alerting patterns |
| `security` | 12 | Security constraints, threat models, authentication patterns |
| `team-process` | 12 | Team workflow, code review, incident response patterns |
| `testing` | 10 | Testing strategies, coverage, test architecture |

## CLI

| Command | Description |
|---------|-------------|
| `silo list` | List all stored collections |
| `silo pull <pack> --into <file>` | Pull claims into a claims file |
| `silo store <name> --from <file>` | Store claims from a sprint |
| `silo search <query>` | Full-text search across claims |
| `silo packs` | List available knowledge packs |
| `silo publish <name> --collections <ids>` | Bundle collections into a pack |
| `silo install <file>` | Install a pack from a JSON file |

## How it works

Silo uses the filesystem for storage (`~/.silo` by default). No database, no network calls, no accounts.

When you `pull`, Silo re-prefixes claim IDs to avoid collisions, deduplicates against existing claims, and merges into your claims.json.

When you `store`, Silo hashes the content for versioning, saves to `~/.silo/claims/`, and updates the search index.

## Programmatic API

```js
const { Store } = require("@grainulation/silo/lib/store");
const { Search } = require("@grainulation/silo/lib/search");
const { ImportExport } = require("@grainulation/silo/lib/import-export");
```

## Zero dependencies

Node built-in modules only. Filesystem-based storage. Works offline.

## License

MIT
