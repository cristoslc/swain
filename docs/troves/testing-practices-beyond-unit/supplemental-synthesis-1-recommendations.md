# Supplemental Synthesis I: Recommendations for Overhauling Swain's Verification System

## Purpose

This synthesis takes the trove's research findings and applies them directly to Swain's current verification architecture. It makes from-scratch recommendations for how to overhaul the swain-test skill, adapt the verification initiative (INITIATIVE-022) and related artifacts (DESIGN-027, EPIC-052, EPIC-062), and integrate testing practices that don't currently exist in Swain.

The recommendations are intellectually honest: they call out sacred cows, acknowledge where Swain's current design is wrong, and propose alternatives even when those alternatives conflict with current plans.

---

## 1. The Verification Loop Is Half a Loop

### Current state

DESIGN-027 describes a verification loop: implementation finishes, verification design discovers existing tests and writes new ones, tests run, failures loop back. This is a verification-only loop. It confirms that known requirements are met.

### The problem

The testing research converges on a hard split: **verification** confirms known requirements; **exploration** discovers unknown problems. Martin Fowler'sbliki and Brian Marick's quadrants formalize this as supporting-the-team vs. critiquing-the-product. Elisabeth Hendrickson's "net" metaphor makes it visceral: automated tests form a net that catches known bugs; exploratory testing finds holes in the net.

Swain's verification loop has no exploration phase. It can only verify against what it already knows — specs, ADRs, acceptance criteria. It cannot discover that a spec is missing an edge case, or that an ADR is silently violated in a way no test checks for, or that the agent's implementation works correctly for the stated requirements but fails catastrophically under conditions nobody thought to specify.

### Recommendation

**Rename the loop "Verification and Exploration Loop" and add a structured exploration phase.**

The exploration phase would run after verification passes (not instead of — verification first, then exploration). It would use charter-based discovery sessions inspired by exploratory testing:

- **Charter**: Each exploration session has a focused question ("what happens when the skill dispatches to an unavailable model?", "what happens when two agents modify the same artifact simultaneously?").
- **Time-boxed**: Each session is limited (5-10 minutes of agent time) to prevent runaway exploration.
- **Non-deterministic by design**: Where verification requires passing tests, exploration requires discovering new information. The output is observations, not pass/fail results.
- **Feeds back into the loop**: If exploration discovers an issue, it files a SPEC or ADR update, which becomes new intent, which triggers re-verification.

This maps to Marick's Q3/Q4 quadrants (business-facing and technology-facing critiques of the product) and fills a gap that no amount of BDD traceability can close.

---

## 2. BDD Traceability Is Over-Engineered

### Current state

EPIC-062 proposes a chain of seven specs (SPEC-269 through SPEC-275) to establish Gherkin-to-test-code traceability: `@id:` tags in specs, `@bdd:` markers in test code, `test-results.json` contracts, evidence sidecars with symlinks, staleness detection, and a `swain-verify` command.

### The problem

The testing research (Fowler, Searls, Adzic) converges on a practical principle: **the effort of maintaining traceability must earn its keep**. Justin Searls, endorsed by Martin Fowler, puts it directly: "People love debating what percentage of which type of tests to write, but it's a distraction. Nearly zero teams write expressive tests that establish clear boundaries, run quickly and reliably, and only fail for useful reasons. Focus on that instead."

Swain's BDD traceability chain would produce:
- Gherkin scenarios embedded in SPEC markdown
- Custom `@id:` and `@bdd:` marker syntax
- A JSON contract for test results
- Per-scenario evidence sidecars with symlinks
- A staleness detection system
- A verification CLI command

This is six specs of infrastructure to maintain for a project that has ~101 BDD tests across 20 bats files covering 13% of its consumer-facing scripts. The maintenance burden of the traceability chain will exceed its discovery value for the foreseeable future.

The deeper issue: Gherkin is designed for human stakeholders (product owners, business analysts) to read. In a solo-developer-plus-AI-agent context, there is no Three Amigos workshop. The operator is the sole stakeholder, and agents read the SPEC acceptance criteria directly. The Gherkin layer is a translation step between two audiences that are the same person.

### Recommendation

**Simplify EPIC-062 to three specs instead of seven, and drop the Gherkin layer entirely.**

| Current | Proposed | Why |
|---------|----------|-----|
| SPEC-269 Gherkin notation convention | SPEC-269 **Acceptance criteria as verification targets** | ACs in specs already serve the purpose. No new syntax needed. |
| SPEC-270 BDD test-code markers | SPEC-270 **Evidence sidecars** | Simplified: each artifact gets a `verification-log.md` that records what was verified and when. No `@bdd:` markers. |
| SPEC-271 Test results JSON contract | **Drop** | Too heavy. The verification-log.md is human-readable and sufficient. |
| SPEC-272 Evidence sidecars with symlinks | Merged into SPEC-270 | Simplified evidence recording. |
| SPEC-273 Commit-hash staleness detection | SPEC-273 **Staleness detection** | Keep. This is genuinely useful and cheap to implement. |
| SPEC-274 Swain-verify command | SPEC-274 **swain-verify command** | Keep, but define it as reading verification-log.md and comparing against current artifact state, not parsing `@bdd:` markers. |
| SPEC-275 BDD retrofit migration | **Drop** | No Gherkin to retrofit to. |

The verification-log.md approach aligns with SPEC-226 (which already proposes this) and avoids building a parallel Gherkin-to-test-code mapping that nobody except automated systems would read.

---

## 3. ADR Compliance Should Be Fitness Functions, Not Manual Scans

### Current state

`design-check.sh` and `adr-check.sh` scan ADRs and artifacts for compliance. They are shell scripts that produce text output. DESIGN-027 mentions "ADR alignment checks" as one of the things the verification design phase does, but it treats them as something an agent reads and reasons about, not as executable tests.

### The problem

The architecture fitness functions research (Ford/Parsons/Kua, ArchUnit) demonstrates that architectural constraints can and should be automated as executable tests. An ADR that says "all scripts must follow the conventions in ADR-019" should have a test that checks whether scripts follow those conventions. Currently, Swain relies on agents reading ADRs and reasoning about compliance. This is exactly the kind of thing an agent might "forget" during a long session.

### Recommendation

**Treat every ADR as a potential fitness function. When an ADR is adopted, create a bats test (or a command-line check) that verifies compliance with it.**

This is not far from what Swain already has. The `adr-check.sh` and `readability-check.sh` scripts are proto-fitness-functions. They just aren't integrated into the verification loop as first-class tests.

Concrete mapping:

| ADR | Fitness function | Type |
|-----|-------------------|------|
| ADR-019 Script conventions | A bats test that checks script structure, shebang, error handling | Compliance |
| ADR-013 Trunk + release branch | A test that `release` branch exists and trunk merges are clean | Compliance |
| Any readability ADR | The existing `readability-check.sh` | Characteristic |
| Any performance ADR | A threshold test that measures deployment time or response time | Characteristic |

This connects directly to the compliance-testing research: ADRs are governance decisions. Making them executable turns them from documents that agents might or might not read into tests that fail when the decision is violated.

---

## 4. The Two-Phase Gate Is Too Narrow

### Current state

The swain-test skill has two phases: Phase 1 (deterministic integration tests via `swain-test.sh`) and Phase 2 (agent-driven smoke tests). DESIGN-027 envisions a richer verification design phase but still frames it as "discover existing tests, write new tests, run them."

### The problem

The testing research identifies at least eight distinct verification practices beyond unit and integration tests, each serving a different purpose. The current two-phase gate recognizes only two (integration tests and smoke tests). It does not recognize:

- **Contract testing** — verifying that skills respect their SKILL.md interface contracts
- **Mutation testing** — measuring whether the existing test suite actually catches bugs
- **Property-based testing** — generating edge cases that no human would think to write
- **Compliance testing** — verifying that ADRs and architectural constraints are followed
- **Fitness functions** — verifying that -ilities (readability, script conventions, deployment time) meet thresholds
- **Exploratory testing** — discovering unknown problems through charters and sessions
- **Synthetic monitoring** — repurposing existing tests as production verification

### Recommendation

**Expand swain-test from a two-phase gate to a multi-modality verification system.**

The new structure would be:

| Modality | Trigger | Scope | Output |
|----------|---------|-------|--------|
| Integration tests (Phase 1) | Always | Deterministic | Pass/fail |
| Spec-derived verification (Phase 2) | Always | Agent-driven | Evidence per AC |
| Skill contract testing | When skills change | Agent dispatch | Activation confirmed/denied |
| ADR compliance testing | When ADRs exist | Fitness functions | Pass/fail per ADR |
| Mutation testing | On demand or periodic | Test suite quality | Mutation score |
| Property-based testing | On demand or when ACs are vague | Edge case discovery | Shrunk counterexamples |
| Exploratory sessions | After verification passes | Charter-driven | Observations, new SPECs |

Not all modalities run on every invocation. The sensitivity scaling that DESIGN-027 already envisions would decide which modalities to activate. Low-sensitivity changes (a typo fix) might only run integration tests. High-sensitivity changes (touching auth, changing core paths, modifying the loop) would run all modalities.

This is a significant expansion of scope, but it is also a significant increase in confidence. A verification system that can discover unknown problems (exploration), measure its own effectiveness (mutation testing), and validate architectural constraints (fitness functions) is qualitatively different from one that only confirms known requirements.

---

## 5. Sensitivity Scaling Should Be Explicit and Data-Driven

### Current state

DESIGN-027 says: "V1 is judgment-based, not rule-based." Agents decide sensitivity based on VISION context and file paths. The design acknowledges this as a future improvement area: "Future: automated sensitivity classifier based on file paths, ADR references, and VISION context."

### The problem

Judgment-based sensitivity is a sacred cow that should be questioned. The chaos engineering research teaches that even stochastic experiments benefit from structured hypotheses ("steady state hypothesis"). The canary deployment research teaches that sensitivity can be measured by monitoring business metrics, not by agent intuition. The property-based testing research teaches that edge cases emerge from random input generation, not from human reasoning about what might go wrong.

An agent that guesses sensitivity based on "vibes" about the code is no better than a human guessing. The whole point of the verification loop is to remove the operator from the loop during execution. Sensitivity classification should be automated from the start.

### Recommendation

**Define explicit sensitivity rules based on file paths, ADR references, and artifact metadata.**

| Signal | Sensitivity |
|--------|-------------|
| Files matching `*/auth*`, `*/security*`, `*/encrypt*` | High |
| Files referenced by an active ADR | High |
| Files in `skills/` or `.agents/skills/` or `.claude/skills/` | Standard |
| Files matching `*.md` only (documentation only) | Low |
| Files matching `docs/blog/*` | Low |
| SPEC with >5 acceptance criteria | High |
| SPEC with no acceptance criteria | Standard |
| Touching `swain-test.sh` or verification code | High (meta-change) |

This is not v2. It is implementable today with a simple file-matching ruleset in `.agents/execution-tracking.vars.json` or the sensitivity configuration file.

---

## 6. The Loop Limit Should Be Adaptive, Not Fixed

### Current state

DESIGN-027 specifies a default loop limit of 5 consecutive failures, configurable in `.agents/execution-tracking.vars.json`. A full pass resets the counter to zero.

### The problem

The property-based testing research demonstrates that shrinking (finding the minimal failing case) is more valuable than the raw number of failing cases. A fixed loop limit of 5 does not distinguish between:
- 5 different failures (the agent is trying different things and progressing)
- 5 identical failures (the agent is stuck in a loop)
- 5 failures where each one is smaller than the last (the agent is shrinking toward a fix)

Chaos engineering's "steady state hypothesis" concept also applies here: if the system is improving with each iteration (more tests pass, smaller diffs), it makes sense to continue. If it's not improving, stop early.

### Recommendation

**Replace the fixed loop limit with an adaptive convergence check.**

- Track which tests fail in each cycle. Compare against the previous cycle.
- If the set of failing tests is identical across cycles (the agent is stuck): increment a stuck counter. Escalate when stuck_count > 2.
- If the set of failing tests shrinks (the agent is making progress): reset the stuck counter. Continue.
- If the set of failing tests grows (the agent is making things worse): increment a regression counter. Escalate when regression_count > 1.
- If a full pass is achieved: success. Reset all counters.

This borrows from property-based testing's shrinking behavior and chaos engineering's steady-state hypothesis. It is more nuanced than a fixed limit and more honest about whether the loop is converging or spinning.

---

## 7. The Reconciliation Spectrum Should Include Exploration Findings

### Current state

DESIGN-027 defines three reconciliation severities: small (add a ticket), medium (update SPEC/ADR), large (escalate to operator). These are all verification outcomes — the loop detected that implementation doesn't match intent.

### The problem

Exploration findings don't fit this spectrum. An exploration session might discover:
- A missing edge case that no spec covers (this is not a gap between implementation and a spec — it's a gap in the specs themselves).
- A resilience failure that only manifests under unusual conditions (not a bug in the current implementation — a brittleness in the architecture).
- A compliance drift where an ADR was violated so long ago that nobody remembers the original constraint.

These require new intent (new specs, new ADRs, new acceptance criteria), not just re-implementation of existing intent.

### Recommendation

**Add a fourth reconciliation severity: discovery (new intent needed).**

| Severity | Signal | Action | Example |
|----------|--------|--------|---------|
| Small | Implementation missed an edge case | Add ticket, continue loop | Race condition not accounted for |
| Medium | SPEC now misaligned with ADR | Update SPEC, continue loop | New ADR adopted mid-work |
| Large | SPEC is impossible or wrong | Stop, escalate to operator | "4GB embeddings in 200ms" |
| **Discovery** | **Exploration found something no spec covers** | **File new SPEC or ADR, continue loop** | **Agent discovers that concurrent artifact writes cause corruption, but no ADR or SPEC addresses concurrency** |

The discovery severity acknowledges that the loop can generate new intent, not just reconcile existing intent. This is a direct application of PURPOSE.md's principle: "Execution is where learning happens."

---

## 8. The Teardown Report Should Include Exploration Observations

### Current state

DESIGN-027 specifies that the teardown report includes verification design decisions, verification results, agent decision history, retro accumulation, and merge recommendation.

### The problem

If exploration sessions are added (Recommendation 1), the teardown report needs a section for exploration observations. These are not pass/fail results. They are discoveries: things found during exploration that no spec anticipated.

### Recommendation

**Add an "Exploration observations" section to the teardown report format.**

The section would contain:
- Charter that was explored (what question the session asked).
- Observations made (what was found).
- New intent filed (if any — SPECs, ADRs, or tickets created).
- Unresolved questions (observations that need operator judgment).

This section is where the "unknown unknowns" surface. It is the most valuable part of the teardown report for the operator, because it contains information that no verification phase could produce.

---

## 9. swain-test.sh Should Be a Verification Orchestrator, Not Just a Test Runner

### Current state

`swain-test.sh` (SPEC-220) is a 290-line script that detects test commands, runs integration tests, and emits structured output. It is a test runner, not a verification orchestrator.

### Recommendation

**Evolve swain-test.sh toward being a verification orchestrator that selects modalities based on context.**

This does not mean the script itself implements all modalities. It means the script:
1. Detects context (what changed, what ADRs are active, what specs are involved).
2. Selects which verification modalities to activate based on sensitivity rules (Recommendation 5).
3. Orchestrates the execution of each modality.
4. Collects and structures results for the evidence summary.

Phases:
- **Phase 1** (existing): Run deterministic integration tests.
- **Phase 2** (existing): Agent-driven smoke tests.
- **Phase 3** (new): ADR compliance fitness functions.
- **Phase 4** (new, on demand): Mutation testing of the test suite.
- **Phase 5** (new, on demand): Property-based testing for ACs marked with property invariants.
- **Phase 6** (new, after verification passes): Structured exploration sessions.

Phases 3-6 are optional and triggered by sensitivity rules. Not every run needs all six phases.

---

## 10. Production Verification Is the Missing Half

### Current state

Swain's entire verification model is pre-merge: verify before trunk merge, produce a teardown report, then merge. There is no post-merge verification. Once the code is on trunk, Swain has no way to verify that it works in the real environment.

### The problem

The testing-in-production research (Wilsenach, Majors) and synthetic monitoring research (Fale/Gebhardt) demonstrate that some bugs only manifest in production: real user traffic, real data distributions, real infrastructure. Swain's bats-core suite, repurposed as synthetic transactions, could run against a live Swain installation to catch these.

Canary deployment research (Sato) provides the progressive rollout pattern: deploy to trunk, let synthetic transactions verify business-critical paths, and automatically roll back if they fail.

### Recommendation

**Add a post-merge verification phase: synthetic monitoring of the live installation.**

This is a future recommendation (it requires a live installation and CI infrastructure that Swain doesn't currently have), but it should be designed into the verification model now:

1. The BDD tests in `spec/` should be runnable as synthetic transactions against a live Swain installation.
2. A `swain-monitor` command (or section in swain-test) should run these transactions on schedule and report results.
3. Results should feed into the observability loop: if a synthetic transaction fails, it should trigger a SPEC creation (not just an alert).

This closes the loop: verification before merge (pre-merge loop), verification after merge (synthetic monitoring), and reconciliation (drift detection between pre-merge expectations and post-merge reality).