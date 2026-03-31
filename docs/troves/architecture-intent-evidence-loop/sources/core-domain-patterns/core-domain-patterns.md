---
source-id: "core-domain-patterns"
title: "Core Domain Patterns"
type: web
url: "https://medium.com/nick-tune-tech-strategy-blog/core-domain-patterns-941f89446af5"
fetched: 2026-03-29T00:00:00Z
hash: "41b76b95dc12edc192aa50684f1abb16c0d8c5346ac014e421f778b127b408c2"
---

# Core Domain Patterns

**Author:** Nick Tune
**Published:** January 19, 2020
**Source:** Nick Tune's Tech Strategy Blog (Medium)
**Capability:** Cap 2 -- Find Boundaries / Cap 8 -- Design from the Business (Go Deeper)

## Content

Time and resources are limited. How we spend our time when developing software systems is the most fundamental challenge. The Core Domain concept from DDD provides a counter-balance to developers' natural tendency to gravitate toward technically interesting challenges.

### Core, Supporting, and Generic Domains

- **Core Domains**: Parts of the system with the highest ROI for the business -- high business differentiation potential AND sufficient complexity
- **Supporting Domains**: Business necessities with limited ROI, contain business concepts but limited differentiation
- **Generic Domains**: Concepts not unique to the domain (user identity, email, payments) -- consider buying SaaS or using open source

### The Classification Framework

Tune uses a 2x2 visualization with axes of **business differentiation** (y-axis) and **model complexity** (x-axis) to identify patterns.

### Pattern Catalog

**Decisive Core**: Extremely complex AND maximum business differentiation. Whichever organization gets this right becomes market leader. Requires big investment.

**Short-term Core**: High differentiation but low complexity. Not a defensible advantage -- competition catches up relatively quickly.

**Hidden Core**: Low complexity but high differentiation potential. Often means complexity is still handled manually by employees. Business should ask: "Can we leverage technology to replace manual processes?"

**Table Stakes Former Core**: Natural lifecycle for innovation -- over time it becomes table stakes. No longer differentiating but still needed. Example: contactless payments.

**Commoditised Core**: What was once core becomes generic -- any company can use SaaS or open source. Example: advanced search capabilities commoditized by Elasticsearch.

**Black Swan Core**: A commodity unexpectedly becomes a core domain. Example: Slack -- IRC was established, but an internal chat tool became a $13 billion product.

**Big Bet Core / Disruptive Core**: Differentiation potential is unknown. Potentially disrupting an industry. Organization injects significant resources as a bet.

**Suspect Supporting**: Super complex yet only supporting -- accidental complexity may be too high. Should have a clear plan to reduce complexity.

### Evolution Over Time

Core domains are not static -- they evolve:
- Decisive Core -> Table Stakes Former Core -> Commoditised Core (typical trajectory)
- Generic -> Black Swan Core (rare but high-impact)
- Understanding evolution requires Wardley Mapping and the Cynefin framework

## Relevance to Intent-Evidence Loop

Core domain classification is fundamentally about **allocating architectural attention** -- a meta-intent decision. The pattern catalog helps answer: where should the intent-evidence loop be most rigorous?

- **Decisive Core**: Requires the most detailed intent specification and most rigorous evidence collection and reconciliation
- **Generic Domains**: Intent can be minimal ("use a standard solution"); evidence is mainly "does it still work?"
- **Supporting Domains**: Moderate intent; reconciliation should watch for creeping complexity

For swain, this connects to the trove's question about where Observable Reality deserves the most investment. Core domain classification provides the framework: invest evidence-collection effort proportionally to business differentiation potential.

The evolution patterns (Former Core, Commoditised Core) show that reconciliation must also check whether the *classification itself* remains valid -- the meta-reconciliation problem.
