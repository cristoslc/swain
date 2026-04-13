---
source-id: "grainulation-wheat"
title: "Wheat — CI/CD for Technical Decisions"
type: repository
url: "https://github.com/grainulation/wheat"
fetched: 2026-04-06T15:00:00Z
hash: "59a2c76416533af6119d56c49c120f2e0c84e98f4a02808619cd1f63c67d8749"
highlights:
  - "grainulation-wheat.md"
selective: true
notes: "Core research engine — most-starred tool, primary entry point for the ecosystem"
---

# Wheat — CI/CD for Technical Decisions

**Tagline:** CI/CD for technical decisions.

Wheat is the core research engine of the grainulation ecosystem. It treats technical decisions like code: findings are validated as they come in, the compiler catches conflicts, and you can't ship a brief built on contradictions — same as you can't merge with failing tests.

## Quick start

```bash
npx @grainulation/wheat "Should we migrate to GraphQL?"
```

One command. Zero prompts. Sprint ready in under 3 seconds.

Then open your AI coding tool and start investigating:

```
/research "GraphQL performance vs REST"
/challenge r003
/blind-spot
/brief
```

Works with Claude Code, Cursor, GitHub Copilot, or standalone via CLI.

## Full MCP integration (optional)

```bash
claude mcp add wheat -- npx -y @grainulation/wheat-mcp
```

This gives Claude direct access to wheat's claims engine — add-claim, compile, search, status — without shelling out.

Sub-sprints: every MCP tool accepts an optional `dir` parameter to target a sub-sprint, letting you run multiple sprints without restarting the MCP server.

## How it works

Wheat is a continuous planning pipeline. Findings are validated as they come in:

```
You investigate  →  Claims accumulate  →  Compiler validates  →  Brief compiles
  /research          typed, evidence-graded   7-pass pipeline       backed by evidence
  /prototype
  /challenge
```

**Claim types:** constraint, factual, estimate, risk, recommendation, feedback.

**Evidence tiers:** stated → web → documented → tested → production.

The compiler runs 7 passes: type coverage, evidence strength, conflict detection, bias scan, and produces a confidence score. Unresolved conflicts block output.

## Commands

| Command | What it does |
|---------|-------------|
| `/research <topic>` | Deep dive on a topic, creates claims |
| `/prototype` | Build something testable |
| `/challenge <id>` | Adversarial stress-test of a claim |
| `/witness <id> <url>` | External corroboration |
| `/blind-spot` | Find gaps in your investigation |
| `/brief` | Compile the decision document |
| `/status` | Sprint dashboard |
| `/present` | Generate a stakeholder presentation |
| `/resolve` | Adjudicate conflicts between claims |

## Guard rails

1. **Git pre-commit hook** — prevents committing broken claims.
2. **Claude Code guard hook** — prevents generating output from stale compilations.

## Zero dependencies

Node 20+ is the only requirement. Zero npm dependencies.

## License

MIT
