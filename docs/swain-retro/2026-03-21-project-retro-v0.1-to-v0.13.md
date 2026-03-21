# Retro: Swain Project — v1.0.0 through v0.13.0-alpha

**Date:** 2026-03-21
**Scope:** Full project history
**Period:** 2026-03-07 — 2026-03-21 (14 days)

## Summary

Swain started as a single skill for a single artifact type and grew into a framework with 18+ skills, 10 artifact types, a dependency graph engine, prioritization layer, security scanning, Docker sandboxing, tmux workspace management, research trove system, data contracts, and a trunk+release branch model. 730 non-merge commits across 13 releases.

The project was built almost entirely through agentic development — the operator directing Claude Code agents, making design decisions, and reviewing output while agents handled implementation. The operator estimates this produced 10x–100x more progress than solo development would have.

## Artifacts

| Metric | Count |
|--------|-------|
| Releases | 13 (1.0.0 → 0.13.0-alpha) |
| Non-merge commits | 730 |
| Skills | 18+ |
| Artifact types | 10 (Vision, Initiative, Epic, Spec, Spike, ADR, Persona, Runbook, Design, Journey) |
| Prior retros | 6 |
| Active Visions | 3 (Operator Cognitive Support, Safe Autonomy, Swain) |

## Reflection

### What went well

**Agentic development velocity is real.** 730 commits in 14 days, covering scope that would normally take months of solo work. The operator-as-decision-maker / agent-as-implementer pattern worked: the operator shaped every design decision while agents handled file operations, lifecycle management, cross-referencing, and implementation.

**Persisted artifacts as durable context.** This is the validating meta-pattern for swain itself. Retros were referenced across sessions — the EPIC-038 retro was read 5+ times during the SPIKE-022 → SPEC-114 session, each reading surfacing new insights. Spikes, ADRs, and specs survived context window resets and session boundaries. The artifact graph provided continuity that ephemeral conversation context cannot. Without persisted artifacts, the iterative deepening that produced merge-with-retry (from retro → spike → ADR → spec → implementation) would not have been possible.

**Retro-driven development.** 4 of the 6 retros directly produced implementation work. The EPIC-038 retro led to SPIKE-022, which led to ADR-011/013 and SPEC-114. The v0.10.0 retro led to the Jinja2 changelog template. The spike-findings retro led to SPEC-116/117 (read-before-reasoning, evidence-basis rules). Retros aren't just reflection — they're a discovery mechanism for what to build next.

### What was surprising

**Agentic development has addictive qualities.** The tight feedback loop of "describe → see it built → describe the next thing" creates a compulsion similar to gaming addiction. The operator has had to actively moderate this, with only partial success. This is a genuinely novel phenomenon that isn't well-understood yet.

**Scope explosion was unpredictable.** The operator might have predicted "framework-level scope eventually" but not within two weeks. Each capability created the context for the next — specgraph enabled prioritization, prioritization required initiatives, initiatives required visions, visions required attention tracking. The cost of building dropped dramatically but the cost of deciding what to build stayed constant.

**730 commits is a lot.** Slightly inflated by lifecycle hash stamps and artifact transitions, but mostly meaningful. The volume itself is surprising even to the person who produced it.

### What would change

**Move out of bash earlier.** Some scripts have grown to sizes that make the operator nervous. specgraph was rewritten in Python (3.0.0), but chart.sh and other scripts accumulated complexity under agentic velocity without the review pressure that slower-paced development provides.

**Enforce TDD earlier.** The operator wanted a much better TDD cycle but hasn't figured out how to do TDD on skills, let alone a skill framework. Goal-orientation and enforced-TDD were identified as desirable earlier than they were adopted.

**Read and review more code personally.** Agentic velocity means the operator is approving output faster than they can deeply understand it. The agent writes code the operator hasn't read — a trust gap that accumulates.

**Open question: is this worth continuing?** The operator is genuinely skeptical that swain will work for anyone besides them. The alternative — adopting existing tooling — is tempting but likely leads back to heavy customization... which is how swain started. The "customize existing tooling back into swain" loop is the classic framework author's dilemma.

### Patterns observed (synthesized from 6 prior retros)

#### 1. Agent overcomplicates, operator simplifies

Appears in 4/6 retros. The agent's instinct is to build new infrastructure; the operator's instinct is to use existing primitives correctly. Examples:
- SPIKE-022: three-layer mitigation strategy → "just use merge" (operator: "this must be a solved problem")
- EPIC-038: reactive spec-per-screenshot → architecture-first decomposition (operator: "do we need to rebuild the specs?")
- v0.10.0: agent couldn't reliably bucket changelog entries → Jinja2 template to make categories structural
- EPIC-031: SPIKE-033 recommended No-Go on a disambiguation framework — the simple fix was 2 lines

**Implication:** The operator's highest-value contribution is simplification. Agents naturally accrete complexity; the operator prunes it.

#### 2. Forward-linking is natural, back-propagation is not

Appears in 3/6 retros. Agents naturally link new artifacts to their dependencies but never go back to update old artifacts when new evidence arrives.
- SPIKE-032 invalidated SPEC-067 AC-8, but SPEC-067 was never updated
- DESIGN-005 superseded DESIGN-002, caught only by manual operator inspection
- 7 of 9 audit specs in EPIC-031 were already done by the time execution started — the audit was stale

**Implication:** The system validates at creation time but doesn't re-evaluate when context changes. Every mitigation so far (spike completion hooks, same-type overlap checks, pre-implementation detection) addresses a specific instance of this general pattern.

#### 3. Velocity vs. integrity tradeoff

Appears in 3/6 retros. Autonomous execution optimizes for throughput at the cost of semantic correctness.
- VISION-002: 8 artifacts in one session, but a semantic conflict between spike findings and spec ACs was missed
- EPIC-038: worktree agents reported success in isolation, but the merged result was incomplete
- verification-before-completion was skipped during rapid execution despite being mandatory in AGENTS.md

**Implication:** The superpowers chain (brainstorming → TDD → verification) exists precisely to counter this. The chain was specified but not always followed. Making it structural rather than advisory is the remaining gap.

#### 4. Persisted artifacts enable iterative deepening

Appears in 2/6 retros explicitly, but is the foundational pattern for the entire project.
- EPIC-038 retro was referenced 5+ times across sessions, each reading surfacing new insights
- Retros directly produced 4 implementation streams (SPIKE-022, Jinja2 template, SPEC-116/117, evidence-basis rule)
- Spike research troves (18 sources for multi-agent collision vectors) built durable knowledge bases

**Implication:** This validates swain's core thesis. Artifacts that survive context window resets and session boundaries enable a depth of analysis that ephemeral conversation cannot. The framework's complexity is justified by this capability — but only if the artifacts are actually read and maintained.

#### 5. Research before rendering

Appears in 2/6 retros. Jumping to implementation before understanding the problem space costs time.
- Mermaid quadrantChart limitations: 45 minutes of trial and error that upfront research would have prevented
- ADR-005 wasn't read until the operator asked why cherry-pick was being used — should have been the first thing read

**Implication:** The "read before reasoning" rule (SPEC-116) and "evidence basis for all actions" rule (SPEC-117) are direct responses. These are now governance rules, not just retro observations.

## Learnings captured

| Memory file | Type | Summary |
|------------|------|---------|
| feedback_retro_agentic_addiction.md | feedback | Agentic development has addictive qualities — the operator may need help moderating session length and scope |
| project_retro_swain_viability.md | project | Operator uncertain about swain's viability beyond personal use — "customize existing tooling back into swain" loop |
