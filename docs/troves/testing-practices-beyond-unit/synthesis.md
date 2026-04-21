# Testing Practices Beyond Unit Tests: Synthesis

## Scope

This trove covers 20 testing and QA practices beyond traditional unit testing, plus a mapping of Swain's current verification landscape. The research deliberately sought practices without "test" in the name (synthetic transactions, chaos engineering, fitness functions, canary deployment) alongside better-known techniques (BDD, TDD, contract testing). The goal: build a comprehensive view of what "verification" means when you stop thinking of it as "write assertions, run them, pass or fail."

## Key Findings

### 1. The testing vocabulary is much larger than Swain currently uses.

Swain's verification model recognizes four things: unit tests (bats-core), integration tests (swain-test.sh Phase 1), smoke tests (Phase 2), and BDD traceability (Gherkin in specs). The testing world outside recognizes at least 18 distinct practices, each with its own philosophy, tooling, and place in the lifecycle. The gap is not incremental — it is categorical.

### 2. "Testing" bifurcates into verification and exploration.

Martin Fowler'sbliki and Brian Marick's quadrants converge on a crucial split. **Verification** practices (TDD, BDD, contract testing, smoke tests, mutation testing, compliance testing) confirm that known requirements are met. **Exploration** practices (exploratory testing, chaos engineering, observability-driven testing, dogfooding) discover unknown problems. Swain's current model handles verification but has almost no capacity for exploration.

This split maps directly to Marick's quadrant axes. Supporting-the-team tests (Q1/Q2) are verification. Critiquing-the-product tests (Q3/Q4) are exploration. Swain's loop — Intent, Execution, Evidence, Reconciliation — is a verification loop. It has no structured exploration phase.

### 3. The most valuable practices for Swain may not look like "tests" at all.

Several practices from the research address problems Swain already has but currently solves with governance, not automation:

| Problem | Swain's current approach | Testing practice that could help |
|---------|-------------------------|--------------------------------|
| ADR compliance | design-check.sh manual scan | **Compliance testing** — ADR-as-executable-spec with ArchUnit-style fitness functions |
| Spec-code drift | staleness checks on evidence sidecars (Proposed) | **Contract testing** — consumer-driven contracts between specs and implementation |
| Production confidence | None (no CI, no synthetic monitoring) | **Synthetic transactions** — repurpose BDD tests as production monitoring |
| Architecture erosion | No automated -ility checks | **Fitness functions** — continuous verification of architectural characteristics |
| Unknown unknowns | operator discovers at teardown | **Exploratory testing** — charter-based discovery sessions |
| Resilience of the loop | "loop limit 5 then escalate" | **Chaos engineering** — deliberate fault injection to test loop recovery |
| Test suite quality | pass/fail only | **Mutation testing** — measure whether tests actually catch bugs |

### 4. The "fresh intent snapshot" idea in DESIGN-027 has deeper roots.

DESIGN-027's core insight — verification must run against the current artifact state, not the plan-time state — is a variant of what the testing-in-production movement calls "testing reality, not assumptions." Rouan Wilsenach's "QA in Production" makes the same argument for production systems. Gojko Adzic's Specification by Example makes it for requirements. The pattern is consistent across domains: the longer the gap between specification and verification, the more likely verification checks a world that no longer exists.

### 5. The testing trophy/pyramid/quadrant debate dissolves once you classify by purpose.

Martin Fowler's 2021 "Test Shapes" article demonstrates that the pyramid-vs-trophy-vs-honeycomb argument is mostly a terminology dispute. The real question is: what mix of verification depth, scope, and exploration does your system need? For Swain, the answer depends on the artifact type and lifecycle phase, not on a fixed proportion.

## Points of Agreement Across Sources

- **Verification is necessary but insufficient.** Every authoritative source agrees that automated verification catches known problems. Exploratory practices catch unknown ones. Both are needed.
- **Test doubles create a contract gap.** Consumer-driven contract testing exists because test doubles (mocks, stubs) can diverge from real services. This applies equally to Swain's relationship between specs and implementation.
- **Post-implementation verification is more reliable.** Whether you call it "fresh intent snapshot" (Swain), "testing in production" (Wilsenach), or "synthetic monitoring" (Fale/Gebhardt), the principle is the same: verify against the current state, not a past specification.
- **Fitness functions are underused.** Ford/Parsons/Kua, ThoughtWorks, and the ArchUnit community all argue that most teams lack automated checks for architectural characteristics. Swain's design-check.sh and adr-check.sh are early fitness functions, but they are not yet treated as first-class citizens in the verification loop.

## Points of Disagreement

- **Where to draw the pre/post-production boundary.** Wilsenach and Charity Majors argue for testing in production. Classic TDD and BDD literature assumes all testing is pre-production. Swain's verification loop currently sits in a gray zone: it runs after implementation but before trunk merge. It is not pre-deployment testing and it is not production verification. The research suggests this gap is intentional and valuable, but also that Swain is missing the production-side (synthetic monitoring, canary analysis).
- **Whether BDD traceability is worth the overhead.** EPIC-062 proposes a full Gherkin-to-test-code traceability chain (SPEC-269 through SPEC-275). The broader testing literature is split: Cucumber practitioners consider this essential; Martin Fowler and Justin Searls (endorsed by Fowler) argue that the effort of maintaining traceability often exceeds the value, and that writing expressive tests that fail for useful reasons matters more than traceability proportions.
- **Deterministic vs. agent-driven testing.** Swain's Phase 2 smoke tests are agent-executed and non-deterministic. The testing literature strongly favors deterministic, repeatable tests. This tension is inherent to AI-agent-based verification and has no clear precedent in the literature.

## Gaps in the Sources

- **No authoritative source on testing AI-agent output.** The literature covers testing software that humans write. Swain needs to test software that AI agents write. The verification challenge is different: agents can produce syntactically correct but semantically wrong code. Mutation testing and property-based testing are the closest analogues, but neither was designed for AI-generated code.
- **No framework for testing agent behavioral compliance.** Swain skills are behavioral specifications (SKILL.md files) that agents are supposed to follow. There is no established practice for testing whether an agent actually follows a skill's instructions. The closest analogues are contract testing (verify the agent obeys the skill contract) and exploratory testing (discover where the agent deviates).
- **Testing across artifact lifecycles.** No source addresses testing a system where the specifications (artifacts) themselves evolve during the verification process. Swain's fresh-intent-snapshot concept is novel in this regard.

## Implications for Swain

1. **The verification loop needs an exploration phase.** Currently INITIATIVE-022 is purely a verification loop (discover existing tests, write new tests, run them, loop). Adding a structured exploration phase — charter-based discovery sessions, chaos-style fault injection against the skills layer, observability of agent decision patterns — would make it a verification-and-exploration loop.

2. **BDD traceability should earn its keep.** Before investing in the full EPIC-062 chain (Gherkin tags, @bdd markers, test-results.json, evidence sidecars, staleness detection, swain-verify command), Swain should validate that the traceability overhead is justified by the discovery value. Searls' criterion applies: do the tests "establish clear boundaries, run quickly and reliably, and only fail for useful reasons"?

3. **Architecture fitness functions belong in the verification loop.** The DESIGN-027 "ADR alignment checks" are nascent fitness functions. They should be expanded into first-class verification: automated checks that ADRs are followed, that architectural invariants hold, and that -ilities (readability, script convention compliance) are continuously verified.

4. **Synthetic monitoring is the missing production-side practice.** Swain's bats-core suite could be repurposed as synthetic transactions against a live Swain installation, feeding results into a monitoring dashboard. This closes the gap between pre-merge verification and post-merge confidence.

5. **Mutation testing could validate Swain's test suite quality.** The bats-core suite has ~101 tests across 20 files, but Swain has no way to know if those tests actually catch bugs. Stryker or a equivalent could measure mutation coverage.