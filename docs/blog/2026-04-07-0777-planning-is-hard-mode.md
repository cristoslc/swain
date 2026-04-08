# For Agentic Coding, Test-Driven Iteration Is the Only Game in Town

**Date:** 2026-04-07  
**Tags:** agentic-development, testing, architecture, swain



## You Can't Steer With Specs

Swain was built on a hypothesis that seemed sound: if AI agents forget what you decided between sessions, capture those decisions in artifacts. Write them down in git. Make them durable. Build a hierarchy — Vision → Initiative → Epic → Spec — so agents can read what was decided before they act.

I spent 730 commits over 14 days building this system. Sixteen skills. Ten artifact types. A dependency graph that validates downstream work against upstream decisions. A roadmap renderer with Eisenhower quadrants and Gantt charts.

And yet: agents repeatedly went off the rails despite the elaborate artifact hierarchy.

The [VISION-006 Full Session Retro](https://github.com/cristoslc/swain/blob/trunk/docs/swain-retro/2026-04-07-vision-006-full-session-retro.md) tells the story. In a single session that produced 80 integration tests and 34 commits, the architecture shifted three times:

1. **Hexagonal → plugin (operator design shift).** The initial design assumed adapters would be core contributions. Mid-implementation, the operator realized this would block community extensions. The architecture shifted to plugins before the agent wrote any code.

2. **In-process → subprocess (operator correction).** The agent implemented adapters as in-process Python classes. This violated [ADR-038: Microkernel Plugin Architecture](https://github.com/cristoslc/swain/blob/trunk/docs/adr/Active/(ADR-038)-Microkernel-Plugin-Architecture/(ADR-038)-Microkernel-Plugin-Architecture.md)'s subprocess model. It worked. It had tests. It was architecturally wrong. Only operator review caught it.

3. **tmux scraping → HTTP API (serendipitous pivot).** The agent built a tmux adapter that worked but was fragile — ANSI escape codes, output batching, FIFO race conditions. The operator asked why sessions weren't visible in `tmux ls`. Answer: `opencode run` is single-shot. The fix was `opencode serve` — a completely different architecture. The mismatch between expectation and implementation forced a better design.

The hierarchy was designed to *tell* agents what to build. But telling doesn't work. The [retro](https://github.com/cristoslc/swain/blob/trunk/docs/swain-retro/2026-04-07-vision-006-full-session-retro.md) is blunt:

> "The first half was spent debugging live... The operator said 'stop. reset. TDD from architectural plan.' After that, tests drove every change. Every pivot was validated before going live. **The live debugging wasted 60+ minutes; the TDD approach wasted zero.**"

Tests proved behavior, not architecture. The artifact graph answered "what exists?" but not "what matters?" The [Overnight Autonomous Artifact Sweep](https://github.com/cristoslc/swain/blob/trunk/docs/swain-retro/2026-03-22-overnight-autonomous-artifact-sweep.md) found **9 specs that were already implemented but stuck in Active** — the code existed, features worked, but the specs were never transitioned. Ceremony debt accumulated silently.

The pattern repeated across retros:

- **"Tested but not wired"** — [release-skill-deletion incident](https://github.com/cristoslc/swain/blob/trunk/docs/swain-retro/2026-03-28-release-skill-deletion-incident.md) (skill not invoked), [dead-code-in-release retro](https://github.com/cristoslc/swain/blob/trunk/docs/swain-retro/2026-03-31-dead-code-in-release.md) (script not wired), [changelog misclassification](https://github.com/cristoslc/swain/blob/trunk/docs/swain-retro/2026-04-01-teardown-rewrite-release.md) (development process not excluded)
- **Stale state** — `.agents/bookmarks.txt` with a single stale entry from a worktree that no longer existed, never cleaned up because no skill owned the lifecycle
- **Forward-linking is natural, back-propagation is not** — agents link new artifacts to dependencies but never update old artifacts when new evidence arrives

The [Architecture Intent-Evidence Loop trove](https://github.com/cristoslc/swain/blob/trunk/docs/troves/architecture-intent-evidence-loop/synthesis.md) names the core problem: **architecture documents capture decisions so you don't have to re-derive them from code.** But they drift. Code changes. Decisions get forgotten. Reconciliation is the check: does what we wrote down still match what we built?

But reconciliation was manual. Retro documents. Operator attention. The gap between intent (what was decided) and evidence (what exists) widened between sessions.

Here's the shift: **specs steer humans, tests constrain agents.**

Swain's artifact hierarchy started as a way to capture ideas and directions so context would be available to the agent between sessions. That work still matters. Product design, architectural thinking, capturing why decisions were made — none of that goes away. Write the spec to clarify your own thinking. Capture the product design. Document the architecture. But don't expect the spec to align the agent. Use tests for that. Specs give the agent context; tests give it guardrails.



## Test-Driven Iteration Is the Only Path That Works

[VISION-006](https://github.com/cristoslc/swain/blob/trunk/docs/swain-retro/2026-04-07-vision-006-full-session-retro.md)'s turnaround came when the operator invoked TDD after the live debugging failure. The [session retro](https://github.com/cristoslc/swain/blob/trunk/docs/swain-retro/2026-04-07-vision-006-full-session-retro.md) is explicit:

> "TDD rescued the session. The first half was spent debugging live... After that, tests drove every change. Every pivot was validated before going live."

The 80-test suite didn't prevent the architectural violations. But it gave the agent a way to self-correct. Each failing test was a constraint that forced a rewrite. The operator didn't fix the code — the operator fixed the tests, and the agent fixed the code.

**The point:** write tests alongside the spec, before the agent starts coding. Not after as a check. The tests are the steering mechanism. The spec gives context; the tests give constraints.

The first implementation (in-process classes) had tests and passed them all. It was still architecturally wrong — violated [ADR-038](https://github.com/cristoslc/swain/blob/trunk/docs/adr/Active/(ADR-038)-Microkernel-Plugin-Architecture/(ADR-038)-Microkernel-Plugin-Architecture.md)'s subprocess model. The tests checked behavior, not architecture. This is why we need fitness functions — they're the architectural test layer that TDD doesn't provide.

**This isn't model-specific.** This project has used: Opus 4.6 (frontier), Sonnet 4.6 (mid-tier), Qwen3.5:397b (mid-tier), and Gemma 4:31b (budget). Opus built the POC. Sonnet built the test suite. Gemma 4 ran the bridge. The pattern held across all of them: without tests, drift. With tests, convergence.

The [BDD Test Suite Spec](https://github.com/cristoslc/swain/blob/trunk/docs/superpowers/specs/2026-04-04-bdd-test-suite-design.md) documents the coverage: 84 tests across 8 domains (session, worktree, artifact, sync). The [Automated Test Gates Spec](https://github.com/cristoslc/swain/blob/trunk/docs/superpowers/specs/2026-03-31-automated-test-gates-design.md) makes it official: two-phase verification (integration tests → smoke tests) as a hard gate before every merge.

But these tests check **user-facing behavior** — that scripts work, that artifacts transition, that the roadmap renders. They don't test architectural constraints. They don't answer:

- "Can I write a plugin?" (extensibility test)
- "Is page load time < 500ms?" (performance test)
- "Does this skill activate on the right trigger?" (behavioral test)
- "Did you violate the subprocess boundary?" (architectural test)

The fitness functions are missing.

**This isn't a cost problem — it's a capability problem.** [VISION-006](https://github.com/cristoslc/swain/blob/trunk/docs/swain-retro/2026-04-07-vision-006-full-session-retro.md)'s POC was built with Opus, the frontier model for agentic development. It still went off the rails twice in one session. The 80-test suite caught regressions but NOT the architectural violations — operator review did that. But the test suite gave the agent a way to self-correct: each failing test forced a rewrite until the code aligned.

Behavioral specs (BDD) are one useful form — natural language that models can read and write. But the broader category is: tests for everything the artifact hierarchy was supposed to enforce and couldn't.



## What Would Swain Look Like Built from This Assumption?

If test-driven iteration is the only path that works, what changes?

We need to codify *all* forms of testing, not just TDD. Unit tests cover functions. Integration tests cover component wiring. Behavioral tests (BDD) cover user-facing behavior. Fitness functions cover architectural constraints. Performance tests cover latency and throughput. Security tests cover vulnerabilities.

Here's what VISION-006 showed: the 80-test suite caught regressions but missed the architecture violations. Tests that check behavior won't catch structural drift. You need fitness functions for that — tests that encode architectural constraints the same way unit tests encode function contracts.

### 1. Fitness Functions from Day One

The [Architecture Intent-Evidence Loop trove](https://github.com/cristoslc/swain/blob/trunk/docs/troves/architecture-intent-evidence-loop/synthesis.md) defines fitness functions as "objective measurement of some architectural characteristic." Paul and Wang extend this: **just as TDD writes tests before code, fitness function-driven development writes architectural tests before implementing features.**

What if swain's artifact hierarchy was replaced with a test suite that encodes architectural constraints?

```bash
# Instead of ADR-038 saying "use subprocess plugins"...
# A test that fails if you import from the wrong namespace
test_plugin_isolation.sh:
  - verify no direct imports between plugin and host
  - verify NDJSON protocol is only communication channel
  - verify plugin can be written in any language

# Instead of VISION-006 saying "persistent sessions"...
# A test that verifies session persistence across messages
test_session_persistence.sh:
  - send message 1, capture session ID
  - send message 2, verify same session ID
  - verify chat history is present in message 2 context
```

The test suite becomes the architecture. Not "here's a diagram" but "here's a test that fails if you violate the boundary."

### 2. Flattened Hierarchy

Swain has 10 artifact types. Most work requires creating 3-4 of them before implementation starts: Vision (why), Initiative (strategic theme), Epic (coordination), Spec (implementation).

What if the hierarchy was just **Spec + Test Suite**?

The spec declares acceptance criteria. The test suite verifies them — unit, integration, behavioral, architectural, performance, security. Git history provides the audit trail. Retrospectives capture learnings.

The [Overnight Autonomous Artifact Sweep](https://github.com/cristoslc/swain/blob/trunk/docs/swain-retro/2026-03-22-overnight-autonomous-artifact-sweep.md) found 9 specs that were implemented but never transitioned. The hierarchy created ceremony overhead that accumulated debt. Those 9 specs weren't read during implementation. They were written, then ignored. A test suite would have run every commit — and failed, forcing a rewrite.

### 3. Architecture as Testable Constraints

The [Architecture Intent-Evidence Loop trove](https://github.com/cristoslc/swain/blob/trunk/docs/troves/architecture-intent-evidence-loop/synthesis.md) identifies **boundary placement** as the most consequential architectural decision. Evans argues the number one failure mode of microservices adoption is getting the boundaries wrong. Fowler identifies polysemes — words that mean different things in different parts of the system — as invisible to tests but fatal to boundary integrity.

What if boundaries were encoded as tests?

```bash
# Boundary test: session management is isolated per worktree
test_worktree_isolation.sh:
  - start session in worktree A
  - start session in worktree B
  - verify session files are not shared
  - verify cross-worktree bookmark lookup fails (expected)

# Boundary test: skills don't modify superpowers
test_superpowers_immutable.sh:
  - hash all files in .agents/skills/superpowers/
  - run any skill
  - verify hashes unchanged
```

When a boundary is violated, the test fails. Not "the operator notices during retro" but "the gate blocks the merge."

### 4. Evidence Over Intent

Swain's current model: intent (artifacts) → execution (agents) → evidence (git, tests) → reconciliation (retros, drift reports).

What if evidence was the primary source of truth, and intent was derived from it?

Git history already tells you what was built. Test results tell you what works. Dependency graphs tell you what depends on what. **What if specs were auto-generated from this evidence, rather than manually written before implementation?**

The spec would be a projection: "here's what the code does, here's what the tests verify, here's what we think we decided." Reconciliation becomes automated drift detection: "the spec says X, the tests verify Y, the code does Z — investigate."

This inverts the loop. Instead of Intent → Execution → Evidence, it's Evidence → Intent → Reconciliation. The operator reviews auto-generated specs and corrects them, rather than writing specs and hoping agents follow them.

**This is where problem space, solution space, and intent space diverge:**
- **Problem space** — what users need (captured in behavioral tests, user journeys)
- **Solution space** — what we built (captured in code, unit tests, integration tests)
- **Intent space** — what we decided to build and why (captured in specs, ADRs, architecture docs)

Test-driven iteration keeps all three aligned. When tests fail, something drifted — maybe the code, maybe the spec, maybe our understanding of the problem. The test suite forces you to figure out which one.

### 5. Decision Budget, Not Decision Hierarchy

Swain's current model assumes the operator makes decisions (artifacts) and agents execute. The hierarchy exists to structure those decisions.

What if the operator's mental bandwidth was the constraint, not the decision structure?

The [Project Retro v0.1–v0.13](https://github.com/cristoslc/swain/blob/trunk/docs/swain-retro/2026-03-21-project-retro-v0.1-to-v0.13.md) notes: **"Agentic development has addictive qualities. The tight feedback loop of 'describe → see it built → describe the next thing' creates a compulsion similar to gaming addiction."**

What if the system enforced a **decision budget** — N decisions per session, after which the agent must stop and write up what it did? Not "you can keep making decisions" but "you've made 5 decisions, time to close and let the tests verify alignment."

The session would end not when the operator is tired, but when the decision budget is exhausted. The tests would run overnight. The retro would auto-generate. The operator would return to a report: "here's what was decided, here's what was built, here's where they diverge."

**This connects back to testing:** the decision budget only works if tests can verify alignment autonomously. Without tests, every decision requires operator review. With tests, the operator sets the constraint once, then the test suite enforces it across rewrites.



## Open Questions

This is speculative. I'm curious if this generalizes beyond swain:

1. **Is test-driven iteration specific to LLMs?** Or does it reveal something about planning in general? Humans also struggle to follow specs — but we can ask clarifying questions, notice ambiguities, push back on constraints. LLMs can't (reliably).

2. **What's the minimum viable test suite?** Unit tests are cheap. Integration tests are medium. Behavioral specs and fitness functions cost more to write and run. What's the minimum test suite that keeps drift bounded on a big project?

3. **Can evidence-first spec generation work?** Auto-generating specs from code + tests sounds useful until you realize the spec might be wrong in ways the tests don't catch. But maybe that's the point — the spec is a hypothesis, not a commandment.

4. **What other assumptions about agentic development are wrong?** I assumed:
   - Artifacts would be read and followed (they're not)
   - Hierarchy would reduce cognitive load (it increased it)
   - Reconciliation would be automated (it's manual)
   
   What else am I missing?



## This Doesn't Mean Abandon Specs

The counterpoint: specs still matter. They clarify your thinking. They capture product design. They document architecture. They steer humans. But they don't steer agents. Tests do that.

## What's Next

This post argues that test-driven iteration beats spec-driven planning for agentic development. Three followups are in the queue:

1. **Problem Space vs Solution Space vs Intent Space** — How tests triangulate between what users need, what we built, and what we decided. When tests fail, which space drifted?

2. **The Minimum Viable Test Suite** — What's the smallest test suite that keeps drift bounded on a big project? Unit tests are cheap. Fitness functions cost more. Where's the inflection point?

3. **Evidence-First Spec Generation** — Can specs be auto-generated from code + tests, then corrected by the operator? Or do we need intent specified up front?

## Invitation

If you're building agent systems, what's your hard-won lesson? Where did your assumptions fail? Where did tests rescue you from architecture debt?

I'm at [@cristoslc](https://github.com/cristoslc) on GitHub. The swain codebase is at [cristoslc/swain](https://github.com/cristoslc/swain). The retros are in `docs/swain-retro/`. The test suite is in `spec/`.

Come tell me what I'm missing.



## References

- [VISION-006 Capstone Retro](https://github.com/cristoslc/swain/blob/trunk/docs/swain-retro/2026-04-07-vision-006-capstone.md)
- [VISION-006 Full Session Retro](https://github.com/cristoslc/swain/blob/trunk/docs/swain-retro/2026-04-07-vision-006-full-session-retro.md)
- [Project Retro v0.1–v0.13](https://github.com/cristoslc/swain/blob/trunk/docs/swain-retro/2026-03-21-project-retro-v0.1-to-v0.13.md)
- [Overnight Autonomous Artifact Sweep](https://github.com/cristoslc/swain/blob/trunk/docs/swain-retro/2026-03-22-overnight-autonomous-artifact-sweep.md)
- [Teardown/Rewrite/Release Retro](https://github.com/cristoslc/swain/blob/trunk/docs/swain-retro/2026-04-01-teardown-rewrite-release.md)
- [Architecture Intent-Evidence Loop Trove](https://github.com/cristoslc/swain/blob/trunk/docs/troves/architecture-intent-evidence-loop/synthesis.md)
- [BDD Test Suite Spec](https://github.com/cristoslc/swain/blob/trunk/docs/superpowers/specs/2026-04-04-bdd-test-suite-design.md)
- [Automated Test Gates Spec](https://github.com/cristoslc/swain/blob/trunk/docs/superpowers/specs/2026-03-31-automated-test-gates-design.md)
