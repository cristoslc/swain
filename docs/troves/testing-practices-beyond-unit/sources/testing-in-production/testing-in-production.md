---
source-id: testing-in-production
trove: testing-practices-beyond-unit
type: methodology-definition
title: "Testing in Production: Feature Flags, Dark Launching, Shadow Traffic, and the MTTR Shift"
author: "Rouan Wilsenach; Charity Majors; Pete Hodgson"
fetched: 2026-04-20
freshness-ttl: 365
url: "https://martinfowler.com/articles/qa-in-production.html"
tags: [testing-in-production, feature-flags, dark-launching, shadow-traffic, synthetic-monitoring, MTTR, observability, IMVU]
---

## Overview

Testing in production is the practice of validating software behavior under real conditions, with real users, real data, and real infrastructure. It acknowledges a fundamental truth: no pre-production environment can fully replicate production, so some testing must happen where the software actually runs. This is not an abandonment of pre-production testing—it's a recognition that pre-production testing is necessary but insufficient.

The shift from "test before deploy" to "test after deploy" is also a shift in risk philosophy. Traditional approaches optimize for Mean Time Between Failures (MTBF)—preventing failures from reaching production. Modern approaches optimize for Mean Time To Recovery (MTTR)—detecting and recovering from failures quickly. Charity Majors articulated this shift clearly: "Testing in production doesn't mean testing your code in production. It means testing production." The distinction is critical: you're not using production as a test environment; you're instrumenting production to verify that it behaves as expected.

## Feature Flags (Feature Toggles)

Pete Hodgson's "Feature Toggles" article on martinfowler.com (2017) provides the canonical taxonomy. Feature flags are branching logic that allows code to behave differently for different users or contexts. Hodgson classifies them into several categories:

### Release flags

Release flags enable incomplete or unready features to be deployed to production without being visible to users. This allows trunk-based development with continuous deployment: code ships to production immediately, but new features are hidden behind flags. When the feature is ready, the flag is enabled—first for internal users, then for a small percentage of external users, then for everyone.

### Ops flags

Ops flags provide operational control: enabling or disabling features in response to production conditions. If a new feature is causing performance problems, an ops flag can turn it off instantly without a rollback. This is the MTTR philosophy in action: fast recovery matters more than failure prevention.

### Experiment flags

Experiment flags (A/B tests) route different users to different feature variants and measure outcomes. They're a form of production testing: instead of guessing which design is better, you test both variants with real users and measure the result.

### Permission flags

Permission flags control access based on user entitlements. Premium features, beta access, and admin functionality are gated by permission flags.

### Testing implications

Feature flags create testing complexity. Every flag combination is a potential codepath, and testing all combinations is combinatorially explosive. Hodgson recommends:

- Keep flags short-lived. A release flag should live for days to weeks, not months.
- Test the flag-off and flag-on paths separately.
- Use canary releases to validate new flag states under real conditions before broad rollout.

## Dark Launching

**Dark launching** deploys new functionality to production but routes only synthetic or internal traffic through it, keeping it invisible to real users. The goal is to validate functional correctness and performance under production conditions before exposing the feature.

Key patterns:

- **Shadow reads**: A production request hits both the old and new code paths. The response from the old path is returned to the user; the new path's response is logged but discarded. Failures in the new path are observed without affecting users.
- **Shadow writes**: Write operations are duplicated. The original write goes to the primary data store; the shadow write goes to a new data store. The results are compared for consistency.
- **Internal rings**: New features are enabled for internal users first (employees, dogfooders). They get real traffic but from a controlled population that tolerates bugs.

IMVU's **cluster immune system** is a landmark example. IMVU deployed continuously (dozens of times per day) and used feature flags and monitoring to detect regressions in production. When a deploy caused a metrics anomaly, the system automatically rolled back to the previous version. This turned production into a testing environment where the immune system, not human testers, detected failures.

## Shadow Traffic

**Shadow traffic** (also called **mirrored traffic**) copies a percentage of real production traffic to a separate environment or service instance. The shadowed traffic exercises the new code under realistic load without affecting real users.

Shadow traffic is especially valuable for:

- **Performance validation**: Route 10% of production traffic to the new service. Compare latency, error rate, and resource utilization against the existing service. This reveals performance problems that synthetic benchmarks miss because synthetic traffic rarely matches real traffic patterns.
- **Data migration testing**: Route reads to both old and new data stores. Compare results to verify migration correctness.
- **Algorithm validation**: Route traffic to both the old and new recommendation algorithms. Compare outcomes offline to validate that the new algorithm performs better.

The key technical challenge is ensuring shadow traffic doesn't affect production. Shadowed requests must be fire-and-forget: the production response must not wait for the shadow response, and shadow failures must not propagate to callers.

## Synthetic Monitoring

**Synthetic monitoring** (also called **synthetic testing** or **canary testing** in the infrastructure sense) runs scripted transactions against production systems at regular intervals. These are not unit tests running against production—they are isolated, controlled requests that verify end-to-end behavior.

Synthetic monitoring detects:

- **Availability**: Can users reach the system? Are endpoints responding?
- **Functional correctness**: Does the checkout flow complete? Does the search return results?
- **Performance**: Is response time within SLA?
- **Data integrity**: Are product prices correct? Are user accounts complete?

Unlike real-user monitoring (RUM), synthetic monitoring provides consistent baselines because it runs the same transactions repeatedly. This makes it sensitive to regressions: if a synthetic transaction suddenly takes twice as long, something changed.

## The MTBF-to-MTTR Shift

The philosophical core of testing in production is the shift from maximizing MTBF to minimizing MTTR:

- **MTBF mindset**: Prevent failures from reaching production. Invest heavily in pre-production testing, staging environments, and release gates. The goal is zero production failures.
- **MTTR mindset**: Accept that production failures will occur. Invest in fast detection (observability, synthetic monitoring, alerting), fast recovery (feature flags, automatic rollback, circuit breakers), and fast learning (postmortems, failure analysis). The goal is fast recovery from inevitable failures.

This shift doesn't abandon pre-production testing—unit, integration, and acceptance tests remain essential. It adds production validation as a complementary layer. Pre-production testing catches known problems; production testing catches unknown problems.

## Relationship to Other Testing Practices

Testing in production connects to **resilience testing** directly: resilience patterns (circuit breakers, bulkheads) are validated in pre-production and then continuously validated in production via synthetic monitoring and real traffic observation. The circuit breaker is tested in isolation (resilience testing) and then monitored in production (testing in production).

Testing in production relates to **architecture fitness functions** through continuous verification. A fitness function that checks deployment independence is a production test—it verifies that one service can be deployed without affecting others, under real conditions.

Testing in production is the production counterpart to **exploratory testing**'s investigative philosophy. Exploratory testing discovers unknown issues in a controlled environment; testing in production discovers unknown issues in the real environment. Both accept that scripted tests can't anticipate everything.

## Practical Application

- **Instrument before you test.** Testing in production depends on observability. You can't validate production behavior if you can't see it. Invest in structured logging, distributed tracing, and metric instrumentation before adding production testing techniques.
- **Start with dark launching.** It's the lowest-risk production testing technique. Deploy new features behind feature flags, exercise them with internal traffic, and verify behavior before exposing them to users.
- **Add synthetic monitoring for critical paths.** Identify the three to five most critical user journeys. Write synthetic transactions that exercise them end-to-end. Run them every few minutes and alert on deviations.
- **Budget for shadow traffic.** Shadow traffic doubles infrastructure costs for the shadowed percentage. Start with 1–5% and increase as confidence grows. Make the percentage configurable via feature flag.
- **Automate rollback.** The MTTR shift requires fast recovery. Feature flags, blue-green deployments, and canary releases all enable fast rollback—but only if the rollback is automated. IMVU's cluster immune system rolled back automatically; manual rollback is too slow for MTTR optimization.
- **Celebrate production findings.** When a dark launch or shadow traffic test reveals a bug, that's a success—the system worked as designed. Resist the cultural impulse to treat production-discovered bugs as failures. The failure would be not discovering them.