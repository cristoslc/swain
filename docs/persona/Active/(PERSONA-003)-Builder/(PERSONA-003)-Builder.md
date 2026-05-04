---
title: "Builder"
artifact: PERSONA-003
track: standing
status: Active
author: cristos
created: 2026-04-18
last-updated: 2026-04-18
linked-artifacts:
  - PERSONA-004
depends-on-artifacts: []
trove: builders-vs-shippers-agentic-coding@qry-2026-04-18
research-source:
  - the-impact-of-ai-on-software-engineers-in-2026-key-trends
  - tech-debt
  - developer-productivity
---

# Builder

## Archetype Label

Quality-Focused Craft Engineer

## Demographic Summary

- **Role:** Senior or staff engineer, architect, or tech lead
- **Technical proficiency:** High — deep expertise in system design and code quality
- **Project type:** Systems with long lifecycles where maintainability matters
- **AI usage:** Heavy but selective — delegates tedious work to agents, keeps control of architecture and review
- **Environment:** Professional team or solo project where codebase health affects velocity

## Goals and Motivations

1. **Keep the codebase healthy.** Sees the codebase as a shared craft artifact. Good architecture is non-negotiable.
2. **Offload tedious work to AI.** Finds real value in delegating refactoring, migrations, and test coverage — work that is laborious but not hard.
3. **Stay at the conceptual level.** Wants to focus on what to build, not how to type it. AI removes typing as a bottleneck.
4. **Cut the debugging burden from AI slop.** Pays a hidden cost fixing bugs in code that other people's agents made. Wants tools that stop bad AI output before it lands.

## Frustrations and Pain Points

1. **AI slop overload.** Drowning in low-quality AI-generated code from teammates. The volume exceeds what manual review can catch.
2. **The Builder Tax.** Spends more time debugging AI bugs than doing real work. This hidden cost does not show up in velocity metrics.
3. **Identity loss.** The craft skills that defined good engineering feel devalued when agents can write decent code faster than humans can type.
4. **No tradeoff framework.** When a Shipper ships fast but piles up debt, there is no agreed way to decide when speed is worth the cost.

## Behavioral Patterns

- Uses AI for well-scoped tasks: refactoring, migrations, test coverage, large codebase changes. Reviews output carefully.
- Catches patterns in AI-generated code that less experienced reviewers miss.
- Flags changes that violate architectural patterns — even when the code works.
- Fixes nagging bugs and small optimizations that were not worth the time before AI.
- Refuses to ship code that "works but should not be done this way" — even under deadline pressure.

## Context of Use

- **When:** Throughout development — code review, refactoring, architecture planning
- **Where:** IDE with AI agent, terminal, code review tools, ADRs
- **How:** Gives agents precise scope and constraints. Reviews output against standards. Escalates when quality thresholds are not met.
- **Frequency:** Daily. Active AI user with human judgment as the final gate.

## Research Basis

From the Pragmatic Engineer 2026 AI tooling survey (900+ respondents). The survey identified Builders as people who "care about quality, good architecture, following good coding practices, and who talk about the craft of software engineering."

Key findings:

- Builders find AI most useful for dull but non-hard work (refactoring, migrations, tests)
- Builders are hit hardest by AI slop and spend the most time debugging AI bugs
- Some Builders feel identity loss as hands-on coding becomes less justifiable
- The Builder Tax — the hidden debugging cost — is invisible to velocity metrics

Sources: Pragmatic Engineer 2026 survey, Boswell tag syntheses on tech-debt and developer-productivity

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-18 | — | Created from Boswell research-backed archetype |