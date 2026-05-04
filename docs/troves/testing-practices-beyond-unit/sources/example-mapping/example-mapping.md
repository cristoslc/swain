---
source-id: example-mapping
trove: testing-practices-beyond-unit
type: methodology-definition
title: "Example Mapping: From Stories to Scenarios in Four Colors"
author: "Matt Wynne"
fetched: 2026-04-20
freshness-ttl: 365
url: "https://cucumber.io/blog/example-mapping/"
tags: [example-mapping, gherkin, cucumber, collaborative-specification, three-amigos, sticky-notes, bdd]
---

# Example Mapping: From Stories to Scenarios in Four Colors

## The Technique

Matt Wynne introduced example mapping in a 2016 blog post on cucumber.io as a structured facilitation technique for turning user stories into executable Gherkin scenarios. The method uses four colors of sticky notes to make the thinking visible and to expose gaps before anyone writes code. Its power is in its simplicity: a pack of sticky notes, a wall, and twenty minutes can produce better specifications than a week of asynchronous back-and-forth in a ticketing system.

## The Four Colors

The mapping uses four colors, each with a distinct role:

- **Red** — The story. One red sticky note contains the story title or summary. It anchors the session and keeps the group focused on a single piece of work. If the group drifts, the red note brings them back.

- **Blue** — Rules (acceptance criteria). Blue sticky notes capture the business rules that govern the story. Each rule describes a constraint, a piece of logic, or an acceptance criterion. Rules are abstract; they state what must be true without providing specific data. "Premium customers get free shipping on orders over $50" is a rule.

- **Green** — Examples. Green sticky notes provide concrete instances that illustrate each rule. For the shipping rule above, a green note might read: "Alice is premium, orders $75 item → shipping is $0." Every blue rule should have at least one green example. If it does not, the rule is underspecified.

- **Yellow** — Questions. Yellow sticky notes capture anything the group does not know or cannot agree on. "What happens if the order is exactly $50?" is a question. Questions are not failures; they are the most valuable output of the session. Every unresolved question represents a risk that the story is not ready for development.

## How a Session Works

1. **Place the red note** at the top of the wall or board. Read the story aloud.

2. **Identify rules.** The group discusses the story and writes each distinct rule on a blue note, placing it below the red note in a row.

3. **Illustrate each rule with examples.** For each blue note, the group produces one or more green notes with concrete data. These go below their corresponding blue note in a column.

4. **Flag questions.** Whenever the group cannot answer a question, it goes on a yellow note, placed to the side. The session does not stop for questions; it captures them and moves on.

5. **Review the map.** At the end, the group scans for blue notes without green examples (underspecified rules), green notes without blue parents (orphaned examples), and yellow notes (unresolved risks). A story is ready for development when every rule has examples and every question has an answer or an explicit deferral.

The entire session should take 20-30 minutes for a well-understood story and up to 45 minutes for a complex one. If it runs longer, the story is probably too big and should be split.

## The Bridge to Gherkin

Example mapping's primary output feeds directly into Gherkin. Each blue rule becomes a **Scenario** (or a rule in Gherkin 6's Rule keyword). Each green example becomes the Given/When/Then steps within that scenario. The mapping from sticky notes to .feature files is nearly mechanical:

```
Rule: Premium customers get free shipping on orders over $50

  Scenario: Premium customer orders above threshold
    Given Alice is a premium customer
    And she orders an item costing $75
    When she proceeds to checkout
    Then shipping is free
```

This direct translation is why example mapping works so well with BDD. The workshop produces the conversational structure; the Gherkin encodes it in executable form. There is no gap between "what we agreed on the wall" and "what the test checks."

## Why It Works Beyond Just Being Visual

**Forces concreteness.** Abstract discussions about "how the system should work" can go on indefinitely without resolving ambiguity. The green sticky note forces a decision: what specific data, what specific outcome? People discover that they had different mental models only when they must produce a concrete example.

**Makes gaps visible.** A blue note without green examples is immediately obvious on the wall. In a text document, an unwritten example is just empty space. On the wall, it is a visual absence that demands attention.

**Separates what we know from what we don't.** Yellow notes are first-class artifacts. Too many teams let unresolved questions linger in meeting notes nobody reads. Yellow sticky notes on the wall are harder to ignore and easier to triage.

**Time-boxes effectively.** The technique gives a group a clear structure and termination condition: when every rule has examples and every question is captured, the session is done. Open-ended requirements discussions have no such condition and tend to run long without producing proportionally better output.

## Relationship to Other Practices

Example mapping is a **facilitation technique** that sits inside the broader BDD and SBE methodologies. It implements the "specifying collaboratively" process pattern from Adzic's Specification by Example. It provides the concrete structure for the Three Amigos conversation. It produces the input that Gherkin scenarios need.

Without example mapping, teams often struggle to produce good Gherkin. They write verbose scenarios that mix multiple rules, or they produce scenarios that are so abstract they could apply to any feature. Example mapping constrains the output by forcing the group to start from rules and examples, not from prose.

Wynne's *The Cucumber Book* (2nd edition, 2017) positions example mapping as the essential prerequisite to writing Cucumber features. The book's advice is blunt: if you cannot map a story in a 30-minute session, the story is not ready. This is a useful heuristic — it converts a vague feeling of unreadiness into a testable condition.

## Practical Application

1. **Run example mapping as a standing appointment.** Schedule 30-minute sessions at the start of each sprint or as stories approach the top of the backlog. Consistency matters more than perfection.

2. **Keep the group small.** Three to five people is ideal. More than seven and the conversation fragments. The Three Amigos roles (developer, tester, business) are the minimum; add a designer or ops engineer only when the story demands it.

3. **Photograph the map.** Before the group disperses, photograph the sticky-note arrangement. This is the group memory. The person who transcribes the map into Gherkin uses the photo as the source of truth.

4. **Count the yellow notes.** If a session produces more yellow notes than green notes, the story needs more research before development begins. This is a quantitative readiness criterion.

5. **Use example mapping for bug analysis too.** When a bug report arrives, map the expected behavior as if it were a new story. The bug is a missing rule or a missing example. Mapping it makes the fix's scope clear.

6. **Do not skip the green notes.** The temptation for technically-minded participants is to jump from blue rules directly to implementation. Green examples are the step that catches misunderstandings. Skipping them defeats the purpose.

## Key References

- Matt Wynne, "Example Mapping" (cucumber.io/blog, 2016)
- Matt Wynne and Aslak Hellesøy, *The Cucumber Book* (Pragmatic Bookshelf, 2nd ed. 2017)
- Gojko Adzic, *Specification by Example* (Manning, 2011) — chapter on collaborative specification workshops
- Dan North, "Introducing BDD" (dannorth.net, 2006) — the conversation discipline that example mapping operationalizes