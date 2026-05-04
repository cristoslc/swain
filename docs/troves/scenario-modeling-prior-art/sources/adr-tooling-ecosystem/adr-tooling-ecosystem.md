---
title: "ADR Tooling Ecosystem — Decision Capture Without Branching"
source-url: https://adr.github.io/adr-tooling/
source-type: web-page
fetched: 2026-04-28
transcript-source: web-fetch
---

# ADR Tooling Ecosystem

**Source:** https://adr.github.io/adr-tooling/

## Summary

The ADR tooling ecosystem (adr-tools, Log4brains, pyadr, madr-tools, ADR Manager, ADR Architecture Kit, and others) covers creation, lifecycle management, search, and publication of Architecture Decision Records. No tool in the ecosystem supports decision branching, counterfactual analysis, or "what would the artifact tree look like if a different decision had been made."

## Tools Surveyed

| Tool | Key capability | Alternatives/branching support |
|------|---------------|-------------------------------|
| **adr-tools** (npryce) | CLI to create Nygard-format ADRs, manage supersession | Supersession only — marks old ADR as superseded-by, does not model the alternative tree |
| **Log4brains** | Static site generator, VSCode integration, web publishing | None |
| **pyadr** | CLI lifecycle management (propose/accept/reject/deprecate/supersede) | Lifecycle states; no what-if |
| **madr-tools** | Node.js CLI for MADR format | None |
| **ADR Manager** | Web-based GitHub-connected editor | None |
| **ADR Architecture Kit** | Python YAML-structured ADRs, schema + validators | None |
| **Backstage ADR plugin** | Portal integration, search | None |
| **adr-log** | Keeps index.md updated | None |
| **dotnet-adr** | .NET cross-platform CLI | None |
| **ReflectRally** | Collaborative web app, review workflows | None |

## The Supersession Pattern (Closest Existing Primitive)

All ADR tools support "superseded-by" — a pointer from an old ADR to its replacement. This is a linear chain, not a branch:

```
ADR-001 (Accepted) → superseded-by → ADR-005 (Accepted)
```

The alternative that ADR-001 chose over ADR-005 is prose-only in the "Alternatives Considered" section. The "what would the artifact tree look like under ADR-001?" question cannot be answered by querying the tool — only by reading the prose.

## The Gap

No ADR tool answers: "Show me the system design that would have resulted if we had chosen option B in ADR-001 instead of option A." That downstream artifact tree does not exist. The decision's consequences are not modeled — only the decision itself.

## Relevance to swain

This is a confirmed unmet need in the ADR tooling space. swain's scenario modeling feature would be the first tool to surface "the tree under an alternative ADR" as a queryable graph. The supersession chain is the existing hook — scenarios could be implemented as "re-root the artifact graph using a different ADR state as input."
