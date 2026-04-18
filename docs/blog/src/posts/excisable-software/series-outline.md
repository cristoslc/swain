---
title: "Excisable Software — Series Outline"
description: "Editorial outline for a blog series on why agents will rebuild from concepts rather than import from registries."
eleventyExcludeFromCollections: true
permalink: false
---

# Excisable Software

A blog series on the shift in software reuse — from "import a package" to "rebuild from a concept." Driven by two forces: supply-chain trust collapse in public registries, and agent build capacity that makes local reconstruction affordable for a growing slice of problems.

Draft. Not workshopped. Save early so it doesn't drift.

Companion series: [Personal Tools, Shared Substrate](../personal-tools-shared-substrate/series-outline.md). The **personalization gradient** is the bridge concept — shareability tracks inversely with personalization, and the excisable pieces inside a high-personalization framework are exactly the low-personalization ones.

## Working thesis

In a supply-chain-compromised world, agents will rebuild from concepts rather than import from registries. The unit of reuse is shifting from "package" to "concept + evidence." Software architected for *excision* — pieces that can be lifted out with their context and reconstructed locally by an agent — will outlive software architected for import.

## Arc (draft)

| # | Post | Stance | Register | Status |
|---|------|--------|----------|--------|
| 1 | The Registry Is Burning | The import model is structurally doomed in public registries | Urgent, grounded | Planned |
| 2 | When Registries Persist | Steel-man — where the import model survives, and why | Bounded, fair | Planned |
| 3 | What Agents Do With a Concept vs a Package | Behavior observation — concept reconstruction beats blind import | Empirical | Planned |
| 4 | Excisability as a Design Property | What makes a piece liftable — concept + tests + evidence, no framework entanglement | Prescriptive | Planned |
| 5 | BBOM Fights Excision | Monolithic frameworks as legibility failures for extractor agents | Critical, self-implicating | Planned |
| 6 | Case Study: swain v1 → v2 | Migration from monolith to excisable | Reflective | Planned |

The arc moves from *problem* (registries failing) → *boundary* (where they still work) → *mechanism* (what agents actually do) → *design property* (how to build for excision) → *anti-pattern* (what fights it) → *case study* (swain as testbed).

## Post 1: The Registry Is Burning

The motivating observation. Supply-chain attacks on npm, PyPI, crates, actions have moved from "occasional incident" to "weekly event." Trust in public registries is structurally collapsing. The import-first model assumes the registry is a trusted intermediary; that assumption no longer holds for public registries.

Agents change the economics on the other side: if an agent can rebuild a well-specified piece locally in minutes for pennies, the trust cost of importing is no longer the only cost being weighed.

## Post 2: When Registries Persist

The steel-man. Registries don't disappear — they retreat to niches where trust is cheap and rebuild is expensive. The 2×2:

|                        | Rebuild cheap | Rebuild expensive |
|------------------------|---------------|-------------------|
| **Trust cheap**        | Either works; excision wins on recency | **Registries dominate** |
| **Trust expensive**    | Excision wins decisively | Contested; depends on stakes |

Registries persist where trust capability outweighs rebuild cost:

- **Internal enterprise registries.** Trust is an organizational capability — signed artifacts, approved vendors, audit trails, procurement pipelines. The registry is a trust substrate, not a convenience.
- **Regulatory / compliance domains.** FDA-regulated software, finance, aviation. You need provenance pointing to a specific version of a specific artifact, not "an agent rebuilt something equivalent." Equivalence is not a certifiable property.
- **High-complexity artifacts.** Kernels, cryptographic primitives, compilers, ML frameworks. The rebuild token budget is prohibitive, and the correctness bar is higher than an agent can verify without a canonical reference.
- **Protocol-critical interop.** HTTP parsers, TLS, wire-format libraries. A shared canonical implementation is required for correctness; "rebuilt equivalent" means a new bug surface for every caller.
- **Hardware-adjacent code.** Drivers, firmware, kernel modules. Correctness is coupled to physical artifacts that agents cannot observe.

The thesis is bounded: registries retreat to these niches, and excision becomes the default elsewhere. Both models coexist; the ratio shifts.

## Post 3: What Agents Do With a Concept vs a Package

Behavior observation. Give an agent a package, it imports — with whatever the package brings, including drift from what the caller actually needed. Give it a well-formed concept (spec + tests + evidence of prior use), it rebuilds locally, *narrower* and fitted to the caller's context.

Document the difference with concrete examples. The argument is empirical: the "concept-native" path produces smaller, more auditable code than the "import-native" path for a class of problems that's getting larger.

## Post 4: Excisability as a Design Property

Prescriptive. What makes a piece liftable by an extractor agent?

- A concept statement the agent can read (what this does, why).
- Tests the agent can run in isolation (executable definition of "correct").
- An evidence trove showing what was tried and rejected (context).
- No framework entanglement — no hidden coupling that requires importing the whole system.

Contrast with traditional "reusable" design (DRY, clean boundaries, good abstractions). Those optimize for human comprehension and compile-time composition. Excisability optimizes for agent extraction and local reconstruction. Different target, different architecture.

## Post 5: BBOM Fights Excision

The critical turn. Monolithic skill or framework designs — including swain v1 — are *big balls of mud* to an extractor agent. The internals may be sensible to the human author, but the boundaries are not legible from outside. An agent attempting to excise a piece drags in half the framework or bails.

This is the inverse of the legibility problem humans have with BBOMs: humans can sometimes navigate a BBOM because they can hold partial mental models and tolerate ambiguity. Agents can't — they need boundaries they can actually see.

Self-implicating: swain v1 is used as the example of what not to do. This is honest; it earns the next post.

## Post 6: Case Study — swain v1 → v2

Reflective. swain v1 was built as a monolith — skills tightly entangled with shared scripts, artifact types, and a bespoke lifecycle. It works for its sole operator but fails the extraction test: another agent cannot lift the "retrospectives" capability, or the "artifact graph" capability, and rebuild it elsewhere.

swain v2 is architected for excision. Each capability is a concept + tests + evidence trove with minimal cross-coupling. The operator continues using it; other agents can extract pieces without adopting the whole framework.

The experimental question: can another agent successfully excise piece X from swain v2 and rebuild it in context Y? If yes, excisability is a real design property. If no, the thesis needs revision.

## Editorial notes

- **Post 2 is load-bearing for credibility.** Without it the series reads as a naive anti-registry polemic. With it, the thesis becomes the bounded claim that registries retreat to specific niches.
- **The swain case study must not lead.** The industry-level argument has to stand on its own in posts 1–5. Post 6 is the contribution, not the premise.
- **Bridge to "Steering the Machine" is real but secondary.** Tests are how you verify an excised piece — alignment is a subtopic of excisability. Draw the bridge late, not early.
- **Watch register.** This is a platform / security / architecture argument. Audience is bigger than the solo-agent-builder audience of the first series. Jargon budget should be lower; examples from actual supply-chain incidents should be higher.
- **Working title "Excisable Software" is fine for now** — workshop later.
- **Series must have an even number of posts (minimum two).** No single-post series. Posts don't need to drop simultaneously. Current arc is 6, which satisfies this.
- **Standalone cross-ref:** [Don't Type Context. Collect It.](../dont-type-context-collect-it/index.md) is a standalone post about swain-search and research troves. It demonstrates the excisability property in practice — both the skill and its outputs are liftable without the framework. Post 4 ("Excisability as a Design Property") can reference it as a worked example.
