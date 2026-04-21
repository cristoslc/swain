---
source-id: specification-by-example
trove: testing-practices-beyond-unit
type: methodology-definition
title: "Specification by Example: Deriving Living Documentation from Shared Understanding"
author: "Gojko Adzic"
fetched: 2026-04-20
freshness-ttl: 365
url: "https://www.specificationbyexample.com/"
tags: [sbe, specification-by-example, living-documentation, bdd, atdd, double-check-principle, process-patterns]
---

# Specification by Example: Deriving Living Documentation from Shared Understanding

## The Core Idea

Gojko Adzic's *Specification by Example* (Manning, 2011) synthesizes patterns from dozens of successful teams into a single methodology: use **concrete, realistic examples** to specify, validate, and document software behavior throughout its lifecycle. The examples are not throwaway test data — they are the specification itself, and they evolve with the system.

The defining departure from traditional requirements documents is the **double-check principle**: every business rule is expressed both as a natural-language statement and as a concrete example that illustrates it. A rule like "premium customers get free shipping on orders over $50" is ambiguous until paired with an example: *Given Alice is a premium customer, when she orders a $75 item, then shipping is free*. The example does not merely illustrate the rule — it disambiguates it. Edge cases, boundary conditions, and unspoken assumptions surface only when someone must produce a concrete instance.

## The Five Process Patterns

Adzic identifies five recurring process patterns that successful teams follow. They are not sequential phases but overlapping, reinforcing habits.

### 1. Deriving Scope from Goals

Teams that succeed with SBE start from business outcomes, not feature lists. Instead of "add a refund button," they ask "what problem does a refund solve?" The answer — reducing support call volume, improving customer retention, complying with regulation — constrains what the feature must actually do. Every example is evaluated against the goal: does this example help us deliver the outcome we care about? This pattern prevents scope creep driven by plausible but irrelevant scenarios.

### 2. Specifying Collaboratively

No single role can produce good specifications. Business stakeholders know the domain but not the constraints of implementation. Developers know the constraints but not the edge cases. Testers know the edge cases but not the priorities. Collaborative specification — workshops, example-mapping sessions, Three Amigos conversations — produces examples that none of these roles would have produced alone. The conversation is the primary artifact; the written examples are its residue.

### 3. Illustrating Using Examples

Abstract rules invite misinterpretation. Concrete examples anchor understanding. The discipline is to replace every "should" with a "for instance": "The system should handle concurrent edits" becomes "When two users edit the same paragraph simultaneously, the second save receives a conflict prompt with both versions shown." The example is automatically more precise than the rule because making it concrete forces decisions about UI, ordering, error handling, and data display.

### 4. Refining the Specification

Initial examples are often too numerous, too sparse, or too implementation-bound. Refinement trims redundancy, fills gaps, and abstracts repetitive structure. A set of twenty examples that differ only in the dollar amount becomes a single parameterized scenario outline with a data table. Refinement also removes examples that test infrastructure rather than behavior — a scenario that sets up a database connection is a fixture, not a specification.

### 5. Automating Without Changing the Specification

The examples become automated tests, but the automation must not change what the examples say. Step definitions in Cucumber, fixtures in FitNesse, or page objects in a UI framework are implementation details that live below the specification layer. If automation causes you to rewrite the examples in technical jargon, you have lost the business-readable specification and gained a brittle test. The most successful teams enforce a strict separation: the specification language stays stable even as the automation layer is refactored.

## SBE, BDD, and ATDD: How They Relate

Specification by Example is the broadest of the three approaches. BDD provides a specific mechanism for SBE (the Given/When/Then syntax and tooling around Gherkin). ATDD provides a specific workflow (write acceptance tests before implementation). SBE encompasses both and adds the dimension of **living documentation** — the examples remain authoritative descriptions of system behavior long after the sprint ends.

Adzic's framing is useful: BDD is SBE with a particular notation; ATDD is SBE with a particular workflow. A team practicing SBE might use BDD's notation, or it might use FitNesse-style wiki tables, or it might use free-form markdown with code blocks. The notation matters less than the discipline of deriving specification from concrete examples and keeping those examples in sync with the system.

Living documentation is the long-term payoff. Traditional documentation rots because nobody maintains it after the feature ships. SBE documentation stays alive because it is the test suite: if the documentation drifts from the system, the tests fail, and someone must reconcile them. This creates an economic incentive to keep the documentation accurate that no amount of "please update the wiki" ever achieves.

## The Double-Check Principle in Depth

The double-check principle operates at two levels. At the **rule level**, it pairs every business rule with at least one example that demonstrates the rule holds. At the **example level**, it requires that each example maps back to a business rule — examples that exist without a governing rule are noise. This bidirectional check catches two failure modes: rules that cannot be instantiated (signaling incomplete thinking) and examples that do not generalize (signaling overfitting to a specific case).

Teams that skip the double-check tend to produce either vague specifications (rules without examples) or test suites that check specific data points without verifying the underlying logic (examples without rules). Both are expensive: the first leads to implementation that passes tests but misses intent; the second leads to brittle tests that break on legitimate data variation.

## Practical Application

1. **Run a specification workshop before every story.** Gather developer, tester, and business stakeholder. Produce examples on a whiteboard or sticky notes. Type them up as the story's acceptance criteria. Time-box to 30-45 minutes.

2. **Name examples by business intent, not by test data.** "Premium customer free shipping" is a good example name. "Alice-order-75" is not. The name should communicate what the example proves, not what data it uses.

3. **Parameterize aggressively.** When multiple examples illustrate the same rule with different data, collapse them into a scenario outline with a data table. This reduces maintenance burden and makes the rule's parameter space visible.

4. **Automate through a stable interface.** If your specification says "the user sees a confirmation message," automate through a presenter or view model, not through DOM element IDs. The interface between specification and system should change less often than the system's internals.

5. **Treat failing specification as a documentation bug, not just a test bug.** When a specification test fails, the question is not "how do we fix the test?" but "has the system changed, and should the specification change with it?" This distinction keeps living documentation alive.

6. **Review living documentation quarterly.** Even with automated checks, some examples drift into irrelevance as the product evolves. A quarterly review removes cruft and identifies areas where the documentation has thinned and needs fresh examples.

## Key References

- Gojko Adzic, *Specification by Example* (Manning, 2011)
- Gojko Adzic, *Bridging the Communication Gap* (Neuri, 2009) — predecessor work on the communication problem SBE addresses
- Gojko Adzic, "Specification by Example" website (specificationbyexample.com)
- Ward Cunningham, Fit framework (fit.c2.com) — original executable-specification tool
- Lisa Crispin and Janet Gregory, *Agile Testing* (Addison-Wesley, 2009) — ATDD practices that overlap with SBE