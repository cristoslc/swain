---
source-id: "gstack-readme"
title: "GStack — Garry Tan's Software Factory for Claude Code"
type: web
url: "https://github.com/garrytan/gstack"
fetched: 2026-04-12T03:50:00Z
hash: "ea3bc7f1116e66b195bb0eb8b105b10dd63a6067b3d08a51a1df224dc325ded9"
---

# gstack

> "I don't think I've typed like a line of code probably since December, basically, which is an extremely large change." — Andrej Karpathy, No Priors podcast, March 2026

Garry Tan's open source software factory — 23 specialists and 8 power tools that turn Claude Code into a virtual engineering team. A CEO who rethinks the product, an eng manager who locks architecture, a designer who catches AI slop, a reviewer who finds production bugs, a QA lead who opens a real browser, a security officer who runs OWASP + STRIDE audits, and a release engineer who ships the PR.

**Stats:** 600,000+ lines of production code (35% tests) in 60 days. 10,000-20,000 lines per day. Part-time, while running YC full-time. 70.8k stars. 10k forks. MIT license.

## The sprint

gstack is a process, not a collection of tools. The skills run in the order a sprint runs:

**Think → Plan → Build → Review → Test → Ship → Reflect**

Each skill feeds into the next. `/office-hours` writes a design doc that `/plan-ceo-review` reads. `/plan-eng-review` writes a test plan that `/qa` picks up. `/review` catches bugs that `/ship` verifies are fixed.

## Skills (23 specialists)

| Skill | Specialist | What they do |
|---|---|---|
| `/office-hours` | YC Office Hours | Six forcing questions that reframe the product before you write code. |
| `/plan-ceo-review` | CEO / Founder | Rethink the problem, find the 10-star product. Four modes: Expansion, Selective Expansion, Hold Scope, Reduction. |
| `/plan-eng-review` | Eng Manager | Lock architecture, data flow, edge cases, tests. |
| `/plan-design-review` | Senior Designer | Rates each dimension 0-10, AI Slop detection. |
| `/plan-devex-review` | DX Lead | Developer personas, TTHW benchmarks, friction tracing. |
| `/design-consultation` | Design Partner | Build a complete design system from scratch. |
| `/review` | Staff Engineer | Find bugs that pass CI but blow up in production. Auto-fixes obvious ones. |
| `/investigate` | Debugger | Systematic root-cause debugging. Iron Law: no fixes without investigation. |
| `/design-review` | Designer Who Codes | Same audit as /plan-design-review, then fixes what it finds. |
| `/devex-review` | DX Tester | Live developer experience audit. Tests onboarding, times TTHW. |
| `/design-shotgun` | Design Explorer | Generate 4-6 AI mockup variants, comparison board, taste memory. |
| `/design-html` | Design Engineer | Turn mockup into production HTML via Pretext computed layout. 30KB, zero deps. |
| `/qa` | QA Lead | Test app, find bugs, fix with atomic commits, re-verify. Auto-generates regression tests. |
| `/qa-only` | QA Reporter | Same methodology as /qa but report only. |
| `/pair-agent` | Multi-Agent Coordinator | Share browser with any AI agent. Scoped tokens, tab isolation, rate limiting. |
| `/cso` | Chief Security Officer | OWASP Top 10 + STRIDE threat model. Zero-noise: 17 false positive exclusions. |
| `/ship` | Release Engineer | Sync main, run tests, audit coverage, push, open PR. Bootstraps test frameworks. |
| `/land-and-deploy` | Release Engineer | Merge PR, wait for CI and deploy, verify production health. |
| `/canary` | SRE | Post-deploy monitoring loop. Watch for console errors, perf regressions. |
| `/benchmark` | Perf Engineer | Baseline page load times, Core Web Vitals. Compare before/after. |
| `/document-release` | Tech Writer | Update all project docs to match what you just shipped. |
| `/retro` | Eng Manager | Team-aware weekly retro. Per-person breakdowns, shipping streaks, test health. |
| `/autoplan` | Review Pipeline | One command, fully reviewed plan. CEO → design → eng review automatically. |
| `/learn` | Memory | Manage what gstack learned across sessions. Patterns compound over time. |

## Power tools (8)

| Tool | What it does |
|---|---|
| `/codex` | Second Opinion — independent code review from OpenAI Codex CLI. Cross-model analysis. |
| `/careful` | Safety Guardrails — warns before destructive commands. |
| `/freeze` | Edit Lock — restrict file edits to one directory. |
| `/guard` | Full Safety — `/careful` + `/freeze`. |
| `/open-gstack-browser` | GStack Browser — AI-controlled Chromium with anti-bot stealth, auto model routing. |
| `/setup-deploy` | Deploy Configurator — one-time setup for `/land-and-deploy`. |
| `/gstack-upgrade` | Self-Updater — upgrade gstack to latest. |
| `/browse` | Real Chromium browser, real clicks, real screenshots. ~100ms per command. |

## Parallel sprints

gstack handles 10-15 parallel sprints via Conductor. Without process, ten agents is ten sources of chaos. With process — think, plan, build, review, test, ship — each agent knows exactly what to do and when to stop.

## Multi-agent support

- OpenClaw: spawns Claude Code sessions via ACP, every gstack skill just works
- OpenAI Codex CLI, OpenCode, Cursor, Factory Droid, Slate, Kiro: setup auto-detects host
- Native OpenClaw Skills (via ClawHub): office-hours, ceo-review, investigate, retro

## Key design principles

- **Fat skills, thin harness** — skills are markdown, logic goes in skills not in code
- **The sprint structure** makes parallelism work — each agent knows when to stop
- **Test everything** — `/ship` bootstraps test frameworks, `/qa` generates regression tests
- **Smart review routing** — CEO doesn't look at infra bug fixes, design review isn't needed for backend changes
- **Real browser mode** — GStack Browser with anti-bot stealth, sidebar agent for natural language browser control
- **`/pair-agent`** — cross-agent coordination with scoped tokens, tab isolation, rate limiting