---
source-id: "harmel-law-scaling-architecture-conversationally"
title: "Scaling the Practice of Architecture, Conversationally"
type: web
url: "https://martinfowler.com/articles/scaling-architecture-conversationally.html"
fetched: 2026-03-29T00:00:00Z
hash: "2f8581637ca5a51cbe4fccf5a00259f6a17d265d117af7a39b449b249e3405e2"
---

# Scaling the Practice of Architecture, Conversationally

**By Andrew Harmel-Law | Published December 15, 2021**

## Overview

This article presents an alternative approach to software architecture that replaces traditional top-down decision-making with decentralized, conversation-driven practices. Rather than concentrating architectural decisions with a small group of experts, this model empowers teams to make decisions collaboratively while maintaining coherence through supporting mechanisms.

## The Core Element: The Advice Process

The foundation of this approach is the Advice Process, which operates on a simple rule with one qualifier:

**The Rule:** Anyone can make architectural decisions.

**The Qualifier:** Before deciding, the decision-maker must consult two groups: those meaningfully affected by the decision and people with relevant expertise in that area.

Importantly, decision-makers need not follow the advice received, but they must actively seek it out, listen carefully, and record it. As the author explains, "we are not looking for consensus here, but we are looking for a broad range of inputs and voices."

The Advice Process encourages better decision-making by:
- Making decisions faster
- Increasing accountability
- Building ownership among those implementing decisions
- Growing the pool of available decision-takers

## The Four Supporting Elements

### 1. Architectural Decision Records (ADRs)

Lightweight documents stored alongside code artifacts that capture:
- Title with unique identifier
- Status (Draft, Proposed, Adopted, Superseded, Retired)
- Decision statement
- Context and forces driving the decision
- Options considered with pros and cons
- Consequences (positive and negative)
- Advice received during the decision process

ADRs serve dual purposes: documenting decisions and teaching teams how to think architecturally by acting as a "thinking checklist."

### 2. Architecture Advisory Forum (AAF)

A weekly, hour-long meeting where:
- Team representatives share upcoming spikes
- New proposed decisions (in ADR form) are discussed
- Previous decisions are revisited
- Metrics and trends are reviewed

Unlike traditional Architecture Review Boards, the AAF maintains the Advice Process principle -- decisions remain owned by originators, not the forum. The forum's strength lies in creating a learning environment where diverse perspectives surface together.

### 3. Team-Sourced Architectural Principles

Principles must be:
- Specific, measurable, achievable, realistic, and testable (SMART)
- Aligned with business strategy
- Clear about their implications
- Limited in number (8-15) so teams can remember them

An example principle: "Value independence of teams most highly -- Split solutions along team lines." This guides decisions without dictating solutions.

Principles differ from practices (like TDD or pair programming) and general principles (like "keep it simple"). They specifically evaluate architectural choices.

### 4. Technology Radar

A visualization tool mapping current technologies across quadrants (Techniques, Tools, Platforms, Languages & Frameworks) and rings reflecting adoption stages (Experiment, Adopt, Hold, Retire).

Teams build their own radar through workshops, creating a shared understanding of the technical landscape. Radar blips are referenced in ADRs to flag adherence or intended changes to the existing technology portfolio.

## How It Works in Practice

When an architectural decision emerges:

1. **Context Development** - Understanding the "why" and surrounding forces
2. **Principle & Radar Review** - Checking alignment with existing guidance
3. **Criteria & Options Definition** - Establishing evaluation framework
4. **Advice Seeking** - Engaging relevant stakeholders and experts
5. **ADR Creation** - Documenting thinking, advice, and final decision
6. **AAF Discussion** - Sharing insights with broader team

Throughout, conversations remain central. As the article notes, developers' understanding of architecture matters more than architects' diagrams, making shared conversation essential.

## Failure Modes to Avoid

**Good Failures:** Mini failures by less experienced decision-makers that facilitate learning. These should be celebrated.

**Incomplete Participation:** Failing to include all necessary voices creates an illusion of success while limiting actual benefits.

**Undocumented Decisions:** Off-grid decisions signal process gaps; treat them as learning opportunities, not violations.

**Shadow Architecture:** The most dangerous failure -- architects making decisions behind the scenes while maintaining the appearance of decentralization. This destroys the entire approach.

## Key Principles

The author emphasizes that architects' roles shift from decision-makers to conversation facilitators. Success requires:

- Trusting people with decision authority
- Creating psychological safety for learning
- Actively amplifying diverse voices
- Celebrating failures transparently
- Maintaining vigilance against reverting to control

The interplay between these five elements -- the Advice Process, ADRs, Advisory Forum, Principles, and Tech Radar -- creates mutual reinforcement around "conversations, learning and safety."

## Conclusion

This conversational architecture approach leverages collective intelligence rather than relying on a small group of experts. When teams are empowered and given tools to succeed, they naturally begin optimizing beyond what architects might have imagined, accessing "the collective intelligence of the many, over reliance on the much more restricted intelligence of the few."
