---
source-id: testing-quadrants-shapes-shift-left
trove: testing-practices-beyond-unit
type: foundational-bliki
title: "Testing Quadrants, Trophy, Shapes, and Shift-Left: Holistic Test Frameworks"
author: "Brian Marick; Lisa Crispin; Janet Gregory; Kent C. Dodds; Martin Fowler; Mike Cohn; Justin Searls; Ham Vocke"
fetched: 2026-04-20
freshness-ttl: 365
url: "https://martinfowler.com/testing/"
tags: [test-pyramid, test-trophy, test-quadrants, shift-left, sociable-testing, solitary-testing, agile-testing, unit-testing, integration-testing, e2e-testing]
---

# Testing Quadrants, Trophy, Shapes, and Shift-Left: Holistic Test Frameworks

## Why the Framework Matters More Than the Proportions

The testing community has spent decades arguing about the right shape: pyramid, trophy, diamond, ice cream cone. Martin Fowler's 2021 article "The Diverse and Fantastical Shapes of Testing" and his earlier "TestPyramid" bliki make a more important point: the shape matters less than having a deliberate strategy. Justin Searls puts it directly (and Fowler endorses the sentiment): focus on writing good tests, not on what proportion of tests fall in each layer.

This source covers four interconnected frameworks that have shaped how teams think about testing beyond unit tests: Brian Marick's testing quadrants, the agile testing elaboration by Crispin and Gregory, the test trophy versus test pyramid debate, and the shift-left philosophy.

## Brian Marick's Testing Quadrants

Brian Marick introduced the testing quadrants in the early 2000s as a way to categorize tests along two axes:

- **Business-facing vs. technology-facing.** Is the test checking what the business cares about (behavior, workflows, user outcomes) or what the technology team cares about (code quality, architecture, performance)?
- **Supporting the team vs. critiquing the product.** Does the test help the team build the right thing (guiding development, clarifying requirements) or check whether the thing that was built is right (finding defects, evaluating quality)?

This produces four quadrants:

| | Supporting Team | Critiquing Product |
|---|---|---|
| **Business-facing** | Q1: Unit tests, functional tests, examples | Q2: Exploratory testing, usability testing, dogfooding |
| **Technology-facing** | Q3: Integration tests, API tests, system tests | Q4: Performance tests, security tests, compliance tests, observability |

The quadrants are descriptive, not prescriptive. They do not say "write more Q1 tests." They say "understand what each test is for, and make sure you have coverage across all four quadrants." A team with only Q1 tests (quick to write, easy to maintain) has no capacity to find unknown-unknowns (Q2), verify system integration (Q3), or validate non-functional properties (Q4).

Marick's key insight: tests in different quadrants serve different purposes and require different approaches. A Q1 unit test that guides development is not redundant with a Q4 performance test that critiques the product. They answer different questions.

## Crispin and Gregory's Agile Testing Elaboration

Lisa Crispin and Janet Gregory's *Agile Testing* (2009) expanded Marick's quadrants into a full methodology for agile teams. Their contributions:

1. **The testing quadrants are a conversation tool, not a rigid framework.** Teams use the quadrants to discuss what testing they are doing, what they are missing, and what they need to invest in. The quadrants are a map, not a mandate.

2. **Automate everything in Q1 and Q3.** Supporting tests (business-facing and technology-facing) should be fully automated because they run frequently and need to be fast.

3. **Q2 and Q4 require human judgment, but can be supplemented with automation.** Exploratory testing (Q2) cannot be fully automated, but session-based test management and tools like synthetic monitoring can extend their reach.

4. **The "Whole Team" approach.** Testing is not a separate phase or a separate team. Every team member is responsible for quality. Programmers write unit and integration tests. Testers design exploratory sessions and define acceptance criteria. Product owners clarify requirements through examples.

Crispin and Gregory's elaboration is significant because it moves testing from a phase (something that happens after development) to a continuous activity (something that happens throughout development). This is the intellectual foundation for shift-left.

## The Test Pyramid

Mike Cohn's *Succeeding with Agile* (2009) popularized the test pyramid: many unit tests at the bottom, fewer integration tests in the middle, and very few end-to-end tests at the top. The pyramid shape reflects three constraints:

1. **Speed.** Unit tests are fast. Integration tests are slower. End-to-end tests are slowest.
2. **Scope.** Unit tests verify small units of behavior. Integration tests verify interactions. End-to-end tests verify complete workflows.
3. **Fragility.** Unit tests are stable. Integration tests break when interfaces change. End-to-end tests break when anything changes.

The pyramid's prescription: write lots of unit tests, some integration tests, and very few end-to-end tests. This maximizes coverage and speed while minimizing maintenance cost.

Ham Vocke's "Practical Test Pyramid" article on martin fowler.com (2019) gives specific implementation guidance: unit tests should be fast and deterministic, integration tests should use real dependencies (not mocks) where feasible, and end-to-end tests should be limited to critical paths.

## The Test Trophy

Kent C. Dodds introduced the "Testing Trophy" in 2019 as an alternative to the pyramid. The trophy has a large middle section (integration tests), a smaller base (unit tests), and a small top (end-to-end tests). The trophy argues that:

1. **Integration tests provide the best return on investment.** They test real behavior without the brittleness of end-to-end tests or the isolation of unit tests.
2. **Unit tests are necessary but not sufficient.** They catch regressions in small units but miss integration failures.
3. **End-to-end tests are expensive and fragile.** Use them sparingly for critical paths only.

The trophy sparked debate because it challenges the pyramid's assumption that unit tests should dominate. Dodds' point is pragmatic: in web applications, integration tests that render components with real dependencies catch more meaningful bugs per unit of effort.

## Fowler's 2021 Synthesis: Sociable vs. Solitary

Martin Fowler's 2021 article "The Diverse and Fantastical Shapes of Testing" reframes the debate. Instead of arguing about shapes (pyramid vs. trophy vs. diamond), Fowler identifies a more fundamental axis: **sociable vs. solitary tests**.

- **Solitary tests** test a unit in isolation, using test doubles (mocks, stubs) for all dependencies. They are fast, deterministic, and narrow in scope.
- **Sociable tests** test a unit with its real dependencies. They are slower, less deterministic, but broader in scope. They catch integration failures that solitary tests miss.

Fowler's argument: the pyramid vs. trophy debate is moot because it confuses the testing axis with the isolation axis. A team could have a pyramid-shaped collection of sociable tests, or a trophy-shaped collection of solitary tests. What matters is:

1. **Have a deliberate strategy.** Know why you are writing each test and what question it answers.
2. **Prefer sociable tests when feasible.** Sociable tests catch integration failures, reduce mock maintenance, and align more closely with real behavior.
3. **Use solitary tests for edge cases and complex logic.** When a unit has complex branching logic or rare edge cases, solitary tests with carefully constructed inputs are more effective than sociable tests.
4. **Don't agonize over proportions.** Focus on writing good tests that answer real questions about your system.

Justin Searls' endorsement (which Fowler highlights): focus on writing good tests, not on what percentage of tests fall in each category. A test suite with 70% unit tests and 30% integration tests that are all high-quality is better than a test suite with the "correct" proportions that includes bad tests.

## Shift-Left Testing

Shift-left testing is the philosophy of moving testing earlier in the software development lifecycle. Instead of testing after development is complete (shift-right), shift-left advocates:

1. **Write tests before code (TDD).** Tests define the specification. Code is written to pass them.
2. **Include testers in requirements discussions.** Testers help clarify acceptance criteria before development starts.
3. **Automate testing in CI.** Every commit runs the test suite. Failures are caught immediately.
4. **Use static analysis.** Linting, type checking, and security scanning run before tests and catch issues earlier.

Shift-left is complementary to the quadrants, pyramid, trophy, and shapes frameworks. It says: whatever tests you write, write them earlier. The quadrant framework says: make sure you have tests across all four quadrants. The pyramid, trophy, and shapes frameworks say: think about what proportions make sense for your context. Shift-left says: wherever you place your tests, move them left.

The synthesis: have coverage across all quadrants, use a proportion strategy that fits your context (pyramid, trophy, or something else), prefer sociable tests when feasible, and shift all testing as far left as possible.

## Relationship to Other Practices in This Trove

- **Dogfooding** (see companion source) lives in Q2 (business-facing, critiquing product). Internal users exercising the product is exploratory testing with a specific audience.
- **Observability-driven testing** (see companion source) lives in Q3 and Q4. Synthetic monitoring is technology-facing, supporting (Q3) when it verifies known paths, and technology-facing, critiquing (Q4) when it measures system properties like latency.
- **Compliance testing** (see companion source) lives in Q4 (technology-facing, critiquing product). It checks whether the implementation conforms to declared policies.
- **Swain's verification landscape** (see companion source) spans all four quadrants. Integration tests (Q3), BDD acceptance tests (Q1), ADR compliance checks (Q4), and smoke tests with agent judgment (Q2) each occupy a quadrant.

## Practical Takeaways

1. **Map your test suite to the quadrants.** If you have no tests in one quadrant, you have a gap. No Q2 tests means no exploratory or usability testing. No Q4 tests means no performance or compliance testing.
2. **Prefer sociable over solitary tests unless you have a reason not to.** Sociable tests catch integration failures. Use solitary tests for complex logic and edge cases, not as the default.
3. **Do not argue about shapes.** The pyramid, trophy, and diamond are visualizations of trade-offs: speed vs. scope vs. fragility. Pick a strategy that fits your context and change it when your context changes.
4. **Shift left, but do not abandon the right.** Production observability, dogfooding, and compliance testing are shift-right practices that catch what shift-left misses. A complete testing strategy spans the entire lifecycle.
5. **Write good tests, not correct proportions.** A well-written integration test is more valuable than a poorly written unit test. Quality over quantity, always.