# Synthesis: Docker Sandboxes

**Trove:** docker-sandboxes  
**Sources:** 1 documentation site source (`docker-sandboxes-docs`)  
**Date:** 2026-03-17

## Key Findings

Docker Sandboxes is an experimental isolation layer for local AI coding agents. Its central design choice is to put each agent in its own microVM with a private Docker daemon so the agent can build images, run containers, and modify its environment without sharing the host Docker daemon or host kernel.

## Theme 1: MicroVM isolation is the product's core claim

The captured docs consistently position microVMs, not containers, as the security boundary that makes autonomous agents acceptable on a developer workstation.

The architecture story is explicit:

- host execution gives agents too much trust
- socket-mounted containers still expose the host daemon
- Docker-in-Docker creates complexity and weaker operational ergonomics
- microVMs preserve Docker capability while isolating Docker state

This is the single most important claim in the section because every other feature builds on it.

## Theme 2: Sandboxes are designed for agents that need real Docker power

This is not just shell isolation. The docs repeatedly assume the agent needs to:

- install packages
- execute tests
- run Compose
- build and run containers

That requirement explains both the private-daemon model and the persistent sandbox lifecycle. Docker is targeting code agents that need a genuine development environment, not read-only assistants.

## Theme 3: Operator ergonomics depend on persistent, workspace-bound environments

The get-started and architecture pages both stress that a sandbox persists until it is explicitly removed. That gives each workspace a reusable environment with:

- cached images
- installed packages
- agent configuration and history
- synchronized workspace files

The tradeoff is disk usage and explicit lifecycle management. Sandboxes are not disposable by default.

## Theme 4: Control is layered, not absolute

The docs present three separate control layers:

1. microVM isolation
2. host-side credential injection
3. host-side HTTP/HTTPS network filtering

This is a pragmatic security model rather than a formal one. The network-policy page is careful to warn that domain-based filtering is imperfect and that broad allow-rules can still leak data. The architecture page similarly treats proxy filtering as additive rather than foundational.

## Theme 5: Credentials are intentionally kept off the guest when possible

A notable design decision is proxy-mediated credential injection for supported AI providers. The docs claim the sandbox can make outbound API calls while the real credentials remain on the host.

That reduces one common failure mode of ephemeral development environments: secrets persisting inside the guest image or VM.

## Theme 6: The control surface is CLI-first and operator-oriented

The captured pages document a small but coherent CLI surface:

- `docker sandbox run`
- `docker sandbox create`
- `docker sandbox ls`
- `docker sandbox exec`
- `docker sandbox rm`
- `docker sandbox reset`
- `docker sandbox network log`
- `docker sandbox network proxy`

The model is straightforward: create a sandbox per workspace, reconnect to it when needed, and use reset or removal when state goes bad.

## Points of Agreement

- isolation should be strong enough that an autonomous agent does not share the host Docker daemon
- workspace paths should stay stable between host and guest
- sandboxes should persist long enough to be useful for real development work
- network restrictions are necessary but insufficient on their own

## Points of Disagreement

No direct contradictions appear within the captured section. The main tradeoff is architectural rather than editorial: Docker clearly prefers microVMs over container-based isolation, and the docs argue that the alternatives are acceptable only in more trusted or less autonomous workflows.

## Gaps

- The captured subset does not include the `workflows`, `templates`, or `migration` pages.
- The agent-specific pages for Codex, Gemini, Copilot, and others were not mirrored, so provider-specific auth flows are only referenced indirectly.
- The docs describe credential injection and outbound filtering, but they do not provide a deeper threat model, audit model, or formal guarantees.
- Linux support is only mentioned through the legacy-sandbox note; the current microVM path remains macOS/Windows focused in the captured material.
