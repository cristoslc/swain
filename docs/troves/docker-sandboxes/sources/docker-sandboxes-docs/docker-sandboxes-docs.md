---
source-id: "docker-sandboxes-docs"
title: "Docker Sandboxes | Docker Docs"
type: documentation-site
url: "https://docs.docker.com/ai/sandboxes/"
fetched: 2026-03-18T02:17:59Z
hash: "dca294813377777936f6adbb73446675002036e11faa7a4c124a00e28da98b29"
highlights:
  - "index.md"
  - "architecture/index.md"
  - "agents/index.md"
  - "get-started/index.md"
  - "network-policies/index.md"
  - "troubleshooting/index.md"
selective: true
---

# Docker Sandboxes Docs

Selective mirror of the core Docker Sandboxes documentation from `docs.docker.com`.

## Captured pages

- `index.md` - overview, requirements, supported agents, basic usage
- `architecture/index.md` - microVM architecture, isolation model, persistence, networking
- `agents/index.md` - supported agent matrix and shared template environment
- `get-started/index.md` - first-run flow, credential setup, core CLI commands
- `network-policies/index.md` - outbound filtering model, defaults, logging, policy examples
- `troubleshooting/index.md` - common failures and recovery commands

## Structure summary

Docker positions Sandboxes as an experimental local isolation layer for autonomous coding agents. The section consistently emphasizes three design points:

1. Agents need Docker-capable execution, not just shell access.
2. That execution should not share the host Docker daemon or host kernel.
3. Network and credential controls should stay outside the guest environment when possible.

The mirrored subset is intentionally selective rather than exhaustive. It captures the pages needed to understand the product's threat model, operator workflow, supported agents, and control surface without ingesting the entire subsection.
