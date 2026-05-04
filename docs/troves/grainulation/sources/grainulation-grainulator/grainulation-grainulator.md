---
source-id: "grainulation-grainulator"
title: "Grainulator — Research Sprint Orchestrator for Claude Code"
type: repository
url: "https://github.com/grainulation/grainulator"
fetched: 2026-04-06T15:00:00Z
hash: "be14264a7622994a5c612f3a0d9a73967fb6eab5147ed47f5127bc5ae2efe18f"
highlights:
  - "grainulation-grainulator.md"
selective: true
notes: "Claude Code plugin — primary integration point for the ecosystem; includes autonomous subagent"
---

# Grainulator — Research Sprint Orchestrator for Claude Code

**Tagline:** Research that compiles.

Grainulator is the Claude Code plugin for the grainulation ecosystem. It ties together wheat (claims engine), mill (export), silo (knowledge store), and DeepWiki (codebase research) into a single installable plugin with 13 prompt-engineered skills, an autonomous subagent, and a browser-based demo site.

## Try it

**[grainulator.app](https://grainulator.app)** — interactive demo with in-browser AI. No install needed.

## Install

```bash
claude plugin marketplace add https://github.com/grainulation/grainulator/blob/main/.claude-plugin/marketplace.json
claude plugin install grainulator
```

Requirements: Node.js >= 20.

For team deployment, commit to `.claude/settings.json`:

```json
{
  "enabledPlugins": ["grainulator@grainulation-marketplace"]
}
```

## Quick start

Talk to Claude naturally — the intent router handles skill dispatch:

- "research how our auth system works" — runs a multi-pass research sprint.
- "challenge r003" — adversarial testing of a specific claim.
- "what are we missing?" — blind spot analysis.
- "write it up" — generates a compiled brief.

No slash syntax required.

## Claims model

**Claim types:**

| Type | Meaning |
|------|---------|
| `constraint` | Hard requirements, non-negotiable boundaries |
| `factual` | Verifiable statements about the world |
| `estimate` | Projections, approximations, ranges |
| `risk` | Potential failure modes, concerns |
| `recommendation` | Proposed courses of action |
| `feedback` | Stakeholder input, opinions |

**Evidence tiers:** `stated` → `web` → `documented` → `tested` → `production`.

**The compiler** runs 7 passes — type coverage, evidence strength, conflict detection, bias scan — and produces a confidence score. Unresolved conflicts block output.

## Skills (13 total)

| Skill | Description |
|-------|-------------|
| `/init` | Start a new research sprint |
| `/research` | Multi-pass investigation with evidence gathering |
| `/challenge` | Adversarial testing of a claim |
| `/witness` | Corroborate a claim against an external source |
| `/blind-spot` | Structural gap analysis |
| `/brief` | Generate a compiled decision brief |
| `/present` | Generate a presentation deck |
| `/status` | Sprint dashboard snapshot |
| `/pull` | Import knowledge from external sources (DeepWiki, Confluence) |
| `/sync` | Publish artifacts to external targets |
| `/calibrate` | Score predictions against actual outcomes |
| `/resolve` | Adjudicate conflicts between claims |
| `/feedback` | Record stakeholder input |

## Autonomous agent

The **grainulator subagent** (`agents/grainulator.md`) runs multi-pass research sprints autonomously. It reads the compiler output to decide what command to run next — research, challenge, witness, blind-spot — until the sprint reaches decision-ready confidence.

Launch with: `"research X using grainulator"`.

## Architecture

- **Plugin manifest**: `.claude-plugin/plugin.json`
- **MCP servers**: wheat (claims engine), mill (format conversion), silo (knowledge store), DeepWiki (codebase research)
- **Skills**: `skills/<name>/SKILL.md` — 13 prompt-engineered workflows
- **Agent**: `agents/grainulator.md` — autonomous sprint subagent
- **Hooks**: Auto-compile on claim mutation, write-guard on `claims.json` and `compilation.json`
- **Orchard**: Multi-sprint orchestration via `orchard.json` dependency graphs

## Demo site

[grainulator.app](https://grainulator.app) is a PWA demo:

- Mobile-first chat interface.
- In-browser AI via WebLLM (SmolLM2-360M, ~200MB download).
- 50 pre-generated demo topics with fuzzy matching.
- Live local inference when model downloads.
- Compile flow with 7-pass confidence scoring.

## Enterprise deployment

Three levels:

1. **Team lead**: Commit `.claude/settings.json` with `enabledPlugins` to your repo.
2. **IT admin**: Deploy managed settings via MDM with pre-approved permissions.
3. **Air-gapped**: Use `CLAUDE_CODE_PLUGIN_SEED_DIR` with the plugin baked into container images.

## Zero dependencies

Every grainulation tool runs on Node built-ins only. MCP servers download on first use via `npx`.

## License

MIT
