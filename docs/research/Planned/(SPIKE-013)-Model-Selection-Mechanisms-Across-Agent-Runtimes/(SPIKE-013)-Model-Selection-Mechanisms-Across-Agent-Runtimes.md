---
title: "Model Selection Mechanisms Across Agent Runtimes"
artifact: SPIKE-013
status: Planned
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
question: "How does each target agent runtime (Claude Code, Codex, OpenCode, Cursor, Copilot, Gemini CLI) expose model selection and reasoning effort control — and what is the correct instruction format for each?"
gate: Pre-EPIC-007-specs
risks-addressed:
  - Runtime-specific annotations may conflict or cause errors in runtimes that don't understand them
  - Some runtimes may have no model selection mechanism — fallback must be a safe no-op
  - Reasoning effort APIs (extended-thinking, budget tokens) differ across providers and may not map cleanly
linked-artifacts:
  - EPIC-007
evidence-pool: ""
---

# Model Selection Mechanisms Across Agent Runtimes

## Question

How does each target agent runtime (Claude Code, Codex, OpenCode, Cursor, Copilot, Gemini CLI) expose model selection and reasoning effort control — and what is the correct instruction format for each?

## Go / No-Go Criteria

**Go:** For each runtime, produce: (a) the mechanism for steering model selection (config key, prompt annotation, environment variable, none), (b) the mechanism for reasoning effort / extended thinking, (c) a safe fallback instruction that is a no-op if the runtime ignores it, and (d) the instruction format to embed in SKILL.md files.

**No-Go:** No runtime-agnostic instruction format exists that is safe across all targets. In that case, produce a conditional block format (runtime-keyed sections) and flag runtimes that require separate skill file variants.

## Pivot Recommendation

If no-go: design a runtime-keyed annotation block (e.g., `<!-- runtime: claude-code -->` fenced sections) so each runtime reads only its relevant instructions. skill-creator handles the block insertion.

## Findings

(Populated during Active phase.)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-13 | — | Initial creation |
