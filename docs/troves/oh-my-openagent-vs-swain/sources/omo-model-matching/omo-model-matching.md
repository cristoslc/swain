---
source-id: omo-model-matching
type: web
url: "https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/guide/agent-model-matching.md"
fetched: 2026-04-19T12:00:00Z
title: "Oh My OpenAgent — Agent-Model Matching Guide"
---

# Agent-Model Matching Guide

## The Core Insight

Models aren't just "smarter" or "dumber" — they think differently. Claude follows complex, mechanics-driven prompts (1,100-line nested workflows). GPT responds to principle-driven prompts (3 principles in ~121 lines achieve the same behavior). This isn't a bug; it's the foundation of the multi-model approach.

## Agent-Model Mapping

### Communicators (Claude / Kimi / GLM)

These agents need models that reliably follow complex, multi-layered instructions.

- **Sisyphus**: Main orchestrator. Claude Opus 4.7 default. Long fallback chain through Kimi K2.5, GLM 5, GPT-5.4 (medium), Big Pickle.
- **Metis**: Plan gap analyzer. Claude Opus 4.7 default with GPT-5.4 and GLM 5 fallbacks.

### Dual-Prompt Agents (Auto-detect model family)

These ship separate prompts for Claude and GPT families. They detect the model at runtime and switch.

- **Prometheus**: Strategic planner. Claude preferred, GPT supported.
- **Atlas**: Todo orchestrator. Claude Sonnet 4.6 default, GPT-5.4 fallback.

### Deep Specialists (GPT only)

Built for GPT's principle-driven style. Do not override to Claude — same instructions get understood completely differently.

- **Hephaestus**: Autonomous deep worker. GPT-5.4 only. Single-entry chain.
- **Oracle**: Architecture consultant. GPT-5.4 preferred, Gemini 3.1 Pro and Claude Opus as fallbacks.
- **Momus**: Ruthless reviewer. GPT-5.4 xhigh preferred, Claude Opus and Gemini as fallbacks.

### Utility Runners (Speed over intelligence)

Don't "upgrade" these to Opus — that's hiring a senior engineer to file paperwork.

- **Explore**: Grok Code Fast 1 — fastest code grep.
- **Librarian**: MiniMax M2.7 — fast doc search.
- **Multimodal Looker**: GPT-5.4 for vision, Kimi K2.5 as fallback.
- **Sisyphus-Junior**: Category-dependent, general fallback through Claude Sonnet 4.6 → Kimi K2.5 → GPT-5.4 → MiniMax → Big Pickle.

## Model Families Detail

### Claude Family
Communicative, instruction-following, structured output. Best for agents following complex multi-step prompts.
- Claude Opus 4.7: Best overall. Highest compliance.
- Claude Sonnet 4.6: Faster, cheaper. Good balance.
- Claude Haiku 4.5: Fast and cheap. Utility work.
- Kimi K2.5: Behaves very similarly to Claude at lower cost.
- GLM 5: Claude-like behavior. Solid for orchestration.

### GPT Family
Principle-driven, explicit reasoning, deep technical capability. Best for autonomous complex problems.
- GPT-5.3 Codex: Deep coding powerhouse. Autonomous exploration.
- GPT-5.4: High intelligence, strategic reasoning. Default for Oracle and Momus.
- GPT-5.4 Mini: Fast + strong reasoning. Default for quick category.
- GPT-5-Nano: Ultra-cheap, fast. Simple utility tasks.

### Other Models
- Gemini 3.1 Pro: Excels at visual/frontend tasks. Default for visual-engineering and artistry.
- Gemini 3 Flash: Fast. Good for doc search and light tasks.
- Grok Code Fast 1: Blazing fast code grep. Default for Explore.
- MiniMax M2.7 / M2.7 Highspeed: Fast utility models for fallback chains.

## Safe vs Dangerous Overrides

**Safe** (same personality type): Sisyphus: Opus → Sonnet, Kimi K2.5, GLM 5. Prometheus: Opus → GPT-5.4 (auto-switches to GPT prompt).

**Dangerous** (personality mismatch): Sisyphus → older GPT models. Hephaestus → Claude. Explore → Opus (massive cost waste).

## Model Resolution

4-step: override → category-default → provider-fallback → system-default. Your explicit config always wins. Variant and reasoningEffort values are normalized to model-supported values for graceful cross-provider degradation.