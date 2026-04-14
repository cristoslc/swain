---
source-id: "crispy-agents-readme"
title: "CRISPY Agents — Multi-agent coding system for OpenCode"
type: repository
url: "https://github.com/tfolkman/crispy-agents"
fetched: 2026-04-13T17:00:00Z
highlights:
  - "crispy-agents-architect/crispy-agents-architect.md"
  - "crispy-agents-coder/crispy-agents-coder.md"
  - "crispy-agents-reviewer/crispy-agents-reviewer.md"
  - "crispy-agents-build-workflow/crispy-agents-build-workflow.md"
selective: true
---

# CRISPY Agents

Multi-agent coding system built on [OpenCode](https://opencode.ai) using the [CRISPY framework](https://github.com/nicekid1/CRISPY-Agents) by Dex from HumanLayer.

Five specialized agents, each with a distinct role and a different model, orchestrating through seven phases with a 40-instruction budget per phase.

## What You Get

- **5 agent configs** (`~/.config/opencode/agents/`) — architect, coder, reviewer, scout, verifier
- **1 build command** (`~/.config/opencode/commands/`) — `/build-workflow` orchestrates all agents through the CRISPY phases
- **Model diversity by default** — coder and reviewer use different models so they catch each other's blind spots

## The Agents

| Agent | Role | Model | Why |
|-------|------|-------|-----|
| Architect | Context, Structure, Plan phases | GLM 5.1 | SWE-bench Pro #1, sustained execution |
| Coder | Vertical slice implementation | GLM 5.1 | Same context as architect for alignment |
| Reviewer | Validates against structure.md | Qwen 3.6 Plus | Different model catches different bugs |
| Scout | Pure research, no implementation intent | Kimi K2.5 | Fresh context, pure facts |
| Verifier | Generates and runs validation scripts | GLM 4.7 | Execution, not reasoning |

## The Build Command

`/build-workflow` runs the full CRISPY pipeline:

1. **Context** — Load relevant codebase areas
2. **Research** — Pure facts from scout (no implementation intent)
3. **Investigate** — Dig deeper on specific areas
4. **Structure** — High-level outline with testing checkpoints (produces `structure.md`)
5. **Plan** — Tactical execution plan (produces `plan.md`)
6. **Human Review Gate** — You approve before any code is written
7. **Yield** — Implement in vertical slices with TDD mandatory
8. **PR** — Ship it

Each phase gets a max of 40 instructions. No 1,000-line monolithic plans.

## Why Different Models for Coder and Reviewer?

When the same model writes code and reviews it, the reviewer shares the same blind spots. It wrote the code. Of course it thinks the code is fine.

GLM 5.1 and Qwen 3.6 Plus have different training data, different architectural biases, different failure modes. Qwen catches things GLM is blind to, and vice versa. The cost difference is negligible. The quality difference is significant.

## Credits

- **CRISPY framework** by Dex from HumanLayer — the instruction budget principle, phase decomposition, and vertical slice methodology
- **OpenCode** — the open-source terminal-based coding agent this runs on
- Model providers: Zhipu AI (GLM), Alibaba (Qwen), Moonshot AI (Kimi)

## License

MIT