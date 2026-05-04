---
source-id: integration-testing
trove: testing-practices-beyond-unit
type: methodology-definition
title: "Integration Testing: Narrow and Broad, Sociable and Solitary"
author: "Martin Fowler, Ham Vocke"
fetched: 2026-04-20
freshness-ttl: 365
url: "https://martinfowler.com/bliki/IntegrationTest.html"
tags: [integration-testing, test-pyramid, narrow-integration-test, broad-integration-test, sociable-tests, solitary-tests, contract-testing, e2e-testing]
---

# Integration Testing: Narrow and Broad, Sociable and Solitary

## The Ambiguity of "Integration Test"

The term "integration test" is among the most overloaded in software development. Some teams use it to mean any test that touches a database. Others use it to mean tests that exercise multiple services together. Others use it to mean the phase between unit testing and acceptance testing, regardless of what is being tested. Martin Fowler's *"IntegrationTest"* bliki entry directly addresses this confusion by proposing two distinct categories with different scopes, costs, and purposes.

## Narrow Integration Tests

A **narrow integration test** exercises a single component's boundary with the outside world. It tests the code that translates between your domain model and an external dependency's interface — the adapter, gateway, or client layer. It typically runs against a real external dependency (an in-memory database, a local file system, a test instance of a message broker) or a carefully constructed fake that shares the same interface as the real dependency.

The scope is deliberately limited. A narrow integration test does not exercise the full business logic of the component or the full behavior of the external dependency. It verifies that the adapter sends the right requests, handles the expected responses, and translates data correctly in both directions. Errors in business logic are caught by unit tests. Errors in the external dependency's behavior are caught by that dependency's own tests. The narrow integration test covers only the seam between them.

Narrow integration tests are fast enough to run as part of a developer's normal feedback loop. They are deterministic because they run against controlled test instances. They are cheap because they do not require shared infrastructure or coordination between teams.

## Broad Integration Tests

A **broad integration test** exercises multiple components or services working together through their real communication channels. It tests the actual integration: network calls, serialization, authentication, error handling, and idempotency across service boundaries. These tests typically run in an integration environment that simulates production topology.

Broad integration tests are slow. They require provisioning and coordinating multiple services, waiting for startup, seeding data, and managing cleanup. They are flaky because they depend on network reliability, process scheduling, and environmental consistency. They are expensive because the integration environment must be maintained and shared across teams.

Fowler's recommendation is explicit: you need very few broad integration tests. Each one has high cost and diminishing returns. The few you write should target the specific risks that narrow tests cannot cover: end-to-end request paths, serialization format compatibility, and infrastructure configuration. Everything else should be covered by cheaper, narrower tests.

## The Sociable vs. Solitary Distinction

Fowler's bliki also introduces a distinction that cuts across the unit/integration boundary:

**Solitary unit tests** test a class in isolation, with all collaborators replaced by test doubles. This is the London school's approach: mock everything external, test the object's logic alone. Solitary tests are fast and deterministic, but they bind to the object's interaction structure. Refactoring the object's collaborators requires refactoring the tests.

**Sociable unit tests** test a class together with its real collaborators. This is the Chicago school's approach: use real objects whenever possible, test the outcome of the collaboration. Sociable tests are slower (because they exercise more code) and less isolated (because a bug in a collaborator will cause the test to fail), but they are more resilient to implementation changes.

The practical insight is that the sociable/solitary distinction is **independent** of the unit/integration distinction. A sociable unit test that exercises a cluster of domain objects working together is still a unit test if it does not cross process boundaries. A narrow integration test that exercises an adapter layer with mocked business logic is still an integration test even though the adapter is "solitary" within the test.

Teams get into trouble when they confuse these axes. A "unit test" that mocks an HTTP client and injects a fake response is really a narrow integration test that happens to use the unit testing framework. Treating it as a unit test leads to false confidence: the test verifies the adapter's logic but not its integration with the real service. Treating it as a narrow integration test leads to the right follow-up: we still need to verify the contract with the real provider.

## The Test Pyramid and Integration Tests' Place

Ham Vocke's *"Practical Test Pyramid"* article (martinfowler.com, 2018) revisits Mike Cohn's original test pyramid in the context of modern microservice architectures. The pyramid's three layers are:

1. **Unit tests** (many, fast, cheap) — test individual units of logic.
2. **Integration tests** (fewer, slower, more expensive) — test the boundaries between units and services.
3. **End-to-end tests** (few, slow, expensive) — test complete user journeys through the full system.

Vocke's key update is to clarify what "integration test" means on the pyramid: it sits between unit tests and E2E tests, and it should focus on **narrow** integration concerns. Tests that spin up multiple services and exercise full workflows are E2E tests, not integration tests, regardless of what their authors call them. The pyramid's middle layer is for contract tests, adapter tests, and tests that verify a single service's integration with its infrastructure (database, message broker, cache).

## How Integration Testing Relates to Contract Testing

Consumer-driven contract tests are a specialized form of narrow integration test. They test the boundary between a consumer and a provider by verifying the contract: does the provider still deliver the responses the consumer expects? The contract test is narrower than a traditional integration test because it does not exercise the consumer's business logic or the provider's internal behavior — it tests only the API boundary.

In a well-structured test suite, contract tests replace many broad integration tests. Instead of deploying both services to a shared environment and running end-to-end flows, each service independently verifies its side of the contract. The combination of contract tests plus service-level unit tests provides equivalent assurance at lower cost.

Contract tests do not replace all integration tests. Concerns like network latency, TLS handshake correctness, and load balancer configuration are outside the contract's scope. These require broad integration tests or, increasingly, testing in production with feature flags and canary deployments.

## How Integration Testing Relates to E2E Testing

E2E tests exercise complete user journeys through the live system. They are the broadest, slowest, and most expensive tests in the portfolio. Their value is in catching integration failures that no narrower test can catch: a front-end change that breaks a form submission, an API version mismatch that only manifests under specific request ordering, or a serialization edge case that only appears with production data volumes.

The practical guideline is that E2E tests should cover a small number of **critical paths** — the journeys that directly generate revenue or serve the most users. Everything else should be covered by integration and unit tests. When E2E suites grow large, they become a maintenance burden and a source of flaky failures that erode trust in the entire test portfolio.

## Practical Application

1. **Categorize every test by scope, not by name.** A test called "integration test" that spins up three services and exercises a full user journey is an E2E test. Rename it or move it to the right layer. Correct categorization determines correct investment.

2. **Maximize narrow integration tests, minimize broad ones.** For every broad integration test, ask: could this be decomposed into a contract test on the consumer side, a contract verification on the provider side, and unit tests for the business logic on each side? If yes, replace it.

3. **Use sociable unit tests for domain logic clusters.** When domain objects collaborate to produce a result, test the cluster together. Mocking every internal collaborator produces tests that are brittle to refactoring. Sociable tests survive internal restructuring.

4. **Use solitary unit tests for coordination logic.** When an object's job is to route messages to collaborators, testing it with mocks verifies the routing logic precisely. The London school's strength is in testing orchestration.

5. **Run narrow integration tests in CI.** They are fast enough. Run broad integration tests in a separate pipeline or on a schedule, not on every commit. Run E2E tests overnight or on deployment.

6. **Track flakiness by layer.** If your integration tests are flaky, check whether they are actually broad integration tests pretending to be narrow ones. Flakiness at the narrow layer usually indicates a missing fake or a test that depends on external state. Flakiness at the broad layer is expected; manage it with retries and quarantines, not with denial.

## Key References

- Martin Fowler, "IntegrationTest" bliki (martinfowler.com)
- Ham Vocke, "Practical Test Pyramid" (martinfowler.com, 2018)
- Martin Fowler, "Microservice Testing" series (martinfowler.com)
- Mike Cohn, *Succeeding with Agile* (Addison-Wesley, 2009) — original test pyramid
- Toby Clemson, "Testing Strategies in a Microservice Architecture" (martinfowler.com) — contract testing in the pyramid context
- Gerard Meszaros, *xUnit Test Patterns* (Addison-Wesley, 2007) — sociable vs. solitary test terminology