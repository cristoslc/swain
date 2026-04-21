# Supplemental Synthesis II: Testing Practices and Swain's Core Loop

## Purpose

This synthesis steps back from the specific recommendations (Synthesis I) and examines how the testing practices research suggests changes to Swain's core operational loop. The core loop is defined in PURPOSE.md: **Intent -> Execution -> Evidence -> Reconciliation**. The question is: does the testing research confirm this loop, reject it, or suggest modifications?

---

## The Core Loop Confirmed

The testing research does not challenge Swain's four-phase loop. If anything, it reinforces it:

- **Intent** corresponds to what BDD calls "behavior design" and what SBE calls "specification by example." The testing research confirms that clear intent (what should be true) is a prerequisite for meaningful verification.
- **Execution** is where implementation happens. TDD, ATDD, and property-based testing are all practices that shape execution by writing specifications before code.
- **Evidence** is what test results, mutation scores, fitness function outputs, and exploration observations produce. The research confirms that evidence must come from verifiable sources, not from declarations.
- **Reconciliation** is where drift between intent and evidence is detected. The research on compliance testing, contract testing, and architecture fitness functions is entirely about reconciliation: does reality still match intent?

The loop structure holds. But the research suggests four ways in which the loop's current implementation is incomplete.

---

## Change 1: The Loop Needs an Exploration Phase Between Evidence and Reconciliation

### Current transition

```
Intent -> Execution -> Evidence -> Reconciliation ->
```

The loop assumes that reconciliation compares intent against evidence. This is verification thinking: "does the evidence match what we intended?"

### What the research reveals

Exploratory testing, chaos engineering, and observability-driven testing all operate in a mode that is not captured by the current transition from Evidence to Reconciliation. They produce evidence of things that intent never specified. The reconciliation phase can compare intent against evidence ("does the implementation match the spec?"), but it cannot compare evidence against unspecified intent ("what problems exist that no spec covers?").

This is a qualitative gap. The loop has a verification mode (compare against known intent) but no exploration mode (discover unknown intent gaps). Marick's framing makes this precise: Q1/Q2 tests support the team; Q3/Q4 tests critique the product. Swain's loop only supports Q1/Q2.

### Proposed modification

Add an exploration phase between Evidence and Reconciliation:

```
Intent -> Execution -> Evidence -> Exploration -> Reconciliation ->
                    ^                                          |
                    |__________________________________________|
```

The exploration phase:
- Runs after verification evidence is collected (not instead of).
- Uses charters derived from VISION, INITIATIVE, and SPEC context to focus discovery.
- Produces observations, not pass/fail results.
- Feeds observations into reconciliation as discovery signals (Synthesis I, Recommendation 7).
- Can generate new intent (filing SPECs, ADRs) that flows back into the loop.

This change is structural. It adds a phase to the loop. In DESIGN-027, verification design is currently a single phase that discovers existing tests and writes new ones. With this change, verification design would have two sub-phases: verification (confirm known requirements) and exploration (discover unknown problems).

PURPOSE.md's three questions need a fourth:

| Current | Proposed |
|---------|----------|
| 1. What needs a decision? | 1. What needs a decision? |
| 2. What's ready for execution? | 2. What's ready for execution? |
| 3. Does reality still match intent? | 3. Does reality still match intent? |
| | 4. What problems exist that no spec covers? |

Question 4 is the exploration question. It is not answerable by reconciling intent against evidence, because it asks about intent that doesn't exist yet.

---

## Change 2: Fitness Functions Turn Intent Into Continuously Verified Constraints

### Current model

Intent lives in artifacts (SPECs, ADRs, VISIONs). Verification checks whether the implementation matches the intent described in those artifacts. Intent is verified episodically: when swain-test runs, when a plan completes, when swain-sync checks for drift.

### What the research reveals

Architecture fitness functions (Ford/Parsons/Kua) and compliance testing (OPA, compliance-as-code) demonstrate that intent can be continuously verified, not episodically. An ADR that says "all scripts must follow ADR-019" can become a test that runs on every commit, not just when an agent happens to read the ADR.

This is a fundamental shift in the relationship between intent and verification. Currently, intent is declarative (markdown files) and verification is procedural (test scripts that may or may not check the declarations). Fitness functions make intent executable: the ADR is both the declaration and the test.

### Proposed modification

**Treat ADRs as executable fitness functions, not just declarative documents.**

This does not require changing the loop. It changes the implementation of intent within the loop:

- Every ADR should have an associated verification check (a bats test, a script, a command) that validates compliance.
- These checks run in CI and in swain-test Phase 3 (Synthesis I, Recommendation 9).
- ADRs without verification checks are "unenforced intent" — they exist as declarations but the system doesn't verify them.

The loop becomes:

```
Intent (declarative + executable) -> Execution -> Evidence (including fitness function results) -> Exploration -> Reconciliation ->
```

Intent is no longer just "what was decided." It is also "what must continuously be true." The ADR compliance checks in DESIGN-027 were treated as something the agent reads and reasons about. They should be something the system runs and reports on.

---

## Change 3: Contract Testing Reveals a Missing Relationship Type

### Current model

Swain's artifact system has parent-child relationships (SPEC under EPIC under INITIATIVE under VISION) and cross-references (artifact-refs with relationship types like `[aligned]`, `[supersedes]`, `[depends-on]`). But there is no "contract" relationship — no way to say "this SPEC (consumer) expects this SPEC (provider) to behave in this way."

### What the research reveals

Consumer-driven contract testing (Pact, Ian Robinson's pattern) demonstrates that the gap between what consumers expect and what providers deliver is a persistent source of bugs. This applies directly to Swain's artifact system:

- A SPEC that describes a skill's behavior is a **consumer contract**: it specifies what the skill should do.
- The skill's implementation (SKILL.md + scripts) is the **provider**: it delivers the behavior.
- The swain-test Phase 2 behavioral verification is currently an **integration test**: it checks the whole system end-to-end.
- What's missing is a **contract test**: a check that the skill's SKILL.md interface hasn't drifted from what SPECs expect of it.

This is different from BDD traceability (which EPIC-062 proposes). Contract testing is not about linking Gherkin scenarios to test code. It's about verifying that the interface between two components hasn't broken. In Swain, the "components" are skills and their consumers.

### Proposed modification

**Add a `[contracts-with]` relationship type to artifact-refs.**

```yaml
artifact-refs:
  - artifact: SPEC-220
    rel: [contracts-with]
```

This would mean: "SPEC-220 defines a contract that the referenced artifact must satisfy." Verification would then check whether the contract is still satisfied by reading both the SPEC (consumer) and the referenced artifact (provider) and comparing their interfaces.

This is a lighter-weight alternative to the full BDD traceability chain (Recommendation 2 in Synthesis I). Instead of building Gherkin-to-test-code linkage, build SPEC-to-artifact contract linkage. The contract is already implicit in every SPEC that says "this skill must do X." Making it explicit costs almost nothing and enables contract-like verification.

---

## Change 4: Synthetic Monitoring Closes the Loop Back to Intent

### Current model

The loop's reconciliation phase detects drift and feeds it back to intent. But this drift detection is entirely within the development environment (git, artifacts, local tests). Once code is merged to trunk, the loop has no way to detect drift between merged intent and runtime reality.

### What the research reveals

Synthetic monitoring (Fale/Gebhardt) and testing in production (Wilsenach, Majors) demonstrate that some drift only manifests in the runtime environment: performance degradation, configuration drift, dependency failures, data corruption. The testing-in-production movement argues that this drift should feed back into intent just like pre-merge drift does.

### Proposed modification

**Design the verification model so that post-merge evidence can flow back into intent.**

This does not require building production monitoring infrastructure now. It requires designing the model so that when Swain has a live installation (or when projects using Swain have live installations), the evidence loop can close:

```
Production synthetic monitoring
        |
        v
   Evidence (post-merge)
        |
        v
   Reconciliation (detect drift between merged intent and runtime behavior)
        |
        v
   New intent (SPEC, ADR, or ticket) if drift is found
```

Concretely: every `swain-test.sh` Phase 1 integration test should be runnable as a synthetic transaction against a live installation. This means the tests must be idempotent, isolated, and safe to run against production data. The bats-core suite is already close to this — it uses `create_test_sandbox()` for isolation. The gap is ensuring that every test can also target a non-sandboxed environment.

---

## Change 5: Mutation Testing Measures Verification Quality, Not Just Code Quality

### Current model

Swain's verification model asks: "does the evidence match the intent?" It never asks: "would the evidence still match the intent if the code were slightly wrong?"

### What the research reveals

Mutation testing (DeMillo/Lipton/Sayward, Stryker, PITest) answers exactly this question. It introduces small faults into the code and checks whether the test suite detects them. A high mutation score means the test suite catches most introduced bugs. A low mutation score means the test suite has gaps — tests pass, but they're not catching real bugs.

In Swain's loop, mutation testing sits between Evidence and Reconciliation. It is a meta-evidence practice: it provides evidence about the quality of evidence. Without it, a passing test suite is an unvalidated claim. "All tests pass" might mean "the code works correctly" or it might mean "the tests don't catch the bugs that exist."

### Proposed modification

**Add mutation testing as an optional verification modality that runs periodically (not on every invocation).**

This is a quality metric, not a gate. It runs:
- On demand (when the operator asks "how good is our test suite?").
- Periodically (weekly, in CI when it exists).
- After significant changes to the test suite (when a new verification modality is added).

The mutation score feeds back into reconciliation as a measure of verification quality. If the mutation score is low, that's a signal that the tests are not earning their keep — the loop's evidence phase may be producing false confidence.

---

## Change 6: The Loop Should Embrace Reconciliation-Generated Intent

### Current model

Reconciliation detects drift between intent and evidence. When execution drifts from intent, the fix is in the code. When intent drifts from reality, the fix is in the decision. But in practice, Swain's reconciliation is asymmetric: it is much better at detecting code drift than at generating new intent.

### What the research reveals

The testing research reveals that the most valuable output of verification is often not "the code matches the spec" but "we discovered something the spec doesn't cover." Exploratory testing, chaos engineering, and observability-driven testing all produce this kind of discovery. The loop should not just reconcile existing intent against evidence — it should also generate new intent from discoveries.

This is already implied by PURPOSE.md: "Execution is where learning happens." But it is not implemented in the loop. The current reconciliation spectrum (small/medium/large) only handles misalignment between existing intent and existing evidence. It does not handle the creation of new intent from discoveries.

### Proposed modification

**The discovery severity from Synthesis I Recommendation 7 (file new SPEC or ADR) is the implementation of this change.** But the deeper implication is that the loop should treat intent generation as a first-class outcome, not just drift correction.

The modified loop:

```
Intent -> Execution -> Evidence -> Exploration -> Reconciliation -> Intent
                    ^                                          |
                    |______ (discovery: new SPEC/ADR/ticket) _|
```

The feedback arrow from Reconciliation back to Intent is reinforced. Reconciliation doesn't just correct drift — it also creates new intent when exploration or evidence reveals something that no existing intent covers.

This is the most fundamental change suggested by the research. It moves Swain from a system that verifies decisions to a system that also generates decisions. The operator still makes the final call (intent is the operator's domain, per PURPOSE.md), but the system surfaces what needs deciding.

---

## Summary of Proposed Loop Changes

| Change | Current | Proposed | Phase Affected |
|--------|---------|----------|----------------|
| 1. Exploration phase | Not present | Charter-based discovery after verification | New phase between Evidence and Reconciliation |
| 2. Fitness functions | ADRs are declarative only | ADRs have executable compliance checks | Intent phase becomes partially executable |
| 3. Contract relationships | artifact-refs use `[aligned]`, `[depends-on]` | Add `[contracts-with]` for consumer-provider contracts | Intent and Evidence phases |
| 4. Synthetic monitoring | Not present | Post-merge verification feeds back into intent | Extends the loop beyond merge |
| 5. Mutation testing | Not present | Periodic measure of test suite quality | Meta-Evidence (between Evidence and Reconciliation) |
| 6. Intent generation | Reconciliation corrects existing intent | Reconciliation also generates new intent | Reconciliation phase |

These changes do not replace the core loop. They extend it. The Intent -> Execution -> Evidence -> Reconciliation structure holds. But each phase becomes richer: Intent includes executable constraints, Evidence includes fitness function results and mutation scores, Exploration discovers unknown problems, and Reconciliation generates new intent rather than only correcting drift.

The loop becomes:

```
Intent (declarative + executable fitness functions)
  |
  v
Execution (implementation by agents)
  |
  v
Evidence (test results + contract verification + mutation scores)
  |
  v
Exploration (charter-based discovery of unknown problems)
  |
  v
Reconciliation (drift correction + new intent generation)
  |
  +---> (correction: fix code, update SPEC/ADR)
  |
  +---> (discovery: file new SPEC/ADR/ticket)
  |
  v
Intent (updated)
```

This is the loop that the testing research suggests. It is still Swain's loop — still oriented around the operator's decisions, still evidence-based, still reconciling intent against reality. But it is more capable: it can verify continuously (fitness functions), discover unknown problems (exploration), measure its own effectiveness (mutation testing), verify interfaces (contract testing), verify post-merge (synthetic monitoring), and generate new decisions (discovery-driven intent creation).