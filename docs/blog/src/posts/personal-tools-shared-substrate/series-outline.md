---
title: "Personal Tools, Shared Substrate — Series Outline"
description: "Editorial outline for a blog series on how agentic capability moves from individual to organizational use — and what that inverts about enterprise adoption."
eleventyExcludeFromCollections: true
permalink: false
---

# Personal Tools, Shared Substrate

A blog series on the organizational form of agentic capability. The move from individual-scale agent tooling to organizational deployment doesn't follow the adoption curve previous enterprise software cycles followed. Agents made custom artifacts cheap, which made personal-first the default. Organizations can't standardize what individuals build; they can only standardize the substrate that individual builds run on.

Companion series to [Excisable Software](../excisable-software/series-outline.md). Both series examine where the unit of reuse is shifting in the agentic era — *Excisable Software* from the registry/supply-chain angle, this series from the individual-to-organization angle. The **personalization gradient** is the bridge concept.

Draft. Not workshopped. Working title is probably fine but revisit before publishing.

## Working thesis

Agents make custom artifacts cheap, which inverts the prior enterprise adoption cycle. Previously, organizations adopted shared artifacts because custom was expensive; individuals used the organization's tool. Now, individuals build personal apparatus by default, and there is no canonical version for the organization to deploy. The organizational move is therefore to standardize the *substrate* — durable runs, sandboxes, boundaries, artifacts, review surfaces — not the *capabilities*. Personal tools, shared substrate.

Corollary: the pieces that survive the individual↔organizational transition are the ones low on the personalization gradient (shared tools, shared disciplines, constrained domains). High-personalization workflows don't travel; they die with their author or require excision into lower-personalization fragments.

## Arc (draft — 4 posts, 2 pairs)

| Pair | # | Post | Stance | Status |
|------|---|------|--------|--------|
| 1 | 1 | The Adoption Curve Doesn't Fit | Diagnosis: previous enterprise adoption cycles converged on shared artifacts; agents break that assumption | Planned |
| 1 | 2 | What Agents Made Cheap | Mechanism: custom artifacts cost a programmer's time before; they cost a conversation now | Planned |
| 2 | 3 | Substrate, Not Capability | The organizational move is to standardize runtimes (Spectre-style), not what agents do | Planned |
| 2 | 4 | The Personalization Gradient | Which capabilities travel wholesale, which excise, which die with their author | Planned |

Posts 1+2 cover "what's different" (diagnosis + mechanism). Posts 3+4 cover "what to do about it" (substrate standardization + capability-layer taxonomy).

## Post 1: The Adoption Curve Doesn't Fit

The diagnostic post. Rogers/Moore-style adoption curves assume an artifact that diffuses — each adopter gets approximately the same thing, with differences in integration and config. Enterprise software cycles (SaaS, containers, cloud platforms) followed this shape. Agentic capability doesn't.

Individual users build idiosyncratic apparatus: custom CLAUDE.md files, personal skills, memory stores tuned to their domain. No two working setups look the same. The Harvey blog's own diagnosis — "leverage is moving up a level, from individual to organization" — assumes the leverage is transferable. Some of it is. A lot isn't.

The post doesn't say the adoption curve is wrong — it says the curve is measuring a different substrate than people think. Diffusion is happening, but at the substrate level (AGENTS.md conventions, MCP protocols, sandbox models), not the capability level (someone's actual working setup).

## Post 2: What Agents Made Cheap

The mechanism post. Prior enterprise adoption cycles converged on shared artifacts because custom was expensive — you had to pay a programmer, or wait for a vendor. Configuration was the settlement: everyone runs the same software, each site tweaks config.

Agents collapse the cost of custom. A skill file is 150 lines of markdown and a weekend. A memory system is a directory of text. A custom lifecycle is a shell script wrapping `gh`. The cost of personal customization drops below the cost of adopting-and-adapting someone else's tool for a growing class of capabilities.

Historical analog: spreadsheets let non-programmers build personal tooling, and the organizational response was to standardize on Excel-the-platform, not on the specific spreadsheets. Same move here, at a bigger scale.

## Post 3: Substrate, Not Capability

The prescriptive post. What Spectre actually standardizes is the *runtime*, not *what agents do*. Durable runs, ephemeral workers, scoped credentials, sandbox boundaries, review surfaces, audit trails, cost accounting. The capability layer — what the agent actually does in a given run — is still personal or team-scoped.

Why this works: substrate has shared properties everyone needs (durability, isolation, observability, compliance). Capability has personal properties that don't generalize. Attempting to standardize capabilities produces the enterprise-software failure mode — vendor-built "AI agents for legal" that no practitioner actually uses because they don't match that practitioner's reasoning flow.

The analog: Docker standardized the runtime for containerized applications; it didn't standardize the applications. Agent platforms are walking the same path.

## Post 4: The Personalization Gradient

The taxonomic post. Not all capabilities sit at the same point on the personal-to-shared axis. A rough gradient:

- **Low personalization — wholesale adoption works.** Shared-tool wrappers (office-skills, git-aware skills), shared-discipline encodings (TDD, brainstorming, verification — obra/superpowers), constrained-domain pipelines (media-summary). These encode knowledge with one agreed shape. People adopt them as-is.
- **Middle — excision works.** Components inside high-personalization frameworks. Individual scripts, utilities, verification patterns. Not the whole framework, but specific liftable pieces.
- **High personalization — personal only.** Advanced composite workflows that encode the author's judgment about how to manage their work. These rarely travel intact. They may travel as *patterns* (someone else builds their own version of the same idea) but not as *implementations*.

The gradient is the bridge to *Excisable Software*. The pieces that survive organizational adoption are low or middle on the gradient. The pieces that survive registry collapse are excisable. Strong correlation, different axes.

Pragmatic implication: when building a skill or capability, ask where it sits on the gradient before deciding how to package it. Low-personalization → publish as a drop-in. Middle → publish with explicit excision points and tests. High → publish as narrative (blog, retro) so others can build their own version.

## Editorial notes

- **Series must have an even number of posts (minimum two).** No single-post series. Posts don't need to drop simultaneously. Current arc is 4, which satisfies this.
- **This series complements *Excisable Software*.** The personalization gradient appears in both but does different work. In *Excisable* it's the reason monoliths fight extraction; here it's the reason organizational adoption standardizes substrate, not capability. Cross-reference, don't duplicate.
- **Audience is platform engineers, agent-platform builders, and in-house AI leads — not solo agent operators.** The solo-operator audience gets *Excisable Software*. This series is for people deciding what their organization standardizes on.
- **Be wary of Harvey/Spectre worship.** Spectre is the cleanest public example of substrate standardization, but it's *one* architecture by *one* firm in *one* domain. Use it as an existence proof, not as a blueprint.
- **Don't absorb the "org form of agentic capability" question — it's bigger than this series.** Staffing, apprenticeship, pricing, practice-area structure (Harvey's broader claim) are downstream of the substrate/capability split but deserve their own treatment.
