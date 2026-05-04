---
source-id: exploratory-testing
trove: testing-practices-beyond-unit
type: methodology-definition
title: "Exploratory Testing: Disciplined Investigation Beyond Scripted Tests"
author: "Elisabeth Hendrickson; Cem Kaner; James Bach; Bret Pettichord"
fetched: 2026-04-20
freshness-ttl: 365
url: "https://www.amazon.com/dp/1937785025"
tags: [exploratory-testing, SBTM, test-charters, human-testing, context-driven, Hendrickson, Kaner, Bach]
---

## Overview

Exploratory testing is a style of testing that emphasizes the tester's freedom and responsibility to optimize the value of their work by treating test design, execution, interpretation, and learning as parallel activities rather than sequential phases. It is not random clicking, not ad hoc testing, and not the absence of methodology. It is disciplined investigation guided by heuristics, experience, and real-time learning about the system under test.

Cem Kaner, who coined the term in the context of software testing in the 1980s, defined exploratory testing as "a style of software testing that emphasizes the personal freedom and responsibility of the individual tester to optimize the quality of his or her work by treating test-related learning, test design, test execution, and test result interpretation as mutually supportive activities that run in parallel rather than as sequential phases." This definition is deliberately broad—it's a cognitive approach, not a technique.

The context-driven testing school, championed by Kaner, Bach, and Pettichord in "Lessons Learned in Software Testing" (2002), argues that testing practices must be chosen to fit the context—not dictated by orthodoxy. Exploratory testing is the natural expression of this philosophy: when you don't know what you're looking for, scripted tests won't find it.

## The Net Metaphor

Elisabeth Hendrickson's "Explore It!" (2013) introduces the **net metaphor**, which is perhaps the most accessible framing for understanding exploratory testing's relationship to automated tests:

Automated tests are a net. They catch known bugs—failures you've anticipated and written assertions for. But nets have holes. Exploratory testing finds what slips through: unanticipated states, unexpected interactions, emergent behaviors that no test author thought to check. The net doesn't catch fish that swim through its holes; you need a different kind of fishing for that.

This metaphor has practical implications. A team that invests only in automated regression tests has a net, but never examines its holes. A team that explores without automating has no net at all. The two practices are complementary: automated tests guard against regressions, exploratory tests discover unknown risks.

## Charter-Based Sessions

James Bach formalized exploratory testing into **session-based test management (SBTM)**, bringing structure and accountability to what many dismissed as unstructured. SBTM organizes exploratory testing around **charters**: short mission statements that define what to explore and what questions to answer.

A charter typically includes:

- **Target**: What area of the product to explore (e.g., "the checkout flow when payment provider is slow").
- **Resources**: What tools, data, or environments are available (e.g., "staging environment with synthetic payment gateway in latency mode").
- **Information needs**: What questions the session should answer (e.g., "Does the UI degrade gracefully? Are timeouts visible to the user? Does the order complete eventually?").

A session is timeboxed—typically 60 to 120 minutes. After the session, the tester produces a **session report** documenting what was explored, what bugs were found, what risks were identified, and what areas warrant further investigation. This report becomes the primary artifact, replacing traditional test cases as the record of what was tested.

Bach's key insight is that charters provide *just enough* structure to make exploratory testing accountable and observable without destroying its essential freedom. Too much structure turns it into scripted testing; too little makes it unobservable and unrepeatable.

## Session-Based Test Management

SBTM adds a layer of metrics on top of charter-based sessions:

- **Session duration**: Time spent in the session (charter time, bug investigation time, and setup/teardown time are tracked separately).
- **Charter coverage**: Percentage of planned charters completed, providing a progress metric analogous to test case execution rates.
- **Bug yield**: Number of bugs found per session, which helps identify high-risk areas for further exploration.
- **Debrief quality**: After each session, a debrief with a test lead or manager assesses whether the charter was well-scoped and the findings are actionable.

These metrics address the common objection that exploratory testing is unmeasurable. SBTM provides enough measurement to manage a testing effort without imposing the overhead of detailed test case documentation.

Hendrickson extends this with the concept of **test tours**: structured walkthroughs of the product organized around themes—"landmark tour" visits major features, "feature tour" exercises one feature deeply, "variable tour" varies input data systematically, and so on. Tours give testers starting points without prescribing exact steps.

## Relationship to Other Testing Practices

Exploratory testing complements **automated regression testing** directly. Automated tests stabilize known behavior; exploratory testing probes unknown behavior. The net metaphor makes this relationship clear: one fills the net, the other finds the holes.

Exploratory testing feeds into **acceptance criteria and test case design**. Findings from exploratory sessions often become new automated tests—once you've found a bug exploratively, you write a regression test to ensure it stays fixed. This is exploratory testing's most direct ROI: it discovers test cases nobody thought to write.

Exploratory testing connects to **mutation testing** in spirit. Mutation testing systematically injects faults to probe test suite effectiveness; exploratory testing probes real system behavior for unexpected states. Both are *investigative* rather than *confirmatory*.

In regulated environments (medical devices, avionics), exploratory testing is sometimes questioned because it isn't fully scripted. The SBTM framework addresses this: session reports provide traceability, charters provide auditability, and the overall approach is documented in the test strategy. The key is that *the planning is emergent, not absent*.

## Practical Application

- **Run exploratory sessions when features land.** After a feature is deployed to staging, run a 90-minute session before writing regression tests. The findings become your test cases—written *after* you know what matters.
- **Use charters to focus, not restrict.** A charter should narrow the scope enough to be coverable in one session but leave the tester free to follow leads. "Explore the search feature with special characters" is a good charter; "Verify that entering ! in search returns error message X" is a test case.
- **Debrief and share.** The value of exploratory testing compounds when findings are shared. Session reports should be lightweight—bullet points, screenshots, and bug reports—not novel-length documents.
- **Combine with automation strategically.** Use automated smoke tests to verify basic function, then explore around the edges. The automation says "it works for the happy path"; the exploration reveals what happens when things go wrong.
- **Resist the urge to script everything.** The temptation to convert every exploratory finding into a detailed test case undermines the practice's strength. Document the finding, write a targeted regression test, and keep exploring.