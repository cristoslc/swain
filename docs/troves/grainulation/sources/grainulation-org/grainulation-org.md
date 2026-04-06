---
source-id: "grainulation-org"
title: "Grainulation — Structured Research Ecosystem for AI Agents"
type: repository
url: "https://github.com/grainulation/grainulation"
fetched: 2026-04-06T15:00:00Z
hash: "f364e0a513121ee7499caf9228f5e3b8caab2d92e8cd8e891f81a5bd7f6ab77b"
highlights:
  - "grainulation-org.md"
selective: true
notes: "Main org landing repo — unified CLI and ecosystem overview"
---

# Grainulation — Structured Research Ecosystem for AI Agents

**Tagline:** Structured research for decisions that satisfice.

Grainulation is a process for turning data into evidence and evidence into conviction. You start with a question, grow typed claims with confidence levels and evidence tiers, challenge what you find, and compile a brief only when conflicts are resolved and gaps are acknowledged.

## Install

```bash
npm install -g @grainulation/grainulation
```

Or start a research sprint directly:

```bash
npx @grainulation/wheat init
```

## Quick start

```bash
grainulation              # Ecosystem overview
grainulation doctor       # Health check: which tools, which versions
grainulation setup        # Install the right tools for your role
grainulation wheat init   # Delegate to any tool
grainulation farmer start
```

## The ecosystem

Eight tools. Each does one thing.

| Tool | What it does | Install |
|------|-------------|---------|
| wheat | Research engine — grow structured evidence | `npx @grainulation/wheat init` |
| farmer | Permission dashboard — approve AI actions in real time | `npm i -g @grainulation/farmer` |
| barn | Shared tools — templates, validators, sprint detection | `npm i -g @grainulation/barn` |
| mill | Format conversion — export to PDF, CSV, slides, 24 formats | `npm i -g @grainulation/mill` |
| silo | Knowledge storage — reusable claim libraries and packs | `npm i -g @grainulation/silo` |
| harvest | Analytics — cross-sprint patterns and prediction scoring | `npm i -g @grainulation/harvest` |
| orchard | Orchestration — multi-sprint coordination and dependencies | `npm i -g @grainulation/orchard` |
| grainulation | Unified CLI — single entry point to the ecosystem | `npm i -g @grainulation/grainulation` |

**You don't need all eight.** Start with wheat.

## The research journey

```
Question --> Seed Claims --> Grow Evidence --> Compile Brief
  /init       /research       /challenge        /brief
                              /blind-spot
                              /witness
```

Every step is tracked. Every claim has provenance. Every decision is reproducible.

## Philosophy

- **Satisficing over maximizing.** You will never have perfect information. The goal is enough evidence to make a defensible decision.
- **Claims over opinions.** Every finding is a typed claim with an evidence tier.
- **Adversarial pressure over consensus.** The `/challenge` command exists because comfortable agreement is the enemy of good decisions.
- **Process over heroics.** A reproducible sprint that anyone can pick up beats a brilliant analysis that lives in one person's head.

## Zero dependencies

Every grainulation tool runs on Node built-ins only. No npm install waterfall. No left-pad. No supply chain anxiety.

## License

MIT
