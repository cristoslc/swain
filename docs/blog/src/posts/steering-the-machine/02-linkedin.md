---
title: "LinkedIn Post — Specs Steer Humans. Tests Constrain Agents."
eleventyExcludeFromCollections: true
permalink: false
---

Specs are how teams stay aligned. They don't work on agents.

An agent read a documented architectural decision, wrote code that violated it, and passed every test. It worked. It was structurally wrong. Only my review caught it. This happened across every model I tested.

LLMs read everything. Their next token is still a coin flip. Reading a constraint and following it are fundamentally different operations.

Steering teams works the same way. You set intent before the work and verify compliance after. Nobody hands someone a design doc and assumes the outcome. The difference with agents is that verification can't be a code review — it has to be automated, and it has to cover more than behavior.

With behavioral tests, every model converged. Without them, every model drifted. The model didn't matter. The constraints did.

But behavioral tests only closed half the loop. Architectural boundaries — the kind we encode in ADRs and hope people internalize — still needed me.

So: what if we had more kinds of tests? Fitness functions for architecture. Boundary tests for isolation. Protocol tests for contracts. Specs set the intent. Broad-spectrum tests verify compliance. Every constraint we'd write into a doc and hope gets followed — encode it as something that fails on violation.

For more about my agentic coding journey: https://steeringthemachine.com/posts/steering-the-machine/02-specs-steer-humans-tests-constrain-agents/
