---
title: "The 2026 MCP Roadmap"
source-url: "https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/"
fetch-date: "2026-05-01"
type: web-page
publisher: "Model Context Protocol Blog"
---

# The 2026 MCP Roadmap

## Current State (March 2026)

MCP runs in production at companies large and small. Powers agent workflows. Shaped by community Working Groups, SEPs, and formal governance under the Linux Foundation.

## Four Priority Areas for 2026

1. **Transport evolution** — making Streamable HTTP work statelessly at scale, with proper load balancer and proxy support.
2. **Agent communication** — closing lifecycle gaps in the Tasks primitive (retry semantics, expiry policies).
3. **Governance maturation** — formal contributor ladder and delegation model.
4. **Enterprise readiness** — audit trails, SSO-integrated auth, and gateway patterns.

## Strategic Decisions

- Keeping the spec small is deliberate — grounded in MCP design principles.
- Tasks primitive (experimental) works well for its design scope. Early production use surfaced concrete lifecycle gaps.
- 2026 roadmap explicitly addresses gaps that triggered "is MCP dying?" concerns.
- Context bloat addressed through reference-based results and better streaming.
- Auth limitations fixed with SSO-integrated Cross-App Access flows.
- Enterprise observability (audit trails, gateway patterns) is a first-class 2026 priority.

## Tool Discovery Evolution

The roadmap addresses context window bloat — a key concern for tools packaging methodology as MCP. Reference-based results and streaming improvements mean tool-heavy MCP servers become more viable over time.
