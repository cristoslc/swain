---
source-id: omo-readme
type: repository
url: "https://github.com/code-yeongyu/oh-my-openagent"
fetched: 2026-04-19T12:00:00Z
title: "Oh My OpenAgent — README"
highlights:
  - omo-readme.md
selective: true
---

# Oh My OpenAgent — README

Oh My OpenAgent (OmO, formerly oh-my-openencode) is a multi-model agent orchestration harness for OpenCode. It transforms a single AI agent into a coordinated development team. The plugin is dual-published on npm as both `oh-my-opencode` and `oh-my-openagent`.

## Core Claim

"Install OmO. Type ultrawork. Done." The project positions itself as the zero-configuration multi-agent solution. You don't need to understand the architecture — just type `ultrawork` and all 11 agents activate in parallel.

## Key Features

- **Discipline Agents**: Sisyphus orchestrates Hephaestus, Oracle, Librarian, Explore as a parallel dev team.
- **ultrawork / ulw**: One-word command that activates every agent and doesn't stop until done.
- **IntentGate**: Classifies user intent before acting, preventing literal misinterpretations.
- **Hash-Anchored Edit Tool (LINE#ID)**: Every read line gets a content hash; edits validate hashes before applying. Zero stale-line errors. Inspired by oh-my-pi.
- **LSP + AST-Grep**: Workspace rename, go-to-definition, find-references, AST-aware code search across 25 languages.
- **Background Agents**: Fire 5+ specialists in parallel. Context stays lean. Results when ready.
- **Built-in MCPs**: Exa (web search), Context7 (official docs), Grep.app (GitHub search).
- **Ralph Loop / /ulw-loop**: Self-referential loop that continues until 100% done.
- **Todo Enforcer**: Yanks idle agents back to work. Tasks get done.
- **Comment Checker**: Strips AI slop from comments.
- **Tmux Integration**: Full interactive terminal for REPLs, debuggers, TUIs.
- **Claude Code Compatibility**: Hooks, commands, skills, MCPs, and plugins all work.
- **Skill-Embedded MCPs**: Skills carry their own MCP servers. Scoped to task. Context window stays clean.
- **Prometheus Planner**: Interview-mode strategic planning before execution.
- **/init-deep**: Auto-generates hierarchical AGENTS.md files throughout the project.

## Agent Architecture

```
User Request
    ↓
[Intent Gate] — Classifies what you actually want
    ↓
[Sisyphus] — Main orchestrator, plans and delegates
    ↓
    ├─→ [Prometheus] — Strategic planning (interview mode)
    ├─→ [Atlas] — Todo orchestration and execution
    ├─→ [Oracle] — Architecture consultation
    ├─→ [Librarian] — Documentation/code search
    ├─→ [Explore] — Fast codebase grep
    └─→ [Category-based agents] — Specialized by task type
```

When delegating, agents don't pick model names — they pick categories (visual-engineering, ultrabrain, deep, artistry, quick, unspecified-low, unspecified-high, writing). Categories map to optimal models automatically.

## Agent Roster

- **Sisyphus** (Claude Opus 4.7 / Kimi K2.5 / GLM 5): Main orchestrator. Plans, delegates, drives to completion.
- **Hephaestus** (GPT-5.4): Autonomous deep worker. Goal-oriented, explores and executes end-to-end.
- **Prometheus** (Claude Opus 4.7 / Kimi K2.5 / GLM 5): Strategic planner with interview mode.
- **Atlas** (Claude Sonnet 4.6): Todo-list orchestrator. Executes plans systematically.
- **Oracle** (GPT-5.4): Read-only architecture and debugging consultant.
- **Librarian** (MiniMax M2.7): Multi-repo analysis and documentation lookup.
- **Explore** (Grok Code Fast 1): Fast codebase exploration and grep.
- **Metis** (Claude Opus 4.7): Pre-planning gap analyzer.
- **Momus** (GPT-5.4 xhigh): Ruthless plan reviewer.
- **Multimodal Looker** (GPT-5.4): Vision/screenshot analysis.
- **Sisyphus-Junior** (category-dependent): Category-spawned executor that cannot re-delegate.

## Philosophy

The manifesto states: "Human intervention during agentic work is fundamentally a wrong signal." The goal is code indistinguishable from a senior engineer's work. Higher token usage is acceptable if it means the task completes without human babysitting.

## Model Matching Philosophy

Models are developers with different personalities. Claude follows complex instructions well. GPT reasons architecturally. Gemini visualizes. Haiku moves fast. OmO routes by task type to the model whose personality fits the work — this isn't temporary, it's the architecture that will grow more valuable as models specialize further.

## Anti-Patterns Enforced

- No `as any`, `@ts-ignore`, `@ts-expect-error`
- No emoji in code/comments unless explicitly requested
- No AI filler phrases in generated content
- No catch-all utility files
- Given/when/then test style, not Arrange-Act-Assert

## License

SUL-1.0 (source-available, not OSI-approved open source).