# CRISPY Agents — Synthesis

## Key Findings

CRISPY Agents is a multi-agent coding system for OpenCode. It builds on the CRISPY framework by Dex from HumanLayer. Development is split into seven phases with strict instruction budgets and vertical slice delivery. Five agents — architect, coder, reviewer, scout, and verifier — each handle distinct roles. The coder and reviewer use different models to avoid shared blind spots.

## The CRISPY Pipeline

The framework defines a linear but gated pipeline:

1. **Context** — Architect loads relevant codebase areas.
2. **Research** — Scout gathers pure facts. The architect hides the build goal from the scout. This prevents solution-biased research.
3. **Investigate** — Scout + architect dig deeper with decomposed questions.
4. **Structure** — Architect writes `structure.md` (<200 lines). It contains vertical slice outlines with testing checkpoints. Like C headers: signatures, not implementation.
5. **Plan** — Architect writes `plan.md` (<200 lines). It details tactical execution with per-slice agent assignments.
6. **Human Review Gate** — Hard stop. No code until the human approves structure + plan.
7. **Yield** — Coder builds vertical slices with mandatory TDD. Reviewer checks against structure.md. Verifier runs checkpoint scripts.
8. **PR** — Ship when all slices pass.

Each phase is capped at 40 instructions for frontier LLMs. A full context window holds roughly 150-200 instructions. This budget prevents the 1,000-line monolithic plan anti-pattern.

## Model Diversity Strategy

The key design choice: **coder and reviewer use different models** (GLM 5.1 and Qwen 3.6 Plus). A model reviewing its own code shares blind spots. It wrote the code, so it thinks the code is fine. Different training data and biases produce better coverage. The claimed cost is ~$35-45/month.

## Vertical Slices vs Horizontal Layers

CRISPY enforces vertical slices instead of horizontal layers. Vertical slices are end-to-end and independently testable. Each slice goes from mock to integration in one shot. Each slice has a testing checkpoint in structure.md that the verifier script validates.

## Role Separation

- **Architect** owns phases 1, 4, and 5. Writes structure.md and plan.md. Delegates research to scout.
- **Scout** does pure research with a fresh context window. It has no knowledge of the build goal. It answers decomposed questions only.
- **Coder** builds vertical slices with strict TDD (tests first, always).
- **Reviewer** checks code against structure.md (the design contract). It uses a different model than coder. Max 3 review cycles per slice.
- **Verifier** generates and runs validation scripts. No LLM guessing — only actual execution. Max 2 verification cycles.

## Points of Agreement Across Sources

All five agent configs and the build workflow agree on:
- 40-instruction budget per phase as a hard constraint
- structure.md as the binding contract — code that diverges without escalation is a failure
- Vertical slices over horizontal layers
- Mandatory human review gate between planning and implementation
- Iteration limits: max 3 review cycles, max 2 verification cycles
- TDD as non-negotiable for the coder

## Points of Disagreement or Tension

No explicit disagreement — the sources form a coherent system. But some tensions exist:

- **Scout's no-implementation-intent rule** conflicts with real-world research. Knowing what you build shapes better questions. The architect decomposes questions to hide intent, but this is fragile.
- **40-instruction budget** is pragmatic but may underserve complex architecture. The system allows splits, but splits risk losing cross-cutting context.
- **Model diversity** assumes different models have meaningfully different failure modes. This is plausible but not empirically shown in the sources.

## Gaps

- **No empirical validation** of framework claims (SWE-bench rankings, quality metrics, cycle time data).
- **No cost guidance** beyond "$35-45/month." Token costs for complex workflows could vary a lot.
- **No single-model fallback.** The system assumes at least two model providers (Ollama Cloud Pro + Fireworks AI).
- **No concurrent work support.** The pipeline is strictly sequential per feature.
- **No CI/CD integration.** The pipeline stops at PR creation.
- **The original CRISPY-Agents framework repo** (nicekid1/CRISPY-Agents) was not accessible (404). This trove only covers tfolkman's implementation.

## Relationship to Other Troves

The `gastown-agent-orchestration` trove covers multi-agent patterns from a design perspective. It focuses on agent bottlenecks, vibecoding at scale, and merge queue dynamics. Where gastown covers organizational dynamics, CRISPY covers the mechanical workflow: phase decomposition, instruction budgets, role separation, and vertical slices.