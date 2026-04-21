---
source-id: smoke-testing
trove: testing-practices-beyond-unit
type: foundational-bliki
title: "Smoke Testing / Build Verification Testing: The Deployment Gate"
author: "Martin Fowler, Jez Humble, Dave Farley"
fetched: 2026-04-20
freshness-ttl: 365
url: "https://martinfowler.com/bliki/ThresholdTest.html"
tags: [smoke-testing, bvt, deployment-pipeline, threshold-testing, continuous-delivery, production-gate]
---

## Origin and Metaphor

The term "smoke testing" comes from hardware and plumbing: plug the device in, turn it on, and if smoke comes out, you know it's broken before running any detailed diagnostics. The software equivalent is the same idea applied to builds — run the application's most basic functions first, and if those fail, nothing else matters. Stop immediately. Don't waste CI minutes on deeper tests when the fundamentals are on fire.

This practice is also called Build Verification Testing (BVT), particularly in enterprise contexts where the hardware metaphor feels less natural. Both names describe the same thing: a small, fast, broad-but-shallow suite that answers one question — *is this build worth testing further?*

## What Smoke Tests Cover

Smoke tests are intentionally broad in scope but shallow in depth. They exercise the critical path through every major subsystem — can the app start? Can a user log in? Can they reach the main screen? Does the API respond to a health check? They do not verify edge cases, boundary conditions, or complex business logic. That is the job of deeper test tiers.

A good smoke suite has these properties:

- **Fast.** Minutes, not hours. If smoke tests take 30 minutes, teams will skip them or route around them.
- **Deterministic.** A flaky smoke test is worse than no smoke test, because it erodes trust in the entire pipeline. Every test in the suite must pass reliably on every run or it gets quarantined and fixed immediately.
- **Broad.** Touch every major component at least once. If the database is down, the cache is misconfigured, or a critical dependency is missing, the smoke suite should catch it.
- **Shallow.** Each test validates the happy path only. A login test checks that valid credentials succeed — not that invalid ones fail, not that password reset works, not that session expiry behaves correctly.

Martin Fowler calls these **Threshold Tests** — the gate you must pass before the pipeline invests in more expensive verification. His bliki entry on the topic emphasizes that threshold tests are a pipeline concern, not a coverage concern. Their value is measured in time saved, not in percentage of code exercised.

## Smoke Tests in the Deployment Pipeline

In the Continuous Delivery model described by Humble and Farley, the deployment pipeline is a progression of stages, each adding confidence before the next. Smoke tests sit at the entrance of every stage where costs increase significantly:

1. **Commit stage.** Unit tests run on every commit. Smoke tests validate the assembled artifact — does the deployment package actually start?
2. **Acceptance stage.** Integration and functional tests are expensive. Smoke tests gate them. If the app can't boot, don't bother spinning up the test environment.
3. **Production deployment.** After deployment, smoke tests confirm the new version is serving traffic correctly before routing users to it. This is the basis of canary and blue-green strategies — you don't promote a canary that fails its smoke check.

This gating function is why smoke tests must be fast and deterministic. They are the tollgate on the deployment highway. A slow or flaky tollgate causes traffic jams — manual overrides, skipped stages, and eventually the pipeline loses authority and teams revert to manual deployment.

## Threshold Tests vs. Other Shallow Test Types

Fowler's Threshold Test concept overlaps with smoke testing but emphasizes a specific role: the test suite that decides whether to proceed at a pipeline stage boundary. Not all smoke tests are threshold tests, and not all threshold tests are smoke tests, but in practice they usually converge. The key insight from Fowler is that the *purpose* of the test — gating a stage transition — should drive the selection of which tests to include, rather than a categorical label like "integration" or "end-to-end."

This is a useful distinction because teams often conflate scope with depth. An end-to-end test that validates a complete user journey is not a threshold test if it takes 20 minutes to run, even though it's broad. Threshold tests sacrifice depth for speed, on purpose.

## Connection to swain-test Phase 1

The swain-test skill organizes its verification phases as a progressive pipeline:

- **Phase 1: Integration gate.** Deterministic detection of whether integration tests exist, whether they pass, and whether basic application functionality works upon deployment. This is a threshold test — it checks that the system under test is alive and responding before investing in deeper verification.
- **Phase 2: Smoke instructions.** Manual or semi-automated checks for basic functionality that cannot be trivially automated. These are the human-in-the-loop equivalent of threshold tests for aspects that defy easy automation.

Phase 1 directly inherits the smoke testing philosophy: fast, deterministic, broad, shallow. The goal is to fail fast and fail loud. If the app can't start or the primary endpoint returns 500s, the pipeline should stop before burning compute cycles on deeper test stages.

## Practical Guidance

- **Quarantine flaky tests immediately.** A smoke suite with a 95% pass rate is a smoke suite with a 0% trust rate. Quarantine failing tests into a separate suite and fix them before re-admitting them.
- **Treat smoke test failures as stop-the-line events.** A failed smoke test means the build is not deployable. No exceptions, no "it's just flaky." Investigate, fix, and re-run before proceeding.
- **Include infrastructure checks.** Database connectivity, cache reachability, external service health — these are smoke test concerns because they gate everything downstream.
- **Separate smoke from regression.** Regression tests verify that previously-broken behavior stays fixed. Smoke tests verify that fundamental functionality works right now. Mixing the two leads to suites that are too slow for pipeline gating.
- **Make results visible.** Smoke test results should be the first thing a developer sees on a pipeline dashboard. Red means don't deploy. Green means proceed to the next stage.

## Sources

- Martin Fowler, "ThresholdTest" bliki, martinfowler.com — introduces the concept of threshold tests as pipeline gates distinct from test categorization by scope.
- Wikipedia, "Smoke testing (software)" — historical origin of the term and its evolution in software contexts.
- Jez Humble and Dave Farley, *Continuous Delivery* (Addison-Wesley, 2010), Chapter 5: "The Deployment Pipeline" — the canonical treatment of pipeline stages and how smoke/BVT tests gate each transition.