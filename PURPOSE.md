# Swain

Swain makes agentic development safe, aligned, and sustainable for a solo developer working with AI coding agents.

## Why this exists

AI coding agents are fast, stateless, and uncritical. They will build whatever they're told, or whatever they infer from incomplete context. They operate with real credentials, real filesystem access, and real consequences. Left unsupervised, they produce code that passes tests but silently violates architectural constraints, drifts from prior decisions, and accumulates structural debt that no test suite can detect. Left uncontained, a confused or compromised agent can cause damage far beyond its intended scope.

The problem is threefold:

**Alignment.** The gap between human decisions and agent execution widens silently over time. Decisions made in week one are forgotten by week twelve. Architectural constraints are ignored under speed pressure. The reasoning behind past choices evaporates when the conversation ends.

**Safety.** Agents run with the operator's authority but without the operator's judgment. As agents gain autonomy — from interactive pair-programming to unattended background workers — the security model must keep pace. Without containment, the operator must either supervise every action or accept unbounded risk.

**Sustainability.** The operator's cognitive resources are finite. Without structure, every session surfaces the entire open backlog, every decision is re-derived from scratch, and the operator never gets closure. The system that was supposed to support decisions becomes a decision tax.

Swain addresses all three. It captures what was decided and structures it so agents can act on it. It contains what agents can access so mistakes have bounded blast radius. And it manages the operator's attention so decisions are clustered, bounded, and closeable.

## The alignment loop

Swain's architecture rests on a four-phase loop:

**Intent** — What has been decided. Specs, ADRs, architectural constraints, component boundaries, goals. Human-authored declarations of what should be true. Intent is the operator's domain: swain helps structure and connect it, but the operator makes the decisions.

**Execution** — Where intent meets reality. Agents implementing specs, building features, running migrations. The transition from "decided" to "done." Swain does not control execution — agents are black boxes. Swain provides the alignment context (what constraints apply, what decisions govern this work) and verifies outcomes.

**Evidence** — What can be observed. Git history, test results, dependency graphs, drift reports, agent session outputs. Evidence is derived from verifiable sources, not from declarations. It exists independently of intent and may contradict it.

**Reconciliation** — The structured comparison of intent against evidence. Drift reports, retrospectives, ADR compliance checks, spec gap analyses. Reconciliation is where the system learns: where intent was wrong, where evidence reveals something unexpected, where the gap between plan and reality has grown too wide.

The loop is continuous, and reconciliation flows in both directions. Most often, execution has drifted from intent and needs to be corrected — a spec was partially implemented, an ADR was violated, a boundary was crossed. The fix is in the code, not the decision. But sometimes the drift reveals that intent was wrong — a boundary that agents repeatedly violate may be poorly drawn, a constraint that every implementation works around may be outdated. The fix is in the decision, not the code. Reconciliation surfaces the divergence; the operator decides which side to update.

## Three questions

Everything swain does serves one of three questions:

1. **"What needs a decision?"** — The operator's question. What intent is missing, ambiguous, or stale? Where has the operator's attention been requested but not yet given?

2. **"What's ready for execution?"** — The agent's question. What intent is structured enough to act on? What constraints apply? What prior decisions govern this work?

3. **"Does reality still match intent?"** — The system's question. Where has evidence diverged from what was declared? What decisions are no longer holding? What needs the operator's attention?

## Who this is for

**The operator** — a solo developer who makes decisions and delegates implementation to AI coding agents. Swain is the operator's decision-support system: it captures intent, surfaces what needs attention, and preserves the reasoning behind choices. The operator steers; swain keeps the record.

**The agent** — any AI coding agent that reads markdown. Swain provides alignment context (acceptance criteria, scope boundaries, constraints, dependency graphs) and verifies outcomes against that context. How the agent works internally is irrelevant. Any agent that reads structured text can participate.

## Foundational principles

**Artifacts are the single source of truth.** What was decided lives in artifacts — not in conversations, not in memory, not in the operator's head. If it's not in an artifact, it wasn't decided.

**Git is the persistence layer.** Swain does not maintain its own database. Everything is markdown files in a git repository. Version history, blame, and diff are the audit trail.

**Agents are black boxes.** Swain does not prescribe or constrain how agents work internally. It provides inputs (intent, context, constraints) and verifies outputs (evidence, compliance, completion). The agent runtime is interchangeable.

**Intent and evidence are separate things.** Source code tells you what exists; intent declares what should exist. These must not be collapsed. Architecture documents are amortized derivation — caches of structural understanding that are cheaper to validate than to re-derive. The cache validity problem is where reconciliation earns its keep.

**Intent is malleable.** Decisions are hypotheses, not commandments. When evidence repeatedly contradicts intent — when agents keep violating a boundary, when implementations consistently deviate from a spec — that's a signal. The boundary may be wrong, the constraint may be outdated, or the operator's mental model may need updating. Reconciliation doesn't just enforce intent; it challenges it.

**Execution is where learning happens.** Agents encounter reality that specs didn't anticipate. Patterns emerge from implementation that no amount of upfront planning could predict. Execution is not a mechanical translation of intent — it's a source of evidence about whether intent was well-formed in the first place. Repeated friction at a boundary is information, not failure.

**Reconciliation is not blame.** Drift between intent and evidence is normal and expected. The goal is detection and resolution, not attribution. Reconciliation surfaces divergence so the operator can decide what to do about it — which may mean updating the intent, not fixing the evidence.

## Appraisal

Every piece of work competes for two scarce resources: the operator's **attention** (cognitive load, decision-making capacity) and **calendar time** (which has opportunity cost — time spent here is time not spent elsewhere). Swain needs a way to express *why* work matters, not just *what order* to do it in. Priority labels without grounding are gut feelings dressed up as decisions.

Swain appraises work on three value dimensions:

**Capability** — does this work enable something the system cannot do today? New functionality, new integrations, new audiences served. Capability value is highest when the gap between "what exists" and "what's needed" is wide and clearly articulated.

**Efficiency** — does this work reduce ongoing cost? Fewer manual steps, less cognitive overhead per session, faster feedback loops, less drift to detect and repair. Efficiency value compounds: a small reduction in per-session friction pays dividends across every future session.

**Risk reduction** — does this work prevent or bound a potential loss? Security vulnerabilities, data loss scenarios, architectural dead-ends, bus-factor exposure. Risk value is asymmetric: the expected cost of the bad outcome, discounted by its probability, often dwarfs the cost of prevention.

These dimensions are not exclusive — a single piece of work can deliver on all three. But naming them separately forces honest assessment. Work that scores zero on all three dimensions is work that should not be done, regardless of how easy it is.

### Return

Return is value delivered per unit of cost invested. Cost is measured in operator attention and calendar time — the two resources that don't scale.

At the artifact level, this means every container (Vision, Initiative, Epic) and every implementable (Spec) can express its expected value and estimated cost. The ratio is the return. High-value, low-cost work should happen first. Low-value, high-cost work should be deferred or cut. This is not a replacement for judgment — it is a framework for making judgment legible and comparable.

The system computes return from operator-supplied estimates. It does not pretend to be precise. A rough ratio that distinguishes "obviously worth doing" from "probably not worth doing" is more useful than a precise priority label that means different things on different days.

## What swain is not

- **Not a team tool.** Solo operator with AI agents. Team coordination is a different problem with different solutions.
- **Not an agent runtime.** Alignment and verification, not execution. Swain works with any agent that reads markdown.
- **Not a replacement for git.** Git is the foundation. Swain is an opinionated layer on top of it.
- **Not prescriptive about agent choice.** Swap runtimes freely. Swain doesn't care which agent you use.

---

## Revision history

| Date | Change | Context |
|------|--------|---------|
| 2026-03-24 | Initial creation | Supersedes VISION-001. Reframes swain's identity around the Intent-Execution-Evidence-Reconciliation loop, informed by architecture-intent-evidence-loop trove research. |
