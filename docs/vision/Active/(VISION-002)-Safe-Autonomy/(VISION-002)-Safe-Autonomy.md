---
title: "Safe Autonomy"
artifact: VISION-002
track: standing
status: Active
product-type: personal
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
priority-weight: high
depends-on-artifacts: []
evidence-pool: ""
---

# Safe Autonomy

## Target Audience

The operator (PERSONA-001) running AI coding agents unattended on personal projects. Agents poll GitHub issues, implement fixes, research spikes, and run tests without real-time supervision. The operator reviews results, not individual actions.

## Value Proposition

The sandbox is not a restriction — it is an enabler. Without it, the operator must either supervise every agent action or accept unbounded risk. With sandboxed operation as the default execution environment, agents can run unattended against real projects with real credentials, because the sandbox guarantees a maximum blast radius.

The goal is to make sandboxed operation so seamless that running outside a sandbox feels like running without a seatbelt.

## Problem Statement

AI coding agents are gaining autonomy — from interactive pair-programming to unattended background workers. The security model hasn't kept pace. Today's agents run with the operator's full credentials, full filesystem access, and unrestricted network egress. For attended use, the operator is the safety layer. For unattended use, there is no safety layer.

The sandbox fills that gap: a containment boundary that limits what an agent can access (credentials, filesystem, network) so that a confused, hallucinating, or compromised agent cannot cause damage beyond a defined blast radius.

## Existing Landscape

- **`claude --sandbox`** (Tier 1): Claude Code's built-in native sandboxing using OS-level mechanisms (Seatbelt on macOS, Landlock/Bubblewrap on Linux). Process-level isolation with near-zero overhead. Works with all auth methods. Claude-specific — other runtimes can't use it.
- **Docker Sandboxes** (Tier 2): Docker Desktop's microVM-based sandboxing (`docker sandbox run`). Hypervisor-level isolation with full kernel separation. Runtime-agnostic (supports Claude, Copilot, Codex). But the MITM credential proxy breaks OAuth/Max subscriptions (docker/desktop-feedback#198) and adds architectural constraints.
- **Apple Containers** (future): macOS 26 will introduce sub-second lightweight VMs. Potentially combines the isolation strength of Docker Sandboxes with the simplicity of native sandboxing. Not yet production-ready.

## Build vs. Buy

Tier 2 — glue-code existing solutions. The isolation mechanisms exist (Seatbelt, Landlock, Docker Sandboxes, future Apple Containers). What's missing is the orchestration layer: choosing the right sandbox type for each runtime, scoping credentials, enforcing network boundaries, and providing clear security guarantees. That orchestration is swain-box.

## Maintenance Budget

Low. The sandbox layer wraps existing platform primitives — it should not require ongoing maintenance beyond tracking upstream changes in Docker Desktop and OS sandbox APIs. If the orchestration layer grows complex, the architecture is wrong.

## Success Metrics

- Every unattended agent runs inside a sandbox — no exceptions
- An agent has access only to the credentials it needs, never the operator's full keychain
- A confused agent cannot damage anything outside its project directory
- The operator can articulate what security promises the sandbox makes and what it explicitly does not
- Swapping sandbox types (native, Docker, Apple Containers) requires changing one configuration, not rewriting the agent workflow

## Non-Goals

- Not an agent orchestrator — which agent works on what is VISION-001's domain
- Not a security scanner — secrets scanning, vulnerability detection, and static analysis stay in INITIATIVE-004
- Not a correctness guarantee — the sandbox contains blast radius, it does not judge whether the agent did the right thing
- Not a team tool — single operator with multiple agents

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | — | Created from brainstorming session; consolidates sandbox work from INITIATIVE-004 and INITIATIVE-006 |
