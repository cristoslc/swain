---
source-id: synthetic-monitoring
trove: testing-practices-beyond-unit
type: web-article
title: "Synthetic Monitoring: Testing in Production as a First-Class Practice"
author: "Flavia Fale, Serge Gebhardt, Martin Fowler, Sam Newman, Charity Majors"
fetched: 2026-04-20
freshness-ttl: 365
url: "https://martinfowler.com/articles/synthetic-monitoring.html"
tags: [synthetic-monitoring, semantic-monitoring, production-testing, observability, mttr, continuous-delivery]
---

## What Synthetic Monitoring Is

Synthetic monitoring — also called synthetic transactions, semantic monitoring, or directed monitoring — runs automated, business-facing tests against a production system on a schedule and feeds the results into the monitoring and alerting pipeline. Instead of waiting for real users to encounter a problem, synthetic monitoring simulates user behavior on a timer, continuously verifying that critical paths work.

The key shift is ontological: synthetic monitoring is not a test that happens to run in production. It is monitoring that uses test automation as its sensing mechanism. The test is the sensor; the monitoring system is the consumer. This reframing matters because it changes what you optimize for, how you handle failures, and who owns the output.

## From Staging to Production

Traditional integration and acceptance tests run against staging or pre-production environments. Synthetic monitoring runs against production. This is not a minor difference:

- **Environment fidelity.** Staging environments drift. Synthetic testing against production eliminates the "works in staging, broken in production" problem by definition — you're testing the real thing.
- **Failure mode.** A failing staging test blocks a deployment. A failing synthetic alert pages an on-call engineer. The response is different: MTTR (mean time to recovery) thinking, not MTBF (mean time between failures) thinking.
- **Ownership.** Staging test failures are owned by the build pipeline. Synthetic monitoring failures are owned by the on-call rotation and incident response process.
- **Continuous verification.** Staging tests run on change. Synthetic monitoring runs continuously, catching issues caused by configuration drift, dependency failures, data corruption, and other changes that don't come through the deployment pipeline.

This distinction is critical. Fale and Gebhardt in their 2017 article on martinfowler.com emphasize that synthetic monitoring fills a gap that neither testing nor traditional monitoring covers: continuous verification of business-critical paths in the actual production environment, with alerting semantics.

## The ThoughtWorks Radar and "Semantic Monitoring"

ThoughtWorks introduced the concept in their Technology Radar as early as 2012, under the term "semantic monitoring." The word "semantic" is deliberate: the tests verify *meaning* — did the shopping cart checkout succeed? did the search return relevant results? — rather than *infrastructure* — is the server responding to pings? Traditional monitoring catches infrastructure problems. Synthetic monitoring catches business problems that happen to manifest through infrastructure.

The radar entry positioned semantic monitoring as a technique that "combines the best aspects of testing and monitoring" — the specificity of automated tests with the continuous, production-grade feedback of monitoring. This dual nature is what makes it powerful and also what makes it organizationally tricky: it straddles the testing and observability teams, and either side may assume the other owns it.

## Designing Effective Synthetic Tests

Not every automated test should become a synthetic monitor. Good candidates share these characteristics:

- **Business-critical paths.** Login, search, checkout, registration — paths where failure directly impacts revenue or user trust.
- **Externally visible.** The failure should be something an end user would experience, not an internal consistency check.
- **Deterministic and automated.** Synthetic monitors run unattended on schedules. Flaky or manual steps have no place here.
- **Independent.** Each synthetic transaction should be self-contained — provision its own test data, execute its path, clean up after itself. Shared state between synthetic monitors creates cascading failure modes that confuse alerting.
- **Fast enough.** Synthetic monitors that take 10 minutes per run will alert slowly. Aim for sub-minute execution.

Sam Newman in *Building Microservices* (2nd ed., 2021) dedicates a section to synthetic monitoring, emphasizing that microservice architectures make it especially valuable because the blast radius of a single service failure can be difficult to predict from infrastructure metrics alone. A health check on the payment service doesn't tell you whether end-to-end checkout works; a synthetic checkout transaction does.

## Synthetic Monitoring and Observability

Charity Majors, Liz Fong-Jones, and George Miranda in *Observability Engineering* (O'Reilly, 2022) position synthetic monitoring as complementary to — not a replacement for — observability. Observability tools excel at explaining *why* something is broken after you know it's broken. Synthetic monitoring excels at telling you *that* something is broken, often before any user reports it.

The practical integration:

1. **Synthetic alert triggers investigation.** A synthetic check fails, creating an alert.
2. **Observability tools provide diagnosis.** The on-call engineer uses traces, logs, and metrics to understand why.
3. **Both feed the same dashboard.** Synthetic results and observability telemetry should be co-located so that the alert and the diagnostic data appear together.

Majors et al. explicitly warn against treating synthetic monitoring as a replacement for good observability. A system where the only signal is "synthetic check failed" forces engineers to guess at the cause. The real power comes when synthetic alerts and observability tooling work together.

## Relationship to Integration Testing

The distinction between synthetic monitoring and integration testing is not just "production vs. staging." It reflects different failure philosophies:

- **Integration testing** optimizes for MTBF. Find bugs before they ship. Block deployments that introduce regressions. The cost of failure is deployment delay.
- **Synthetic monitoring** optimizes for MTTR. Detect problems fast when they occur. Route alerts to the right responder. The cost of failure is customer-facing downtime.

Both are necessary. Systems that only test in staging miss production-specific failures. Systems that only monitor in production let through bugs that could have been caught earlier. The mature practice uses both, with clear ownership boundaries between them.

## Practical Guidance

- **Start with the three most critical user journeys.** Don't instrument everything at once. Login, search, and checkout cover most business-critical ground.
- **Make synthetic tests first-class monitoring citizens.** Route their output to the same alerting system as your infrastructure monitoring. Don't leave them in CI dashboards where on-call engineers won't see them.
- **Separate synthetic test code from CI test code.** Synthetic monitors may need different setup, different timeouts, and different failure handling. Forcing them into the same framework as CI tests creates awkward abstractions.
- **Expect and handle flaky monitors.** Production environments are inherently non-deterministic. Build retry logic and degradation detection into your synthetic monitoring framework.
- **Track synthetic monitor coverage.** Which critical paths have synthetic coverage? Which don't? This is a production-readiness question, not a test-coverage question.

## Sources

- Flavia Fale and Serge Gebhardt, "Synthetic Monitoring," martinfowler.com (2017) — the primary article defining the practice and its relationship to testing and observability.
- ThoughtWorks Technology Radar, "Semantic Monitoring" (2012) — early identification of the practice and its strategic value.
- Sam Newman, *Building Microservices*, 2nd ed. (O'Reilly, 2021), Chapter 12: "Observability" — treatment of synthetic monitoring in microservice architectures.
- Charity Majors, Liz Fong-Jones, and George Miranda, *Observability Engineering* (O'Reilly, 2022) — positioning synthetic monitoring within a broader observability strategy.