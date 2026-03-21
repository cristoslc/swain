---
title: "Context Fork as Model Routing Implementation Path"
artifact: SPIKE-026
track: container
status: Active
author: cristos
created: 2026-03-16
last-updated: 2026-03-16
question: "Can Claude Code's `context: fork` frontmatter directive, combined with agent type selection, implement the per-operation model tier routing that SPIKE-014 recommended — and if so, what is the concrete mechanism?"
gate: Pre-future-model-routing-work
risks-addressed:
  - SPIKE-014 recommended per-operation tier routing but SPEC-026 implemented only advisory annotations — context fork may close the gap between annotation and runtime enforcement
  - Model routing via advisory prose depends on agent compliance — a runtime mechanism (fork + agent type) would be deterministic
  - Unknown whether context fork supports model selection per forked context — may be agent-type-only
linked-artifacts:
  - EPIC-007
  - INITIATIVE-003
  - SPEC-026
  - SPIKE-013
  - SPIKE-014
trove: context-fork-claude-code
---

# Context Fork as Model Routing Implementation Path

## Summary

<!-- Final-pass section: populated when transitioning to Complete.
     Lead with the verdict (Go / No-Go / Hybrid / Conditional), then
     1-3 sentences distilling the key finding and recommended next step.
     During Active phase, leave this section empty — keep the document
     evidence-first while research is in progress. -->

## Question

Can Claude Code's `context: fork` frontmatter directive, combined with agent type selection, implement the per-operation model tier routing that SPIKE-014 recommended — and if so, what is the concrete mechanism?

## Go / No-Go Criteria

**Go:** Context fork supports at least one of: (a) per-fork model selection (e.g., `model: haiku` in frontmatter alongside `context: fork`), (b) agent type selection that maps to different model tiers, or (c) a composable pattern where fork + env var override achieves tier routing. Produce a working proof-of-concept skill that demonstrates the mechanism.

**No-Go:** Context fork only isolates conversation history — no model or agent type differentiation is possible. The `agent` field is limited to built-in agent types (Explore, Plan, etc.) with no model control. In that case, advisory annotations (SPEC-026) remain the only viable approach.

## Pivot Recommendation

If no-go: investigate whether Claude Code hooks (pre-tool, post-tool) can intercept skill invocations and dynamically set `ANTHROPIC_MODEL` or `CLAUDE_CODE_SUBAGENT_MODEL` environment variables based on the `<!-- swain-model-hint -->` annotations already present in SKILL.md files. This would achieve runtime enforcement without requiring context fork support.

## Findings

### Prior art (from completed spikes)

**SPIKE-013** found that no agent runtime accepts model hints in instruction files — model selection is always out-of-band (settings, env vars, CLI flags). Advisory prose blocks are safe but unenforceable.

**SPIKE-014** classified 30 swain skill operations into heavy/analysis/lightweight tiers and found 3 mixed-tier skills (swain-design, swain-do, swain-help) that need per-operation routing. Section-level `<!-- swain-model-hint -->` annotations were recommended.

**SPEC-026** implemented the annotations across all 17 SKILL.md files and added routing rules to AGENTS.md, but these remain advisory — the agent may or may not honor them.

### Context fork mechanism (from ClaudeLog)

The `context: fork` directive in skill frontmatter:
- Runs the skill in an isolated sub-agent with separate conversation history
- Accepts an optional `agent` field to select agent type (e.g., `Explore`)
- Returns results to the main thread without intermediate execution details
- Keeps the main conversation context clean

### Open questions for investigation

1. **Model selection in forked context:** Does `context: fork` accept a `model` field? Can the forked agent run on a different model than the main thread?

2. **Agent type → model mapping:** Do built-in agent types (Explore, Plan, general-purpose) run on different models? If so, can this be leveraged for tier routing?

3. **Environment variable inheritance:** Does the forked context inherit `ANTHROPIC_MODEL` / `CLAUDE_CODE_SUBAGENT_MODEL`? Can these be overridden per-fork?

4. **Hook-based interception:** Can Claude Code hooks detect skill invocation and set model env vars before the fork executes?

5. **Performance overhead:** What is the latency cost of forking vs. inline execution? Is it acceptable for lightweight (Haiku-tier) operations?

6. **Composability:** Can `context: fork` coexist with other frontmatter fields (`context`, `agent`, `model`) and swain's existing `<!-- swain-model-hint -->` annotations?

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-16 | -- | Initial creation; trove: context-fork-claude-code |
