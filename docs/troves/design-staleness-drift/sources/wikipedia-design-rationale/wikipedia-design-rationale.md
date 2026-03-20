---
source-id: wikipedia-design-rationale
type: web
url: https://en.wikipedia.org/wiki/Design_rationale
fetched: 2026-03-19
---

# Design Rationale — Wikipedia

## Definition

A design rationale is an explicit documentation of the reasons behind decisions made when designing a system or artifact. Originally developed by W.R. Kunz and Horst Rittel, it seeks to provide argumentation-based structure to the collaborative process of addressing wicked problems.

## Major Frameworks (Chronological)

- **IBIS** (Issue-Based Information System) — Kunz & Rittel, 1970s. Issues → Positions → Arguments
- **gIBIS** — graphical IBIS for hypertext environments
- **Potts & Bruns** — extended IBIS for software engineering
- **DRL** (Decision Representation Language) — extends Potts & Bruns; decision problems, alternatives, goals, claims
- **QOC** (Questions, Options, Criteria) — aka Design Space Analysis
- **RATSpeak** / **SEURAT** — Software Engineering Using RATionale; inference over rationale for impact assessment
- **DRed** (Design Rationale Editor) — Rolls-Royce; successful industrial adoption (6% fuel saving in Trent 1000)
- **Win-Win** — collaborative negotiation model

## Uses of Design Rationale

1. Improve documentation of the design process
2. Verify design methodology and resulting artifacts
3. Support analysis and explanation of design process
4. Enhance reusability of design artifacts
5. Avoid repeating past mistakes
6. Save time during system upgrades

## Why It's Not Widely Adopted

Despite decades of research, design rationale capture has NOT achieved widespread industrial use. Primary barriers:
- **Capture overhead** — documenting rationale is cumbersome during active design work
- **Mismatch with work practices** — structured rationale capture interrupts natural design flow
- **Cost-benefit perception** — benefits are long-term but costs are immediate

## Key Insight for Swain

The academic consensus is clear: the *concept* of capturing design rationale is valuable, but *every framework that adds capture overhead has failed to achieve adoption*. The successful cases (DRed at Rolls-Royce) succeeded by making capture a natural byproduct of the design methodology itself, not an additional step.

This suggests swain should NOT create a heavy DDR artifact type. Instead, rationale should be captured within existing artifacts (ADRs for decisions, Design Intent sections for vision) with minimal additional overhead.
