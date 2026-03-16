---
title: "Postflight Summary Design"
artifact: SPIKE-024
track: container
status: Proposed
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
question: "How should swain skills invoke postflight summaries, what context should they pass, and what does 'keeping the user in flow' mean concretely for the output format?"
gate: Pre-development
risks-addressed:
  - Postflight output that's too verbose breaks flow instead of preserving it
  - Invocation mechanism that requires heavy modification to every calling skill
  - Recap quality that's no better than listing file paths (the GH #51 problem)
  - "In flow" being undefined leads to inconsistent postflight experiences across skills
linked-artifacts:
  - EPIC-022
  - "github:cristoslc/swain#51"
trove: ""
---

# Postflight Summary Design

## Summary

<!-- Populated when transitioning to Complete. -->

## Question

How should swain skills invoke postflight summaries, what context should they pass, and what does "keeping the user in flow" mean concretely for the output format?

## Go / No-Go Criteria

**GO (build postflight):**
- A clear invocation protocol exists that doesn't require heavy changes to every calling skill
- "In flow" can be defined concretely enough to guide output design
- The recap can be meaningfully better than what skills produce today (domain terms, not just file lists)

**NO-GO (defer):**
- Every skill's completion context is so different that a unified postflight adds more complexity than value
- The recap requires re-reading so much context that it adds unacceptable latency
- "In flow" remains too vague to act on

## Investigation Areas

### 1. Invocation mechanism

How does a swain skill tell swain-status "I just finished, show a postflight"?

Options to evaluate:
- **Skill invocation**: the completing skill invokes swain-status as a chained skill call with postflight context
- **Convention**: the completing skill writes a postflight context blob (JSON/markdown) to a known location, then invokes swain-status
- **Inline**: swain-status exposes a function/template that skills embed directly in their completion output (no separate invocation)
- **Hook**: a Claude Code hook that fires after any skill completion, invoking swain-status automatically

Use skill-creator to evaluate which approach best fits swain-status's current architecture.

### 2. Context-passing protocol

What does the calling skill need to pass to postflight?

Minimum viable context:
- Which artifact(s) were just worked on (artifact IDs)
- What action was performed (implemented, researched, transitioned, synced, dispatched)
- Whether it succeeded or failed

Nice-to-have:
- Commits produced
- Duration
- Tasks completed (tk IDs)

Evaluate: is a structured JSON blob the right format, or is a natural-language summary from the calling skill sufficient?

### 3. Defining "in flow"

The operator asked for postflights that "keep the user in flow." What does this mean concretely?

Investigate:
- **Brevity**: how many lines/tokens before output becomes interruptive? (hypothesis: 3-5 lines)
- **Actionability**: does the postflight end with a clear next action the operator can take immediately?
- **Progressive disclosure**: can the operator expand from postflight to full dashboard with a single command?
- **Latency**: how fast must the postflight appear? (if it takes 10 seconds to generate, that breaks flow)
- **Tone**: should it read like a status update, a nudge, a handoff? What voice preserves momentum?

Look at examples from other tools:
- How do CI/CD systems present post-deploy summaries?
- How do code review tools present post-merge summaries?
- How does `git` itself present post-operation summaries (push, merge, rebase)?

### 4. Recap generation

How does the postflight produce a domain-context recap that's better than file lists?

Approach options:
- **Read the artifact**: postflight reads the artifact's title, goal/question, and summarizes in one sentence
- **Diff the status cache**: compare status cache before and after the activity — what moved? what unblocked?
- **Calling skill provides it**: the calling skill writes the domain recap as part of the context blob (it already has the context)
- **Hybrid**: calling skill provides the "what happened" line, postflight adds "what changed in the project" from status delta

### 5. Completion events inventory

Which swain skills have meaningful completion events that should trigger postflight?

Audit each skill:
- **swain-do**: task completion (tk close), implementation pass complete
- **swain-commission**: artifact created, artifact transitioned
- **swain-dispatch**: dispatch sent, dispatch completed (async — how to handle?)
- **swain-sync**: push complete
- **swain-search**: evidence pool collected
- **swain-retro**: retrospective complete
- **swain-release**: release tagged

For each: what's the natural completion moment? What context is available at that moment?

### 6. Relationship to swain-status architecture

How does postflight fit into swain-status's current design?

- Is it a new section in the agent summary template?
- Is it a separate output mode (like `--compact` for MOTD)?
- Does it need changes to the status script, the agent summary logic, or both?
- Can it reuse the recommendation engine as-is, or does it need a "scoped" recommendation (only considering what changed)?

## Findings

<!-- Populated during Active phase. -->

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation; informs EPIC-022 |
