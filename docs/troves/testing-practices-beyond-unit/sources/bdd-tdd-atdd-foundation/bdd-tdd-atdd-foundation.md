---
source-id: bdd-tdd-atdd-foundation
trove: testing-practices-beyond-unit
type: methodology-definition
title: "BDD, TDD, and ATDD: Foundation and Distinctions"
author: "Dan North, Kent Beck, Martin Fowler, Liz Keogh"
fetched: 2026-04-20
freshness-ttl: 365
url: "https://dannorth.net/introducing-bdd/"
tags: [bdd, tdd, atdd, chicago-school, london-school, mocks, stubs, given-when-then, three-amigos, cucumber, specflow]
---

# BDD, TDD, and ATDD: Foundation and Distinctions

## Test-Driven Development (TDD)

Kent Beck formalized TDD in *Test-Driven Development By Example* (2002), distilling a practice he had used on Smalltalk projects into a repeatable cycle: **Red-Green-Refactor**. Write a failing test, write the simplest code that makes it pass, then improve the design without changing behavior. The discipline is deceptively simple but profoundly consequential: it forces specification before implementation, guarantees a regression safety net, and produces designs that are testable by construction.

TDD operates at two levels. At the unit level, it drives the design of individual objects and methods. At a higher level — sometimes called "acceptance TDD" — it drives the design of entire features by writing a failing acceptance test first and growing the system to satisfy it. The cycle time is the critical variable. Beck recommends tests that run in milliseconds; a test suite that takes minutes changes behavior entirely, because developers stop running it frequently.

## The Chicago School vs. The London School

A deep split emerged in how TDD practitioners think about design and mocking, crystallized in Martin Fowler's influential essay *"Mocks Aren't Stubs"* (2004). Fowler distinguished four roles — test doubles that return canned data (stubs), verify interaction (mocks), provide empty implementations (dummies), and spy on real objects (spies) — but the real insight was philosophical.

The **Chicago school** (sometimes called the "classical" or "Detroit" school) grows design from the state of objects. Practitioners write tests against real collaborators whenever possible, using fakes or in-memory implementations when external dependencies are involved. The emphasis is on outcome: does the object return the right state? Refactoring is safe because tests don't bind to implementation details, but the cost is that tests tend to be broader in scope and slower to run.

The **London school** (or "mockist" school) grows design from the interactions between objects. Practitioners mock every collaborator outside the object under test, specifying which messages it should send and to whom. The emphasis is on behavior: does the object talk to its neighbors correctly? This yields highly specified designs and fast, isolated tests, but it binds tests tightly to implementation structure. Refactoring a mockist test suite often requires changing the tests themselves, because the tests encode the very wiring they are supposed to verify.

Neither school is universally right. Fowler's own position is pragmatic: use the style that fits the problem. State-based testing works well for simple return-value logic; interaction-based testing works well for orchestration and side effects. Most real codebases end up somewhere in between.

## Behavior-Driven Development (BDD)

Dan North introduced BDD in *"Introducing BDD"* (2006) as an evolution of TDD that addresses two recurring failures: developers not knowing what to test first, and the vocabulary of "test" leading people to think about verification rather than specification. North's insight was to rename TDD's cycle from "test" to "behavior" and to provide a structured vocabulary for specifying that behavior.

The **Given/When/Then** syntax is BDD's most recognizable artifact:

- **Given** some precondition (the world as it is).
- **When** an action occurs.
- **Then** an outcome should result.

This structure is not merely cosmetic. It forces the writer to separate context, action, and assertion — a discipline that produces clearer specifications and catches ambiguous requirements early. The phrasing deliberately mirrors natural language so that non-technical stakeholders can read and validate the scenarios.

BDD extends TDD in a second important direction: it operates at the **feature level**, not just the unit level. Where TDD asks "what should this method do?", BDD asks "what should this feature do for the user?" This shift in granularity connects testing to business value and makes it possible to have conversations with product owners, analysts, and testers in a shared language.

Cucumber popularized Given/When/Then as executable specification. Scenarios written in **Gherkin** syntax (.feature files) map to step definitions — glue code that translates each Given/When/Then line into test operations. SpecFlow provides the same mechanism for the .NET ecosystem. The key risk with these frameworks is that teams treat them as "test tools" rather than "specification tools," writing scenarios that Nobody except developers can read. When the scenarios become opaque, BDD has failed at its primary purpose.

## Acceptance Test-Driven Development (ATDD)

ATDD focuses on writing **acceptance criteria** before implementation begins. Unlike BDD, which grew out of TDD, ATDD grew out of the agile testing community's effort to make acceptance testing a first-class activity in the sprint, not an afterthought at the end.

Liz Keogh clarified the relationship in *"ATDD vs BDD"* (2011): ATDD answers "are we building the right thing?" while BDD answers "are we building the thing right?" In practice the boundary is porous. Both use examples to drive conversations. Both produce automated checks. The pragmatic distinction is that ATDD tends to operate at the story level (does this story pass its acceptance criteria?) while BDD tends to operate at the scenario level (does this behavior hold under these conditions?).

## The Three Amigos

The **Three Amigos** practice formalizes the conversation that BDD and ATDD both demand. Before a story enters development, three perspectives meet: a **developer** (can we build it?), a **tester** (what could go wrong?), and a **business representative** (do we want it?). The output of that conversation is a shared set of examples — concrete instances of the feature's behavior — which then become the acceptance tests.

The Three Amigos is not a meeting format; it is a discipline. Without it, developers write scenarios that reflect what is easy to code, testers write scenarios that reflect what is easy to break, and businesspeople write scenarios that reflect what is easy to imagine. The intersection of all three perspectives produces scenarios that are valuable, implementable, and robust.

## Practical Application

1. **Start with conversation, not tooling.** The primary value of BDD/ATDD is the shared understanding produced by discussing examples. If you install Cucumber without changing how you talk about requirements, you have gained nothing.

2. **Choose your school consciously.** If your system is state-heavy (calculations, transformations, CRUD), lean Chicago. If your system is interaction-heavy (orchestration, messaging, workflows), lean London. Document the choice so the team works consistently.

3. **Keep scenarios at the feature boundary.** Scenarios that click through UI workflows or exercise internal object graphs are in the wrong place. Feature-level scenarios describe what the system does for a user; unit-level tests describe how objects collaborate internally.

4. **Use the Three Amigos as a gate.** No story enters development without Three Amigos conversation and agreed examples. This is the single highest-leverage practice in the BDD/ATDD space.

5. **Treat Given/When/Then as a thinking tool, not just a syntax.** The value is in forcing clarity about preconditions, actions, and expected outcomes. If a team finds the syntax burdensome and drops it, but retains the discipline of separating context from action from assertion, BDD has still succeeded.

## Key References

- Kent Beck, *Test-Driven Development By Example* (Addison-Wesley, 2002)
- Dan North, "Introducing BDD" (dannorth.net, 2006)
- Martin Fowler, "Mocks Aren't Stubs" (martinfowler.com, 2004)
- Liz Keogh, "ATDD vs BDD" (c2.com, 2011)
- Matt Wynne and Aslak Hellesøy, *The Cucumber Book* (Pragmatic Bookshelf, 2nd ed. 2017)
- Gerard Meszaros, *xUnit Test Patterns* (Addison-Wesley, 2007) — definitive taxonomy of test doubles