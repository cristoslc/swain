---
source-id: omo-manifesto
type: web
url: "https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/manifesto.md"
fetched: 2026-04-19T12:00:00Z
title: "Oh My OpenAgent — Manifesto"
---

# Manifesto

## Human Intervention is a Failure Signal

The manifesto's central premise: "Human intervention during agentic work is fundamentally a wrong signal." If you have to fix the AI's code, guide it step by step, or repeatedly clarify requirements, the agent has failed. The system should complete work without babysitting.

## Indistinguishable Code

Goal: code written by the agent should be indistinguishable from code written by a senior engineer. Not "AI-generated that needs cleanup." Not "a good starting point." The actual, final, production-ready code. If you can tell whether a commit was made by a human or an agent, the agent has failed.

## Token Cost vs Productivity

Higher token usage is acceptable if it significantly increases productivity. Using more tokens to have multiple agents research in parallel, verify work, or accumulate knowledge is a worthwhile investment for 10x-100x productivity gains. But unnecessary token waste is not pursued — the system optimizes for cheaper models on simple tasks, avoids redundant exploration, caches learnings, and stops research when sufficient context is gathered.

## Minimize Human Cognitive Load

The human should only need to say what they want. Two approaches:

1. **Prometheus (Interview Mode)**: You say "I want to add authentication." Prometheus researches your codebase, asks clarifying questions based on findings, surfaces edge cases, documents decisions, and builds a work plan.
2. **Ultrawork (Just Do It Mode)**: You type `ulw add authentication`. The agent figures out the approach, researches best practices, implements following conventions, verifies everything, and keeps going until complete.

## Predictable, Continuous, Delegatable

The ideal agent should work like a compiler: markdown in, working code out.

- **Predictable**: Given same inputs (codebase patterns, requirements, constraints), output should be consistent — not random, not surprising, not "creative" in ways you didn't ask for.
- **Continuous**: Work survives interruptions. Session crashes resume with `/start-work`. Progress is tracked. Context preserved across days.
- **Delegatable**: Like assigning a task to a capable team member — clear acceptance criteria, self-correcting behavior, escalation only when truly needed, complete work not "mostly done."

## The Core Loop

```
Human Intent → Agent Execution → Verified Result
       ↑                              ↓
       └──────── Minimum ─────────────┘
          (intervention only on true failure)
```

Every feature maps to this loop: Prometheus extracts intent, Metis catches ambiguities, Momus verifies plans, the orchestrator coordinates without micromanagement, Todo Continuation forces completion, the Category System routes to optimal models, Background Agents enable parallel research, Wisdom Accumulation prevents repetition.