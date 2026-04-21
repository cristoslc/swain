---
source-id: dogfooding
trove: testing-practices-beyond-unit
type: methodology-definition
title: "Dogfooding: Eating Your Own Cooking as a Testing Practice"
author: "Pete Hodgson; IMVU Engineering; Kent Beck; Microsoft"
fetched: 2026-04-20
freshness-ttl: 365
url: "https://martinfowler.com/articles/feature-toggles.html"
tags: [dogfooding, continuous-deployment, internal-canary, acceptance-testing, xp, imvu, microsoft, champagne-brunch]
---

# Dogfooding: Eating Your Own Cooking as a Testing Practice

## Origin and Definition

"Dogfooding" — short for "eating your own dog food" — means using the product you build before anyone else does. The term originated at Microsoft in the 1980s, where employees were expected to run internal builds of Windows and Office before shipping them to customers. The idea is simple: if you would not use it, why should anyone else?

As a testing practice, dogfooding goes beyond curiosity. It is a structural quality gate. Internal users discover integration failures, missing error handling, and confusing workflows that unit tests and staged environments miss, because they exercise real workflows on real builds under real conditions.

## IMVU's Continuous Deployment Model

IMVU's engineering blog documented one of the most aggressive dogfooding regimes in software history. Every engineer deployed to production multiple times per day. The deployment pipeline ran a comprehensive test suite first, then pushed the build to all internal employees before promoting it to external users.

This "internal canary" model worked because employees ran the same client and server stack that customers used. When a deploy broke something — a broken rendering path, a misconfigured API, a regression in avatar loading — an employee hit it within minutes, not days. The feedback loop between "deploy" and "discovery" compressed from hours to seconds.

Key elements of IMVU's approach:

- **All employees on the latest build.** No one ran a stale version. The canary population was 100% of the company.
- **Automated rollback.** If monitoring detected errors above baseline, the system reverted automatically. Dogfooding did not require a human to notice and act.
- **Feature toggles as safety nets.** Pete Hodgson's feature-toggles article on martinfowler.com describes how IMVU used toggles to ship code in a disabled state, enable it for internal users first, then ramp to production. This is the "Champagne Brunch" pattern: employees get the feature first, celebrate if it works, and roll back if it does not, all behind a toggle.

## Feature Toggles and Dogfooding

Pete Hodgson's "Feature Toggles" article on Martin Fowler's site (2017) details how toggles enable progressive delivery that starts with dogfooding:

1. **Release toggles** hide unfinished features from external users while internal users exercise them.
2. **Ops toggles** let engineers turn features off in production when dogfooding reveals problems.
3. **Experiment toggles** A/B test a feature with internal groups before external rollout.

The toggle pattern makes dogfooding safe. You can deploy incomplete, unstable code to production if it is invisible to external users. Internal users see it, use it, and break it before customers ever encounter a defect. This collapses the feedback loop between development and discovery.

## Kent Beck and On-Site Customers as Formalized Dogfooding

Kent Beck's Extreme Programming (XP) includes an explicit dogfooding practice: the on-site customer. In XP, a real user of the system sits with the development team full-time, writing acceptance tests, prioritizing stories, and providing immediate feedback on every iteration's output.

This is dogfooding formalized as a role. The on-site customer is not a proxy, a product manager interpreting surveys, or a UX researcher running monthly sessions. They are a user who runs the software in their actual work, every day, in the same room as the people building it. Defects surface in minutes. Misunderstood requirements surface before code is written.

Beck's insight was structural: dogfooding works best when the feedback path is short and the user has authority. An on-site customer who can reject a story has real power. A beta tester who files a ticket in a backlog that no one reads does not.

## Variants and Scale

**Champagne Brunch** is the IMVU variant: deploy to internal users first, then promote. Named for the celebration when internal deploy succeeds. It requires feature toggles and automated rollback.

**Internal canary** is the broader pattern: a subset of users (employees, beta testers, a named cohort) receives the build before everyone else. The canary group exercises the system under real conditions and generates alerts if something breaks.

**Shadow mode** runs new code alongside old code, compares outputs, and discards the new results. This is dogfooding without user-visible risk. It is useful for data pipeline changes, recommendation algorithm swaps, and other scenarios where the output is a computed result rather than a UI.

**Battle testing** is the military-adjacent variant: give the system to a hostile internal team whose job is to break it. Red teams, chaos engineering teams, and dedicated QA teams that act as adversarial users all fall here. This is dogfooding with intent to destroy rather than intent to use.

## Relationship to Other Practices

Dogfooding overlaps with but differs from several related testing practices:

- **Observability-driven testing** (see companion source) uses production telemetry to drive test selection. Dogfooding generates the signal that observability consumes. Without internal users generating real traffic, there is less telemetry to learn from.
- **Shift-left testing** (see companion source) moves testing earlier in the pipeline. Dogfooding moves it later — into production — but restricts the audience. They are complementary: shift-left catches what you can predict; dogfooding catches what you cannot.
- **Compliance testing** (see companion source) verifies policies. Dogfooding does not verify policies unless the internal users are trained to check, but it does verify that policies are usable. A policy that employees cannot follow is a policy that customers will not follow either.
- **Testing quadrants** (see companion source) place dogfooding in Q2 (business-facing, supporting team) and Q1 (technology-facing, supporting team). Internal users doing real work are business-facing supporting tests. Internal users generating load and errors are technology-facing supporting tests.

## Practical Takeaways

1. **Make the canary population as large as possible.** Every employee on every device on the latest build is the gold standard. Smaller canary groups work but reduce surface area and slow discovery.
2. **Automate rollback.** Dogfooding without automated rollback means a broken deploy stays broken until a human notices. IMVU's model worked because monitoring and rollback were faster than manual intervention.
3. **Use feature toggles to control blast radius.** Ship early, hide from external users, enable for internal users. This makes dogfooding continuous rather than episodic.
4. **Give internal users authority, not just access.** An employee who can file a bug is less effective than an employee who can reject a release or disable a feature. Authority compresses the feedback loop.
5. **Track what dogfooding catches that other tests do not.** If every defect found by dogfooding was also caught by an integration test, the dogfooding is redundant. If dogfooding catches defects that no automated test catches, that is signal about gaps in the test suite — signal that should drive new test creation, not just new bug fixes.