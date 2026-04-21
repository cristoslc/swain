---
source-id: property-based-testing
trove: testing-practices-beyond-unit
type: methodology-definition
title: "Property-Based Testing: Finding Invariants Beyond Examples"
author: "Koen Claessen, John Hughes, David MacIver, Scott Wlaschin"
fetched: 2026-04-20
freshness-ttl: 365
url: "https://fsharpforfunandprofit.com/posts/property-based-testing/"
tags: [property-based-testing, quickcheck, hypothesis, shrinking, invariants, generative-testing]
---

## What Property-Based Testing Is

Property-based testing (PBT) replaces manually specified test cases with automatically generated ones. Instead of writing `assert add(2, 3) == 5`, you write `for all integers a and b, add(a, b) == add(b, a)`. The testing framework generates hundreds or thousands of input values and checks whether the property holds for each one. When a counterexample is found, the framework *shrinks* it — reducing the failing input to the simplest case that still triggers the failure, making the bug easier to understand and fix.

This approach was introduced by Koen Claessen and John Hughes in QuickCheck, originally for Haskell, presented at ICFP 2000. The core insight: most test suites test the same code paths repeatedly with different data, while the interesting bugs hide in edge cases that no one thought to write down. PBT systematically explores the input space rather than relying on the tester's imagination.

## Properties vs. Examples

Example-based testing (the kind most developers write daily) verifies that the system produces specific outputs for specific inputs. Property-based testing verifies that the system satisfies general rules (properties, invariants) across a wide range of inputs. These are complementary approaches, not competing ones. Examples are good for describing expected behavior concretely. Properties are good for finding unexpected failures.

The challenge of PBT is not the tooling — it's finding good properties. As Scott Wlaschin puts it in his property-based testing series on fsharpforfunandprofit.com, "The hard part of property-based testing is coming up with properties." Most developers are trained to think in terms of examples: "given this input, I expect that output." PBT requires a different cognitive model: "given any valid input, what must always be true about the output?"

Wlaschin catalogs several patterns for finding properties:

- **Commutativity.** Operations that should produce the same result regardless of order: `add(a, b) == add(b, a)`, `sort(concat(list1, list2)) == sort(concat(list2, list1))`.
- **Idempotency.** Applying an operation twice produces the same result as applying it once: `sort(sort(list)) == sort(list)`.
- **Inverse operations.** If operation A has an inverse B, then `B(A(x)) == x`: `encode(decode(x)) == x`, `deserialize(serialize(x)) == x`.
- **Invariants.** Properties that must hold regardless of input: "the length of a sorted list equals the length of the input list," "a search result page contains no duplicates."
- **Oracle / test model.** Compare the system under test against a simpler reference implementation that is known to be correct (even if slow).
- **Round-trip properties.** Serialize then deserialize, or encode then decode, and verify the result equals the original.

These patterns give developers a starting vocabulary for expressing properties. Most real-world property-based test suites combine several of these patterns.

## Shrinking: The Debugging Superpower

When a PBT framework finds a failing input, the raw counterexample is often large and complex — a thousand-element list, a deeply nested data structure, a string with 200 characters. Shrinking is the process of reducing this counterexample to the minimal failing case.

QuickCheck introduced shrinking via a type-directed approach: each type defines how its values can be shrunk (an integer can be shrunk toward zero, a list can be shrunk by removing elements or shrinking individual entries). When a property fails, QuickCheck tries smaller and smaller values until it finds the smallest input that still triggers the failure.

Hypothesis (Python) takes a different approach, using internal tracking of which bytes in the generated input contributed to the failure. This allows Hypothesis to shrink inputs more aggressively and find simpler counterexamples than QuickCheck-style shrinking in many cases. David MacIver's "How Hypothesis Works" series describes this in detail — the framework maintains a tree of generated values and their relationships, enabling targeted shrinking that understands which parts of the input are relevant to the failure.

The practical impact is enormous. A developer who sees `property failed for input: [1, 2, 3, 4, 5]` can investigate immediately. A developer who sees `property failed for input: [847, 293, 1048, 571, 22, ...]` (500 more elements)` has a much harder time. Shrinking turns PBT from a bug-finding tool into a bug-diagnosis tool.

## Key Implementations

- **QuickCheck** (Haskell, 2000) — the original. Type-class-based shrinking, combinators for generator composition, the conceptual foundation for all subsequent PBT tools.
- **Hypothesis** (Python) — advanced shrinking via internal byte-level tracking, database of previous failing examples, integration with pytest. The de facto standard for PBT in the Python ecosystem.
- **fast-check** (JavaScript/TypeScript) — property-based testing for the JS/TS ecosystem. Model-based testing, asynchronous properties, seed-based reproduction.
- **ScalaCheck** (Scala) — QuickCheck-style PBT for the JVM, integrated with ScalaTest and sbt.
- **fscheck** (F#/.NET) — PBT for the .NET ecosystem, widely used in the F# community.

Each implementation follows the same core model: define generators, define properties, run properties against generated inputs, shrink failures. The differences are in shrinking strategies, integration with test runners, and the expressiveness of the generator combinator library.

## John Hughes and "Testing the Hard Stuff"

John Hughes's 2014 talk "Testing the Hard Stuff and Staying Sane" (EUC) is a landmark in the practical application of PBT. Hughes describes using QuickCheck to test Ericsson's AXD 301 ATM switch, a telecoms product with complex stateful behavior that was resistant to traditional testing approaches. The key findings:

- **State machine modeling.** Hughes modeled the system under test as a state machine and generated command sequences (state machine transitions) rather than simple values. This allowed QuickCheck to explore complex multi-step scenarios that no human tester would think to write.
- **Shrinking command sequences.** When a long command sequence triggered a failure, QuickCheck could shrink it to the minimal sequence that still reproduced the bug. This turned 50-step failure scenarios into 3-step minimal examples.
- **Specification-driven testing.** The properties were derived from the system's specification, not from the implementation. PBT found discrepancies between the spec and the implementation, which is exactly where the hardest bugs live.

This work demonstrated that PBT scales beyond simple functional properties to complex stateful systems — precisely the kind of systems where example-based testing struggles most.

## Practical Guidance

- **Start with round-trip properties.** They're the easiest to write and catch surprising numbers of bugs: serialize/unserialize, encode/decode, parse/format.
- **Use PBT to augment, not replace, example tests.** Keep your existing example-based tests for regression coverage. Add property-based tests for invariants and edge-case exploration.
- **Invest time in generator design.** PBT is only as good as its generators. If your generators only produce simple values, PBT won't explore the edge cases you care about. Write custom generators that produce realistic, complex inputs.
- **Don't ignore shrinking failures.** When a property fails and the framework produces a shrunk counterexample, study it carefully. The minimal case often reveals a fundamental misunderstanding about the system's behavior.
- **Tag your property-based tests separately from example tests.** Property-based tests are slower (they run many more cases) and sometimes non-deterministic (different random seeds produce different inputs). Separate them in your test runner so you can run example tests on every commit and PBT suites on CI or on a schedule.
- **The hard part is finding good properties.** Use Wlaschin's property patterns as a starting vocabulary. As you gain experience, you'll develop domain-specific property patterns that are more powerful than the generic ones.

## Sources

- Koen Claessen and John Hughes, "QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs" (ICFP 2000) — the original paper introducing property-based testing.
- David MacIver, "How Hypothesis Works" series — detailed technical explanation of Hypothesis's shrinking strategy and internal architecture.
- Scott Wlaschin, "Property-Based Testing" series, fsharpforfunandprofit.com — accessible introduction to PBT concepts and property-finding patterns.
- John Hughes, "Testing the Hard Stuff and Staying Sane" (EUC 2014) — practical application of PBT to complex stateful systems, with shrinking as a debugging technique.