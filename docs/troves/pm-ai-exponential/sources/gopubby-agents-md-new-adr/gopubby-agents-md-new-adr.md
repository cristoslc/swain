---
source-id: "gopubby-agents-md-new-adr"
title: "AGENTS.md is the New Architecture Decision Record (ADR)"
type: web
url: "https://ai.gopubby.com/agents-md-is-the-ew-architecture-decision-record-adr-3cfb6bdd6f2c"
fetched: 2026-03-21T00:00:00Z
hash: "5bbcd82db4f8eb03b331c35a81420342386a6deb8763388f64e46edb3eba6809"
---

# AGENTS.md is the New Architecture Decision Record (ADR)

**Author:** Faisal Feroz, Chief Technical Architect
**Date:** January 7, 2026
**Reading time:** 11 min

## The core thesis

The most important architecture documentation today isn't primarily for humans anymore — it's for AI agents. The architecture decisions that matter most now tell Claude, Codex, and other coding agents how to behave in your codebase. Not what you decided last quarter, but what rules they must follow right now.

## ADRs vs AGENTS.md

- **Traditional ADRs answer:** "What did we decide, and why?"
- **AGENTS.md answers:** "Given what we decided, what must never happen, and what must always happen, when changing this code?"

That shift matters because agentic workflows multiply change velocity.

## Why AI-facing documentation matters

You can encode your senior engineer instincts directly into a file that every AI agent reads before touching your code:
- API responses must include tracing headers? Put it in AGENTS.md.
- Database migrations follow a specific rollback pattern? Specify it once.
- PII must not leak into logs? Make it a rule.

## Constraints over prompts

The durable value isn't in how you prompt today. It's in the constraints you institutionalize that survive both new hires and new models. When GPT-6 or Claude Opus 6 launches, prompts need rewriting. But architectural rules should remain stable.

## What belongs in AGENTS.md

1. **Architecture boundaries and layering rules** — encode which modules can depend on which others
2. **Data handling and privacy requirements** — where data can flow, how it must be logged
3. **Error handling patterns** — how errors propagate, what gets logged, how retries work
4. **Testing expectations and quality bars** — what tests are required for what changes
5. **Performance and scaling considerations** — forbidden patterns like N+1 queries
6. **Security guardrails and compliance requirements** — authentication, authorization, input validation

## The key distinction: passive vs active documentation

- **ADRs are passive:** You had to remember they existed, keep them updated, actively choose to read them.
- **AGENTS.md is active:** Every AI-assisted coding session consults them. Every agent-generated PR reflects them. They're not documentation you might read; they're rules that get enforced.

## How this changes the architect's role

Traditional model: architect makes decisions, writes them down, hopes people read them, catches problems in code review. That model is breaking down — when a single engineer with AI outputs 10x more code, reviewing it all is impossible.

AGENTS.md flips this: instead of reviewing after the fact, you provide guidance before code gets written. A junior engineer using Claude Code at 2 AM inherits your 20+ years of experience through the rules you've encoded.

**This is how you scale senior engineering judgment across a larger AI-augmented team.**

## Practical patterns

- Start with your most painful repeated mistakes
- Layer rules hierarchically — root AGENTS.md at repo level, service-level extensions
- Make rules testable where possible
- Keep it maintained alongside architecture changes (unlike immutable ADRs)
- Use it for onboarding, not just AI — if you can't explain a constraint clearly enough for AI, you haven't explained it clearly enough for humans

## The bottom line

> "In the age of AI-assisted development, your most valuable architecture artifact isn't a historical record of decisions made. It's an executable specification of constraints that must hold. Not what we decided, but what must be true."
