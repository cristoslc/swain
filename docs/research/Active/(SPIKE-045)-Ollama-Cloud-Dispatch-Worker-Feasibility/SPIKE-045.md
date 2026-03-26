---
title: "Ollama Cloud Dispatch Worker Feasibility"
artifact: SPIKE-045
track: container
status: Active
author: operator
created: 2026-03-25
last-updated: 2026-03-25
question: "Can OpenCode + Ollama Cloud (qwen3-coder:480b or deepseek-v3.1:671b) reliably execute a simple swain SPEC — reading AGENTS.md, following conventions, editing files, running tests — making auth-free dispatch workers viable for mechanical tasks?"
gate: Pre-MVP
risks-addressed:
  - "Dispatch workers require Claude Code subscription — limits scaling and increases cost"
  - "No auth-free path for background agent execution"
trove: ollama-cloud-dispatch-workers@a530063
linked-artifacts:
  - INITIATIVE-008
  - ADR-016
---

# Ollama Cloud Dispatch Worker Feasibility

## Summary

<!-- Populated when transitioning to Complete. -->

## Question

Can OpenCode + Ollama Cloud (qwen3-coder:480b or deepseek-v3.1:671b) reliably execute a simple swain SPEC — reading AGENTS.md, following conventions, editing files, running tests — making auth-free dispatch workers viable for mechanical tasks?

## Context

swain-dispatch is deprecated ([ADR-016](../../../adr/Active/(ADR-016)-Deprecate-swain-dispatch.md)) because it required `ANTHROPIC_API_KEY` with per-token billing. Ollama Cloud (public beta since January 2026) offers an OpenAI-compatible API with simple API key auth — no subscription, no interactive login. The `ollama launch opencode` command can start an open-source coding agent backed by Ollama Cloud models, creating a potential path for auth-free dispatch workers under [INITIATIVE-008](../../../initiative/Active/(INITIATIVE-008)-Automated-Work-Intake/(INITIATIVE-008)-Automated-Work-Intake.md) (Automated Work Intake).

Key unknowns: whether open-source models can reliably follow swain's AGENTS.md governance conventions, handle YAML frontmatter artifact formats, and maintain coherent multi-step editing sessions.

## Go / No-Go Criteria

**Go (viable for mechanical dispatch)** — all of:
1. OpenCode + qwen3-coder:480b (or deepseek-v3.1:671b) can read and parse AGENTS.md governance rules
2. The agent correctly identifies and invokes swain skills when prompted (or follows manual instructions equivalent to skill behavior)
3. The agent can complete a simple mechanical SPEC: edit YAML frontmatter, create/modify markdown files, run shell scripts
4. Success rate ≥ 70% across 5 trial runs of the same SPEC
5. Effective context window ≥ 16K tokens (enough to hold AGENTS.md + a SPEC + working files)

**No-Go** — any of:
1. Context window < 8K tokens through the OpenAI-compatible API (breaks AGENTS.md loading)
2. Success rate < 50% on mechanical tasks
3. Agent hallucinates file paths, artifact IDs, or frontmatter fields > 30% of the time
4. Free/Pro tier rate limits prevent completing a single SPEC within 30 minutes

## Pivot Recommendation

If No-Go:
- **Pivot A**: Use Ollama Cloud as inference backend but pair with Claude Code Agent SDK for the agent framework (still needs Anthropic auth but gets Ollama pricing for most calls)
- **Pivot B**: Self-host Ollama with a coding-capable model (qwen3-coder:32b) on a dedicated VPS — removes rate limits and cloud dependency at ~$55/month for an RTX 4090 build
- **Pivot C**: Abandon multi-model dispatch; keep all agent work on Claude Code and focus on reducing per-session cost through model routing (SPIKE-026)

## Test Protocol

### Setup
1. Create an Ollama Cloud account and API key
2. Install OpenCode CLI
3. Configure OpenCode to use `https://ollama.com/v1` as base URL with the API key
4. Select a completed mechanical SPEC as the test case (e.g., a frontmatter fix or xref update)

### Trial Runs (5x per model)
1. Start OpenCode in the swain repo root
2. Prompt: "Read AGENTS.md, then implement SPEC-NNN following swain conventions"
3. Record: did it read AGENTS.md? Did it find the spec? Did it correctly edit files? Did it follow conventions?
4. Score each run: pass (completed correctly), partial (completed with errors), fail (could not complete)

### Models to Test
- `qwen3-coder:480b-cloud` — largest coding-specific model
- `deepseek-v3.1:671b-cloud` — largest general model with tool calling
- `devstral-2:123b-cloud` — Mistral's coding model

### Measurements
- Context window effective size (can it hold AGENTS.md + spec + files?)
- Time to complete the SPEC
- Token consumption / cost
- Error types (hallucination, convention violation, tool misuse)

## Findings

<!-- Populated during Active phase investigation. -->

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-25 | — | Initial creation — operator-requested spike |
