# Architecture Intent-Evidence Loop: Trove Synthesis

## Core Thesis

Swain's foundational architecture rests on a four-phase loop: **Intent -> Execution -> Evidence -> Reconciliation -> Intent**. This loop is not a process framework -- it's a claim about what kinds of things exist in a project management system and how they relate.

- **Intent** -- what has been decided (specs, ADRs, component catalog, architectural constraints, SLOs, boundary definitions)
- **Execution** -- where intent meets reality (agents implementing, building, migrating)
- **Evidence** -- what can be observed (git history, test results, dependency graphs, session outputs, the four golden signals, fitness function results)
- **Reconciliation** -- structured comparison of intent vs. evidence (drift reports, retros, compliance checks, error budget consumption)

## Theme 1: Architecture Matters More in the Agentic Era

### The Fundamental Justification

Traditional justifications for architecture (human navigability, cognitive load management) matter less when agents write most code. New justifications are stronger:

1. **Non-functional properties are structural, not behavioral** -- tests don't cover them (Richards: "everything in software architecture is a trade-off"; Tilkov: architecture must address the constraints that actually matter)
2. **Architecture encodes WHY** -- without it, agents introduce correct-but-structurally-wrong solutions. The polyseme problem (Fowler: "meter" meaning different things to different parts of the organization) is invisible to tests but fatal to boundary integrity
3. **Chesterton's fence scales with agent velocity** -- 10x code production means 10x blast radius when removing things with non-obvious purpose
4. **Quality pays for itself** -- Fowler demonstrates the "cost" of high internal quality is negative; the cruft accumulation curve crosses within weeks, not months. DORA research confirms elite teams are both faster AND more reliable

### Amortized Derivation

Architecture documents are caches of structural understanding. Re-derivation from code is expensive (tokens, time, reliability). The agentic era makes the cache more valuable because agents consume structural understanding at higher volume.

Richards' quality-attribute translation framework (Lesson 37) shows another dimension: the translated understanding of WHY a quality attribute matters to the business is itself expensive to re-derive. An ADR that explains "we chose eventual consistency because the business values availability over consistency for the shopping cart" encodes both the technical decision and its business justification.

The cache validity problem is where reconciliation becomes important. Fitness functions (Richards Lesson 73; Paul & Wang) provide the automated validity-checking mechanism.

## Theme 2: Finding and Maintaining Boundaries

### The Boundary Discovery Problem

Boundaries are the highest-leverage architectural decisions. Evans argues the number one failure mode of microservices adoption is getting the boundaries wrong. Fowler identifies the core challenge: polysemes -- the same word meaning subtly different things in different contexts -- can be smoothed over in conversation but not in software.

### Principled Approaches to Boundary Finding

Multiple complementary approaches emerge from the sources:

1. **Bounded Contexts (Fowler, Evans)** -- linguistic boundaries where a particular model and its ubiquitous language apply. The dominant factor is human culture: you need a different model when the language changes.

2. **Business Capabilities (Cartwright/Horn/Lewis, Narayan)** -- stable parts of the organization to structure teams and software around. Capabilities are relatively stable even as organization, processes, and technology change. The "think-it, build-it, run-it" team model ensures feedback loops stay intact.

3. **Domain Model Decomposition (Azure Architecture Center)** -- systematic approach: start with bounded contexts, examine aggregates, consider domain services, factor in nonfunctional requirements. Validation criteria include single responsibility, no chatty calls, independent deployability.

4. **Core Domain Classification (Tune)** -- not all boundaries deserve equal attention. Decisive cores require maximum architectural rigor; generic domains should use commodity solutions. The classification itself evolves over time (table stakes, commoditisation, black swan events).

### Boundaries in the Intent-Evidence Loop

Boundary placement decisions are among the most consequential and hardest to re-derive from code alone. Evidence of whether boundaries are well-placed includes coupling metrics, change propagation patterns, and deployment friction. When evidence shows coupling across boundaries, it signals that the intent (the boundary placement) needs revision.

## Theme 3: Pressure-Testing Architecture Through Fitness Functions

### From Subjective Assessment to Objective Measurement

Fitness functions bridge the gap between architectural intent and measurable evidence. Richards defines them as providing "objective measurement of some architectural characteristic." Paul and Wang extend this into a development methodology: just as TDD writes tests before code, fitness function-driven development writes architectural tests before implementing features.

### Categories of Fitness Functions

The ThoughtWorks article provides a practical taxonomy:

| Category | What It Tests | Loop Phase |
|----------|---------------|------------|
| Code Quality | Maintainability, test coverage | Evidence about internal quality |
| Resiliency | Fault tolerance, deployment safety | Evidence about structural properties |
| Observability | Monitoring, logging, tracing | Meta-evidence (is evidence collection working?) |
| Performance | Latency, throughput, error rates | Evidence about runtime behavior |
| Compliance | Regulatory, legal, corporate standards | Evidence about constraint conformance |
| Security | Vulnerability scanning, access control | Evidence about security posture |
| Operability | Runbooks, alerts, documentation | Evidence about amortized derivation presence |

### Translating Quality Attributes to Business Concerns

Richards (Lesson 37) identifies a critical communication gap: architects speak in "-ilities" while business stakeholders speak in terms of business needs. Without translation, architects make priority decisions unilaterally. The translation framework maps quality attributes to business impact:

- Scalability -> "Can we handle peak traffic without losing customers?"
- Availability -> "How much revenue per minute of downtime?"
- Maintainability -> "How quickly can we ship features our competitors are shipping?"

This translation is itself a form of intent that must be encoded and maintained.

## Theme 4: Production Thinking and Operational Evidence

### The Four Golden Signals

Google SRE's four golden signals provide the canonical framework for what production evidence to collect:

1. **Latency** -- distinguish successful from failed request latency
2. **Traffic** -- demand placed on the system
3. **Errors** -- failure rate (explicit, implicit, or by policy)
4. **Saturation** -- how full the most constrained resource is

### SLOs as Encoded Intent

SLOs are the canonical example of intent encoded as measurable specifications. The SLO control loop (measure SLIs -> compare to SLOs -> decide if action needed -> take action) IS the Intent-Evidence-Reconciliation loop applied to production systems.

Key insights from SRE practice:

- **Start from user needs, not what's easy to measure** -- working backward from objectives to indicators is more effective
- **Don't overachieve** -- the Chubby planned outage story shows that exceeding your SLO creates invisible coupling. Reconciliation must detect both under-delivery AND over-delivery.
- **Error budgets formalize reconciliation thresholds** -- how much divergence between intent and evidence is acceptable before action is required
- **Symptoms before causes** -- monitoring should primarily detect symptoms (what's broken) and use cause-oriented heuristics only as debugging aids

### Monitoring Philosophy

- Keep monitoring simple and comprehensible
- Every page should be actionable, urgent, and require intelligence
- Pages with rote responses are a red flag -- automate them
- Long-term monitoring decisions should prioritize sustainable operations over heroic firefighting
- The Bigtable case study shows how reconciliation (comparing SLO intent against evidence) can reveal that the intent itself needs revision

## Theme 5: Connecting Architecture to Business Strategy

### The Architect Elevator

Hohpe's elevator metaphor describes the architect's role as connecting the engine room (technical implementation) to the penthouse (business strategy). The telephone-game effect -- information losing meaning as it passes through layers -- is the organizational equivalent of the intent-evidence gap.

Key architectural framing from Hohpe:

- **Architecture as options** -- invest in architecture so you can change your mind later at a known cost. In volatile environments (per Black-Scholes model logic), the value of architecture options increases.
- **Architecture is fit for purpose, not good or bad** -- purpose depends on context (commercial agreements, skills availability, installed base)
- **Feedback loops are essential** -- the ivory tower anti-pattern has one cardinal flaw: no feedback on the effectiveness or cost of decisions
- **Architect the organization alongside technology** -- organizational systems are subject to the same forces as technical systems (synchronization points reduce throughput; layering manages complexity but increases latency)

### Business Capability Alignment

Narayan's business-capability centric model shows how organizational structure can reinforce or undermine the intent-evidence loop:

- **Project-centric teams break feedback loops** -- they don't live with consequences of their decisions, so reconciliation never happens
- **Capability-centric teams sustain reconciliation** -- long-lived ownership provides the sustained attention that comparing intent against evidence requires
- **Conway's Law supports capability alignment** -- a single team responsible for multiple related components enables high cohesion and low coupling

### Domain Investment Prioritization

Tune's core domain patterns provide the framework for allocating architectural attention:

- **Decisive Core** -- requires the most detailed intent specification and rigorous evidence collection
- **Generic Domains** -- minimal intent ("use a standard solution"); evidence is mainly "does it still work?"
- **Supporting Domains** -- moderate intent; reconciliation should watch for creeping complexity
- **Meta-reconciliation** -- the classification itself must be periodically validated (former cores become table stakes, commodities may become black swan cores)

## Theme 6: The Vision Structure Question (From Original Sources)

### The Four-Vision Structure is Lopsided

Stress-testing one vision per loop leg revealed:
- **Evidence (Observable Reality)** has the most independent gravity (9/10) -- swain's biggest gap
- **Intent Authority** has real substance (7/10) but overlaps VISION-001
- **Reconciliation** is conceptually important (6/10) but defined by its dependencies
- **Execution** collapses into existing VISION-005 (4/10) -- not enough independent mass

### The Unified Structure is Stronger

One root vision naming the full loop, with boundary-focused initiatives/epics:
- Preserves the insight (the loop) as a single concept
- Decomposes work along boundaries where pain actually lives
- Avoids bureaucracy for a solo developer
- Initiatives for upstream boundaries (schema problems), Epics for downstream (deliverables)

### VISION-004 is Inside the Loop

Operator Cognitive Support is not orthogonal -- the reconciliation->intent boundary is fundamentally about how many findings the operator can absorb per session.

## Cross-Cutting Insights

### The "Good Enough" Principle Applied to the Loop

Tilkov's "good enough" architecture and the SRE "perfection can wait" guidance converge: initial intent should be broad, with reconciliation driving refinement. Start with coarse-grained boundaries (Azure guidance), loose SLO targets (SRE guidance), and basic fitness functions. Tighten as evidence accumulates.

### The Quality Paradox

Fowler's demonstration that high internal quality is cheaper to produce has a parallel in the loop itself: investing in intent specification (architecture, ADRs, SLOs) feels like overhead but actually reduces the cost of future evidence collection and reconciliation. The cruft accumulation curve applies to architectural debt just as it applies to code debt.

### Evidence About Evidence

The observability fitness functions from ThoughtWorks highlight a recursive requirement: the loop needs evidence that its evidence-collection mechanisms are working. Monitoring must be monitored. This is the meta-reconciliation challenge -- ensuring the loop itself is healthy.

## Related Troves

- `likec4` -- LikeC4 architecture-as-code tool; its MCP server could serve as the graph query layer for the intent/evidence system
- `session-decision-support` -- evidence pool for VISION-004
- `design-staleness-drift` -- early reconciliation work

## Disciplines for Further Research

1. Ontology engineering -- maintaining authoritative declarations alongside derived facts
2. Configuration management (systems engineering) -- CMDB "catalog that doesn't drift" failure modes
3. Double-entry bookkeeping -- 500 years of parallel representations + discrepancy surfacing
4. Control theory -- feedback lag, gain, stability in reconciliation loops
5. Archival science -- provenance, appraisal, context of creation vs. use
6. Ethnomethodology -- invisible labor of maintaining records
7. Wardley Mapping -- capability evolution and strategic positioning (referenced by Tune)
8. Cynefin framework -- complexity classification for domain decisions (referenced by Tune)

## Open Questions

- Does Observable Reality deserve standalone vision status or is it an initiative under the unified root?
- Should VISION-004 be explicitly positioned inside the loop?
- Should VISION-005 absorb execution-fidelity concerns?
- What's the migration path for existing children of the current visions?
- Lightest-touch option: evolve VISION-001 with loop vocabulary rather than creating new visions?
- How should fitness functions be integrated into swain's existing reconciliation mechanisms (swain-doctor, pre-commit hooks)?
- What is the right granularity of SLO-like intent for a solo developer project?
- How does core domain classification apply to swain's own capabilities (intent management, execution tracking, evidence collection, reconciliation)?
