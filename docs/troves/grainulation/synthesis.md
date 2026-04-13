# Grainulation Ecosystem — Synthesis

**Sources:** 9 repos (grainulation, wheat, grainulator, farmer, barn, mill, silo, harvest, orchard)
**Last updated:** 2026-04-06

---

## What it is

Grainulation is a structured research toolkit for AI coding agents and solo developers. It treats technical decisions like code: findings are typed claims, a compiler validates them in 7 passes, and output is blocked until conflicts resolve. The core metaphor is "CI/CD for decisions."

The entry point is **wheat** — one `npx` command starts a sprint. Everything else is opt-in. The top-level **grainulation** CLI delegates to any tool in the ecosystem.

---

## Key findings

### The claims model is the load-bearing concept

All tools share one data format: `claims.json`. A claim has a type (constraint, factual, estimate, risk, recommendation, feedback) and an evidence tier (stated → web → documented → tested → production). The 7-pass compiler scores type coverage, evidence strength, and conflict resolution before allowing a brief to be generated. This is the same primitive everywhere: wheat creates them, silo stores them, mill exports them, harvest analyzes them.

### The ecosystem is modular, not monolithic

Eight tools, each with a single responsibility and zero npm dependencies. They interoperate through `claims.json`, not through direct coupling. You can use wheat standalone. You can run mill against any claims file without installing wheat. Silo works offline with no network. This is explicit design: "You don't need all eight. Start with wheat. That's it."

### Grainulator is the Claude Code integration layer

**Grainulator** is the Claude Code plugin. It bundles wheat, mill, silo, and DeepWiki as MCP servers, adds 13 prompt-engineered skills, and includes an autonomous subagent that runs multi-pass research sprints without human intervention. It also ships a demo PWA ([grainulator.app](https://grainulator.app)) with in-browser AI via WebLLM.

This is the primary integration point for anyone using Claude Code. Grainulator is how you get a research sprint inside a Claude session.

### Farmer solves the AI agent permission problem

**Farmer** is an agent-agnostic permission dashboard. It sits between the agent and the terminal, routing tool-call approval requests to a mobile or desktop dashboard. It ships with a Claude Code adapter and an extension interface for other agents. Trust tiers (paranoid, standard, autonomous) let you tune approval overhead per session.

This is a direct complement to swain's operator-sustainability concerns: farmer makes long-running agentic sessions safe to leave running without needing to babysit the terminal.

### Harvest closes the feedback loop

**Harvest** is read-only analytics that answers "are your decisions getting better?" It detects knowledge decay (claims that need refreshing), scores past estimates against outcomes, and tracks sprint velocity. It connects to farmer for mobile monitoring.

This is the retrospective layer: where wheat creates evidence, harvest measures whether the process is working.

### Orchard handles multi-sprint coordination

**Orchard** adds dependency graphs and cross-sprint conflict detection. When two sprints reach opposing conclusions, orchard flags them. It uses topological sort to determine execution order and blocks circular dependencies.

---

## Points of agreement across sources

- Zero npm dependencies is a core design constraint across all 9 repos.
- The filesystem is the database: no external services, no accounts, offline-first.
- Node 20+ is the only runtime requirement.
- All tools are MIT licensed.
- The claims model (typed claims + evidence tiers + 7-pass compiler) is universal.

---

## Points of disagreement / tension

- **Grainulator vs. wheat direct**: grainulator wraps wheat as an MCP server inside a plugin. Wheat can also be used as a standalone MCP server (`claude mcp add wheat`). There are two integration paths for Claude Code; the README recommends `wheat-mcp` over the subcommand path.
- **Autonomy vs. oversight**: the ecosystem has two simultaneous bets — grainulator's autonomous subagent (run without intervention) and farmer's permission dashboard (approve every action). These are opt-in choices, not contradictions, but they represent opposite ends of the autonomy spectrum.

---

## Gaps (what the sources don't cover)

- No documentation on how grainulation handles version skew between tools (e.g., wheat 2.x + silo 1.x).
- No coverage of the grainulation plugin marketplace beyond the grainulator entry — whether other plugins exist or are planned.
- No information on the `grainulation/grainulator` autonomous subagent's termination conditions or guardrails.
- No performance benchmarks for the 7-pass compiler at scale (e.g., hundreds of claims).
- No coverage of grainulation.com beyond the org URL in the GitHub metadata.

---

## Relevance to swain

Grainulation and swain occupy adjacent territory: both support solo developers doing structured work with AI coding agents. Key comparison points:

| Dimension | Grainulation | Swain |
|-----------|-------------|-------|
| Primary artifact | `claims.json` (typed claims) | Docs artifacts (Spec, Epic, ADR, Spike) |
| Compilation model | 7-pass compiler, conflict-blocked output | Lifecycle phases, AC validation |
| Agent integration | Claude Code plugin (grainulator) | Claude Code skills |
| Permission management | Farmer (external dashboard) | Built-in Claude Code hooks |
| Analytics | Harvest (cross-sprint) | Retrospectives (per-EPIC) |
| Orchestration | Orchard (multi-sprint) | Worktrees + Initiative hierarchy |
| Knowledge reuse | Silo (claim packs) | Troves (source collections) |
| Dependencies | Zero (Node built-ins only) | Shell scripts + external tools |

Grainulation's claims model is a potential input primitive for swain research work: a spike that uses wheat to compile evidence could feed directly into a trove or spec. The farmer permission dashboard is also worth evaluating as a complement to swain's operator-sustainability initiative.
