---
source-id: chaos-engineering
trove: testing-practices-beyond-unit
type: methodology-definition
title: "Chaos Engineering: Disciplined Experimentation on Distributed Systems"
author: "Nora Jones, Casey Rosenthal, Netflix Tech Blog"
fetched: 2026-04-20
freshness-ttl: 365
url: "https://principlesofchaos.org"
tags: [chaos-engineering, resilience, distributed-systems, experimentation, failure-injection, simian-army]
---

## What Chaos Engineering Is

Chaos engineering is the discipline of experimenting on a system in order to build confidence in its capability to withstand turbulent conditions in production. This definition, from principlesofchaos.org, contains two critical words: *experimenting* and *discipline*. Chaos engineering is not random destruction, not prank-style outage games, and not a testing technique in the traditional sense. It is a structured experimental method for discovering systemic weaknesses before they manifest as user-facing incidents.

The core distinction from testing: tests verify known properties. Chaos experiments probe unknown properties. A test asks "does the system behave correctly under condition X?" A chaos experiment asks "what happens when we introduce condition X?" — and the answer may be surprising, because distributed systems fail in ways that no single engineer can predict from mental models alone.

## The Four Principles

Principlesofchaos.org states four principles:

1. **Define "steady state."** Before injecting failure, characterize the system's normal behavior. This is the steady-state hypothesis: a measurable, observable baseline of how the system behaves when healthy. Without it, you cannot distinguish between "the system is fine despite the failure" and "we can't tell if the system is broken."

2. **Hypothesize that the steady state will continue.** State your expectation clearly: "Injecting network latency between service A and service B will not cause the checkout flow to exceed its SLO." This hypothesis makes the experiment falsifiable.

3. **Introduce variables that reflect real-world events.** Inject failures that actually happen in production: server crashes, network partitions, DNS failures, disk exhaustion, dependency timeouts. Don't invent impossible failures; simulate plausible ones.

4. **Look for a difference in steady state.** If the system maintains its steady state despite the injection, the hypothesis holds and confidence increases. If it doesn't, you've found a weakness — and that's the valuable outcome.

These principles form a scientific method for system resilience. Not "let's break things and see what happens," but "here's what normal looks like, here's what we expect to stay normal, and here's a real-world stress we'll apply to check."

## The Netflix Simian Army

Netflix pioneered chaos engineering at scale with the Simian Army, a collection of fault-injection tools named after primates:

- **Chaos Monkey** randomly terminates production instances. It is the original and most famous member — its job is to ensure that no single instance failure causes user-visible degradation.
- **Latency Monkey** introduces artificial delays into network calls, testing how services handle slow dependencies.
- **Janitor Monkey** searches for and cleans up unused resources, testing whether the system handles resource reclamation correctly.
- **Security Monkey** looks for security vulnerabilities and configuration drift.

The Simian Army was documented in a 2011 Netflix Tech Blog post that became a watershed moment for the practice. The key insight: Netflix didn't run these tools in staging. They ran them in production, during business hours, with real user traffic. This is because staging environments don't have production's topology, traffic patterns, or failure modes. The only reliable way to learn how a production system responds to production failures is to inject production failures.

Critically, Netflix treated Chaos Monkey as an opt-out system. Services were opted in by default, and teams had to justify opting out. This inverts the typical testing model, where teams opt in to resilience testing when they remember. The default at Netflix was resilience verification.

## Blast Radius Minimization

A chaos experiment without blast radius control is just an outage with extra steps. Jones and Rosenthal in *Chaos Engineering* (O'Reilly, 2020) emphasize minimizing blast radius as a core practice:

- **Start small.** Inject failure into a single instance before injecting into a whole cluster. Test on a non-critical service before testing on a critical one. Use canary populations before fleet-wide experiments.
- **Have abort mechanisms.** Every experiment should have a clear, tested way to stop the failure injection immediately. If you can't stop it, don't start it.
- **Monitor continuously.** Watch the system's steady-state metrics throughout the experiment. If degradation exceeds your predefined threshold, abort.
- **Schedule during business hours.** Run experiments when engineers are available to respond, not at 3 AM on a Saturday.

These controls make chaos engineering safe enough to practice regularly. The goal is not to cause outages — it's to find weaknesses under controlled conditions so that uncontrolled conditions cause fewer outages.

## Chaos Engineering vs. Testing

The distinction is worth belaboring because it's widely misunderstood:

- **Tests are pass/fail.** They verify a specific property against a specific expectation. If the test passes, the property holds. If it fails, you have a bug to fix.
- **Chaos experiments are exploratory.** They probe for behavior you didn't explicitly specify. If the system maintains steady state, confidence increases. If it doesn't, you've discovered something — but it may not be a "bug" in the traditional sense. It could be a missing circuit breaker, an inadequate timeout, a cascading failure mode, or a misconfiguration.
- **Tests run before deployment.** They gate the pipeline. Chaos experiments run after deployment (often continuously) and feed into resilience engineering.

Jones and Rosenthal put it directly: "Chaos engineering is not testing. Testing is about verifying that the system does what you expect. Chaos engineering is about discovering what the system does that you don't expect."

## Tools and Platforms

- **Chaos Monkey** (Netflix) — original instance termination tool, open-sourced and still maintained.
- **Gremlin** — commercial chaos engineering platform with a free tier, offering controlled failure injection across infrastructure, network, application, and state layers.
- **Litmus** (CNCF) — Kubernetes-native chaos engineering framework with a large library of experiments and a growing community.
- **Chaos Toolkit** (ChaosIQ) — open-source toolkit with a declarative experiment format, designed to be platform-agnostic and composable.
- **AWS Fault Injection Simulator** — managed service for running chaos experiments on AWS infrastructure.

The State of Chaos Engineering Report (Gremlin, annual) tracks adoption trends. The consistent finding: organizations that practice chaos engineering regularly have fewer and shorter incidents. The causal direction is contested — mature organizations may be more likely to adopt chaos engineering, rather than chaos engineering causing maturity — but the correlation is strong.

## Practical Guidance

- **Start with Chaos Monkey.** Random instance termination is the simplest, safest, and most valuable experiment. If your service can't survive one instance dying, it can't survive a production outage.
- **Invest in observability first.** You cannot define steady state without being able to observe steady state. If you can't measure it, you can't hypothesize about it, and you can't detect divergence from it.
- **Game day exercises before automated chaos.** Run manual failure injection exercises first. Learn what breaks, how it breaks, and how the team responds. Then automate the experiments you understand.
- **Treat every incident as a chaos experiment result.** When production breaks, compare the failure mode to your chaos experiments. If you didn't experiment for that failure mode, add it to your experiment library.
- **Make chaos opt-out, not opt-in.** Services that haven't been chaos-tested are services that will break in unexpected ways. Default to inclusion.

## Sources

- principlesofchaos.org — the canonical statement of chaos engineering principles.
- Nora Jones and Casey Rosenthal, *Chaos Engineering* (O'Reilly, 2020) — book-length treatment covering principles, practices, and organizational adoption.
- Netflix Tech Blog, "The Netflix Simian Army" (2011) — the foundational description of Netflix's chaos engineering practice and tooling.
- Gremlin, "State of Chaos Engineering Report" (annual) — industry survey tracking adoption, maturity, and outcomes.