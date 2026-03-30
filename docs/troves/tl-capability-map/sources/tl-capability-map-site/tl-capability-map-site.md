---
source-id: "tl-capability-map-site"
title: "TL Capability Map — Draft Sketch"
type: web
url: "https://cristoslc.github.io/tl-learning-plan/capability-map.html"
fetched: 2026-03-29T00:00:00Z
hash: "f0807d37fe8682ab175202972d0cc6e54a462e5a17bbaf9770329868fab0b66d"
---

# TL Capability Map — Draft Sketch

A capability-based program for Tech Leads moving from application expertise to architectural thinking.

**Status:** Draft (March 2026)
**Source:** [GitHub Repository](https://github.com/cristoslc/tl-learning-plan)

Each capability has a situation, curated resources, and a practice exercise. Start with Capability 1 or jump to whatever your team needs most.

## Connection Map

**1. Smell-Test Claims** is the gateway. **2. Find Boundaries** and **3. Pressure-Test** are the core analysis pair; **4. Think in Production** extends 3 into operational thinking. **5. Data Product Thinking** builds on 2 — once you have boundaries, design what crosses them. **6. Strategic Map** and **7. Scope the Problem** feed **8. Design from the Business**: strategic context and problem scoping flowing into applied platform design. **9. Lead the Conversation** is the capstone.

### Capabilities

1. Smell-Test Claims
2. Find Boundaries
3. Pressure-Test
4. Think in Production
5. Data Product Thinking
6. Strategic Map
7. Scope the Problem
8. Design from the Business
9. Lead the Conversation
10. Write to Drive Decisions
11. AI Partner

## Reference Books (O'Reilly Learning)

- _Software Architecture: The Hard Parts_ — Ford, Richards, Sadalage, Dehghani
- _Building Evolutionary Architectures_ 2nd ed — Ford, Parsons, Kua, Sadalage
- _Data Mesh_ — Dehghani
- _Designing Data-Intensive Applications_ 2nd ed — Kleppmann & Riccomini
- _Fundamentals of Software Architecture_ — Richards & Ford
- _The Software Architect Elevator_ — Hohpe
- _An Elegant Puzzle_ — Larson

---

## CAPABILITY 1: Smell-Test an Architectural Claim

**Situation:** Someone in a design review says 'we need microservices for scalability' or 'event sourcing is the right pattern here.' It sounds reasonable. You're not sure if it actually is, but you don't have a way to push on it without sounding like you're just being difficult.

**What Changes:** You develop a reflex: *what kind of claim is this?* Some claims are backed by decades of evidence (tight coupling increases change cost). Some are patterns that work in specific contexts (event sourcing—when you need audit trails and temporal queries). Some are rules of thumb being stated as laws. Some are conference hype. The response is different for each. You stop asking 'is this right?' and start asking 'what would have to be true for this to be right?'

**You're Ready When:** You hear an architectural assertion in a meeting and your first instinct is to classify it, not accept or reject it. You can say 'that's a reasonable pattern—what's the context that makes it fit here?' without preparation.

**Practice:** Pick any claim from the architecture proposal (or from a recent design conversation). Write down: what kind of claim is this? What evidence would support it? What context would it need to be true? Bring your analysis to a session.

### Start Here (2 resources)

1. **How to Think Like an Architect** — Mark Richards — Video (45 min)
   The 'triangle of knowledge'—knowing what you don't know—and how to translate business needs into architectural characteristics.
   https://www.youtube.com/watch?v=W7Krz__jJUg

2. **"Good Enough" Architecture** — Stefan Tilkov — Video (42 min)
   Six real architectures that went wrong. Calibrates your instincts for too much vs too little architectural ambition.
   https://www.youtube.com/watch?v=PzEox3szeRc

### Go Deeper (8 resources)

1. **Thinking Like an Architect** — Gregor Hohpe — Video (50 min)
   Two decades of practice distilled: decision models, blind spots, bridging organizational layers.
   https://www.infoq.com/presentations/architect-lessons/

2. **Software Architecture: The Hard Parts** — Neal Ford & Mark Richards — Podcast (37 min)
   The two laws: 'everything is a trade-off' and 'why is more important than how.'
   https://www.infoq.com/podcasts/software-architecture-hard-parts/

3. **Is High Quality Software Worth the Cost?** — Martin Fowler — Article (15 min)
   Internal quality reduces cost over time—subverts the 'quality vs. speed' framing.
   https://martinfowler.com/articles/is-quality-worth-cost.html

4. **The Elephant in the Architecture** — Fowler & Boeckeler — Article (20 min)
   Business value as the most overlooked factor in architectural assessment.
   https://martinfowler.com/articles/value-architectural-attribute.html

5. **Developer to Architect — Lesson Series** — Mark Richards — Video (10 min each)
   200+ bite-sized architecture lessons. Browse and pick what's relevant.
   https://developertoarchitect.com/lessons/

6. **FSA Ch 2: Architectural Thinking** — Richards & Ford — Book (~45 min)
   How architects and developers should collaborate, technical breadth vs depth, analyzing trade-offs, and understanding business drivers.
   https://learning.oreilly.com/library/view/fundamentals-of-software/9781492043447/ch02.html

7. **FSA Ch 4: Architecture Characteristics Defined** — Richards & Ford — Book (~30 min)
   Systematic framework for the '-ilities'—operational, structural, and cross-cutting.
   https://learning.oreilly.com/library/view/fundamentals-of-software/9781492043447/ch04.html

8. **BEA Ch 8: Pitfalls and Antipatterns** — Ford, Parsons et al. — Book (~40 min)
   Pattern recognition for bad claims: Vendor King, Last 10% Trap, resume-driven development, inappropriate governance.
   https://learning.oreilly.com/library/view/building-evolutionary-architectures/9781492097532/ch08.html

---

## CAPABILITY 2: Find the Real Boundaries

**Situation:** You're looking at a system design and it has boxes with names. Modules, services, components. Are these *real* boundaries (different domains with different rules and different data) or just feature groupings someone drew to organize a slide deck?

**What Changes:** You learn to test boundaries with three questions: Does it own its data? Would a different team draw the same line? How much does it need to talk across the boundary to do its job? Fake boundaries fail at least one. You also learn that the number of boxes is not a quality signal—30 modules isn't better or worse than 7 until you know why each boundary exists.

**You're Ready When:** You can point to a specific boundary and say 'this one is real because [data ownership / independent change / minimal cross-talk]' or 'this one is suspicious because [shared database / high coupling / org-chart-driven].'

**Practice:** Take 3 of the architecture proposal's 30+ modules. For each: does it own its data? Would a team that didn't know about the architecture team's slide deck still draw this boundary? What cross-boundary communication does it need? Write up your assessment.

### Start Here (2 resources)

1. **Bounded Context** — Martin Fowler — Article (10 min)
   Concise definition with examples of how 'product' and 'customer' mean different things in different contexts.
   https://martinfowler.com/bliki/BoundedContext.html

2. **DDD & Microservices: At Last, Some Boundaries!** — Eric Evans — Video (50 min)
   The inventor of bounded contexts on how they give services real isolation.
   https://www.youtube.com/watch?v=yPvef9R3k-M

### Go Deeper (8 resources)

1. **50,000 Orange Stickies Later** — Alberto Brandolini — Video (50 min)
   EventStorming—a workshop technique where boundaries emerge from mapping business events.
   https://youtu.be/1i6QYvYhlYQ

2. **Practical DDD: Bounded Contexts + Events** — Indu Alagarsamy — Video (50 min)
   Worked e-commerce example showing how events achieve autonomous services.
   https://www.infoq.com/presentations/microservices-ddd-bounded-contexts/

3. **Bounded Context Canvas V3** — Nick Tune — Article (15 min)
   Workshop tool for mapping what a context owns, its communication, and business alignment.
   https://medium.com/nick-tune-tech-strategy-blog/bounded-context-canvas-v2-simplifications-and-additions-229ed35f825f

4. **Identify Microservice Boundaries** — Azure Architecture Center — Article (20 min)
   Step-by-step guidance using domain analysis. Prescriptive and concrete.
   https://learn.microsoft.com/en-us/azure/architecture/microservices/model/microservice-boundaries

5. **Vaughn Vernon on Strategic Monoliths** — SE Radio #495 — Podcast (60 min)
   How bounded contexts inform whether you need microservices at all.
   https://se-radio.net/2022/01/episode-495-vaughn-vernon-on-strategic-monoliths-and-microservices/

6. **Hard Parts Ch 5: Component-Based Decomposition Patterns** — Ford, Richards et al. — Book (~90 min)
   Six-step process for extracting services from a monolith.
   https://learning.oreilly.com/library/view/software-architecture-the/9781492086888/ch05.html

7. **Hard Parts Ch 7: Service Granularity** — Ford, Richards et al. — Book (~45 min)
   The disintegrators/integrators framework—structured reasons to split vs keep together.
   https://learning.oreilly.com/library/view/software-architecture-the/9781492086888/ch07.html

8. **FSA Ch 7: Scope of Architecture Characteristics** — Richards & Ford — Book (~30 min)
   The 'architecture quantum'—the independently deployable unit with high functional cohesion.
   https://learning.oreilly.com/library/view/fundamentals-of-software/9781492043447/ch07.html

---

## CAPABILITY 3: Pressure-Test a Design

**Situation:** A proposed architecture looks clean on paper. Nobody's asking hard questions because it's early and everyone wants to move forward. But you've seen 'clean on paper' before.

**What Changes:** You learn that non-functional requirements are the pressure. Not vague ones ('it should be fast') but specific ones ('field inspectors need to sync over 3G with P95 under 200ms'). Each real NFR rules out options and constrains others. You stop evaluating designs by how they look and start evaluating them by what would break them. You also learn fitness functions—automated tests for architectural properties.

**You're Ready When:** Given a design, you can name the top 3 quality attributes that would stress it, explain which part is most vulnerable to each, and sketch how you'd test for it.

**Practice:** Pick one quality attribute that matters for the new platform (offline sync? multi-tenancy? data freshness?). Write it as a specific, measurable scenario. Then trace through the architecture proposal: which component would this break first?

### Start Here (2 resources)

1. **Lesson 73: Architecture Fitness Functions** — Mark Richards — Video (10 min)
   What fitness functions are and how they protect architectural characteristics.
   https://developertoarchitect.com/lessons/lesson73.html

2. **Lesson 37: Translating Quality Attributes** — Mark Richards — Video (10 min)
   How to translate the '-ilities' into language business stakeholders understand.
   https://developertoarchitect.com/lessons/lesson37.html

### Go Deeper (7 resources)

1. **Building Evolutionary Architectures** — Parsons, Ford & Lewis — Video (55 min)
   The co-authors on evolutionary architecture and fitness functions as governance.
   https://gotopia.tech/episodes/232/building-evolutionary-architectures

2. **Fitness Function-Driven Development** — ThoughtWorks — Article (15 min)
   Making fitness functions first-class in the dev cycle.
   https://www.thoughtworks.com/en-us/insights/articles/fitness-function-driven-development

3. **15 Years of ATAM Data** — InfoQ — Article (20 min)
   Empirical: modifiability, performance, availability, and deployability drive real trade-offs.
   https://www.infoq.com/articles/atam-quality-attributes/

4. **Evolutionary Architecture** — Rebecca Parsons — Podcast (35 min)
   How fitness functions matured in practice between BEA editions.
   https://www.infoq.com/podcasts/evolutionary-architecture-evolution/

5. **Software Architecture: The Hard Parts** — Neal Ford & Mark Richards — Video (55 min)
   Trade-off analysis: service granularity, orchestration, distributed transactions.
   https://gotopia.tech/episodes/213/software-architecture-the-hard-parts

6. **BEA Ch 2: Fitness Functions** — Ford, Parsons et al. — Book (~45 min)
   Full taxonomy: atomic vs holistic, triggered vs continual, static vs dynamic, automated vs manual.
   https://learning.oreilly.com/library/view/building-evolutionary-architectures/9781492097532/ch02.html

7. **BEA Ch 4: Automating Architectural Governance** — Ford, Parsons et al. — Book (~60 min)
   Code-level fitness functions with ArchUnit, coupling metrics, linters as governance.
   https://learning.oreilly.com/library/view/building-evolutionary-architectures/9781492097532/ch04.html

---

## CAPABILITY 4: Think in Production

**Situation:** The architecture looks good on the whiteboard. Then it ships, and you discover there's no way to tell if offline sync is silently dropping records, no runbook for when the data pipeline stalls, and the only person who knows how the reconciliation service works is on vacation.

**What Changes:** You learn to design for day 2, not just day 1. Every service needs answers to: how do I know it's healthy? How do I know it's broken? What does the operator do when it breaks? How do I deploy a fix without downtime? You stop treating observability and operability as things you add after launch.

**You're Ready When:** Given a proposed service, you can sketch its health signals, its failure modes, and its recovery path. You push back on designs that can't answer these questions.

**Practice:** Pick one platform service. Answer: What are its health signals? How would an operator know it's silently failing? What's the recovery procedure? What happens to upstream/downstream services when it's down?

### Start Here (2 resources)

1. **Lesson 37: Translating Quality Attributes** — Mark Richards — Video (10 min)
   Translating the '-ilities' into operational concerns that stakeholders understand.
   https://developertoarchitect.com/lessons/lesson37.html

2. **Monitoring Distributed Systems** — Google SRE Book (Ch 6) — Article (20 min)
   The four golden signals (latency, traffic, errors, saturation).
   https://sre.google/sre-book/monitoring-distributed-systems/

### Go Deeper (4 resources)

1. **Implementing Service Level Objectives** — Google SRE Book (Ch 4) — Article (25 min)
   How to define SLIs, SLOs, and SLAs.
   https://sre.google/sre-book/service-level-objectives/

2. **Building Evolutionary Architectures** — Parsons, Ford & Lewis — Video (55 min)
   Fitness functions as automated operational governance.
   https://gotopia.tech/episodes/232/building-evolutionary-architectures

3. **BEA Ch 4: Automating Architectural Governance** — Ford, Parsons et al. — Book (~60 min)
   Code-level fitness functions with ArchUnit, coupling metrics, linters as governance.
   https://learning.oreilly.com/library/view/building-evolutionary-architectures/9781492097532/ch04.html

4. **DDIA 2e Ch 9: The Trouble with Distributed Systems** — Kleppmann & Riccomini — Book (~60 min)
   Everything that can go wrong: unreliable networks, clocks, process pauses.
   https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch09.html

---

## CAPABILITY 5: Data Product Thinking

**Situation:** A domain in your system produces data that other domains need. Right now it's a database table someone queries directly, or a CSV export. When the schema changes, consumers break. When the data is wrong, nobody knows until a report looks funny.

**What Changes:** You learn to treat data that crosses a boundary as a product—something with an owner, a contract, a quality guarantee, and a versioning strategy. You apply the DAUTNIVS checklist: Discoverable, Addressable, Understandable, Trustworthy, Natively accessible, Interoperable, Valuable, Secure.

**You're Ready When:** You can look at a data flow that crosses a domain boundary and decide whether it needs product treatment. You can name the DAUTNIVS attributes and apply them.

**Practice:** Pick a data flow that crosses a domain boundary. Apply the DAUTNIVS checklist. Where does it fall short, and what would you change?

### Start Here (2 resources)

1. **Data Mesh Principles and Logical Architecture** — Zhamak Dehghani — Article (45 min)
   The four data mesh principles and DAUTNIVS—the 8 attributes that define a real data product.
   https://martinfowler.com/articles/data-mesh-principles.html

2. **Data Mesh Paradigm Shift** — Zhamak Dehghani — Video (50 min)
   Dehghani's foundational talk with visuals showing domain-oriented data ownership.
   https://www.infoq.com/presentations/data-mesh-paradigm/

### Go Deeper (5 resources)

1. **Dehghani Ch 3: Principle of Data as a Product** — Book (~45 min)
   The full DAUTNIVS treatment.
   https://learning.oreilly.com/library/view/data-mesh/9781492092384/ch03.html

2. **Dehghani Ch 11: Design a Data Product by Affordances** — Book (~45 min)
   The data product as architectural quantum.
   https://learning.oreilly.com/library/view/data-mesh/9781492092384/ch11.html

3. **Dehghani Ch 9: The Logical Architecture** — Book (~40 min)
   How domains, data products, and platform planes interact.
   https://learning.oreilly.com/library/view/data-mesh/9781492092384/ch09.html

4. **Data Mesh Revisited** — Dehghani, Parsons et al. — Podcast (50 min)
   Honest assessment three years later—what worked, what was hard.
   https://www.thoughtworks.com/insights/podcasts/technology-podcasts/data-mesh-revisited

5. **Hard Parts Ch 14: Managing Analytical Data** — Ford, Richards et al. — Book (~40 min)
   Data mesh applied to the Sysops Squad case study.
   https://learning.oreilly.com/library/view/software-architecture-the/9781492086888/ch14.html

---

## CAPABILITY 6: Read the Strategic Map

**Situation:** Leadership standardizes on C#, pursues MDM, invests in data products. You can repeat the decision but you can't explain *why* it was made.

**What Changes:** You build a mental model of the company's strategic bets: why the new platform exists, why data products matter, why language standardization has a business rationale beyond preference.

**You're Ready When:** Someone asks 'why are we building the new platform instead of improving the legacy platform?' and you can give a clear, accurate, 2-minute answer without checking notes.

**Practice:** Pick one of the company's strategic bets. Write a 2-minute explanation of *why*. Test it on a colleague.

### Start Here (3 resources)

1. **Engineering strategy** — Will Larson — Article (15 min)
   How strategy actually forms: accumulated design decisions synthesized into direction.
   https://lethain.com/engineering-strategy/

2. **Things You Should Never Do, Part I** — Joel Spolsky — Article (10 min)
   The classic argument against rewrites.
   https://www.joelonsoftware.com/2000/04/06/things-you-should-never-do-part-i/

3. **Lessons from 6 Software Rewrite Stories** — Herb Caudill — Article (25 min)
   The counterpoint: six real rewrites show that building new alongside old often works.
   https://medium.com/@herbcaudill/lessons-from-6-software-rewrite-stories-635e4c8f7c22

### Go Deeper (15 resources)

1. **Is High Quality Software Worth the Cost?** — Martin Fowler — Article (15 min)
   https://martinfowler.com/articles/is-quality-worth-cost.html

2. **Technical Debt Quadrant** — Martin Fowler — Article (5 min)
   The 2x2 matrix (reckless/prudent vs deliberate/inadvertent).
   https://martinfowler.com/bliki/TechnicalDebtQuadrant.html

3. **Presenting to executives** — Will Larson — Article (10 min)
   Business value -> historical narrative -> explicit ask.
   https://lethain.com/presenting-to-executives/

4. **Building an effective technical strategy** — Sarah Wells — Video (30 min)
   https://leaddev.com/leadingeng-london-2023/video/building-effective-technical-strategy

5. **ThoughtWorks Technology Radar** — Guide (20 min)
   The Adopt/Trial/Assess/Hold framework.
   https://www.thoughtworks.com/radar

6. **The Platform and Program Split at Uber** — Gergely Orosz — Article (30 min)
   https://newsletter.pragmaticengineer.com/p/program-platform-split-uber

7. **Agile Master Data Management** — Scott Ambler — Article (20 min)
   What MDM is and why enterprises pursue it.
   https://agiledata.org/essays/masterdatamanagement.html

8. **Bottleneck #01: Tech Debt** — Martin Fowler et al. — Article (25 min)
   Organizational patterns for managing tech debt as a strategic concern.
   https://martinfowler.com/articles/bottlenecks-of-scaleups/01-tech-debt.html

9. **Data Monolith to Mesh** — Zhamak Dehghani — Article (30 min)
   The strategic 'why' of domain-oriented data ownership.
   https://martinfowler.com/articles/data-monolith-to-mesh.html

10. **Hohpe Ch 9: Architecture Is Selling Options** — Book (~20 min)
    https://learning.oreilly.com/library/view/the-software-architect/9781492077534/ch09.html

11. **Hohpe Ch 6: Making Decisions** — Book (~20 min)
    https://learning.oreilly.com/library/view/the-software-architect/9781492077534/ch06.html

12. **Hohpe Ch 15: A4 Paper Doesn't Stifle Creativity** — Book (~15 min)
    Standards enable rather than restrict.
    https://learning.oreilly.com/library/view/the-software-architect/9781492077534/ch15.html

13. **Hohpe Ch 26: Reverse Engineering Organizations** — Book (~20 min)
    https://learning.oreilly.com/library/view/the-software-architect/9781492077534/ch26.html

14. **Larson S3.3: Visions and strategies** — Book (~20 min)
    https://learning.oreilly.com/library/view/an-elegant-puzzle/9781492077930/ch03.html#visions_and_strategies

15. **Larson S3.6: Migrations** — Book (~25 min)
    Migrations as the sole scalable fix to tech debt.
    https://learning.oreilly.com/library/view/an-elegant-puzzle/9781492077930/ch03.html#migrations_the_sole_scalable_fix_to_tech

---

## CAPABILITY 7: Scope the Problem

**Situation:** There's a vague mandate: 'build the new platform.' Or a specific one that's actually three problems wearing a trenchcoat. Nobody has explicitly decided what's out of scope.

**What Changes:** You learn to frame problems before solving them. What's the actual question? Who are we building for first? What would we *not* build even if we could? You develop the discipline of writing a scope statement specific enough to be wrong.

**You're Ready When:** Given a vague initiative, you can produce a one-page scope statement that names the problem, the audience, what's in, what's explicitly out, and what assumptions you're making.

**Practice:** Write a scope statement for the new platform MVP. Which service offerings are in the first launch? Which business capabilities are fully in scope, which are partial, which are deferred?

### Start Here (2 resources)

1. **Solving the Engineering Strategy Crisis** — Will Larson — Video (49 min)
   What engineering strategy is and how to make scope decisions visible.
   https://lethain.com/solving-the-engineering-strategy-crisis-videos/

2. **Writing an Engineering Strategy** — Will Larson — Article (15 min)
   Practical framework for strategy documents that scope work.
   https://lethain.com/eng-strategies/

### Go Deeper (3 resources)

1. **Core Domain Patterns** — Nick Tune — Article (10 min)
   Core Domain Charts: classify capabilities as core, supporting, or generic.
   https://medium.com/nick-tune-tech-strategy-blog/core-domain-patterns-941f89446af5

2. **FSA Ch 5: Identifying Architectural Characteristics** — Richards & Ford — Book (~30 min)
   https://learning.oreilly.com/library/view/fundamentals-of-software/9781492043447/ch05.html

3. **FSA Ch 19: Architecture Decisions** — Richards & Ford — Book (~35 min)
   ADRs as scope artifacts.
   https://learning.oreilly.com/library/view/fundamentals-of-software/9781492043447/ch19.html

---

## CAPABILITY 8: Design from the Business Down

**Situation:** You're in a room with a consultant, a whiteboard, and a mandate to build a platform. The consultant has a proposal with 30+ modules. You have domain expertise and a business capability map. But you don't have a method for going from 'what the business does' to 'what the platform builds.'

**What Changes:** You learn to work in three layers: what the business does (capabilities), what the platform builds (services), and what the company sells (offerings). Capabilities are stable. Platform services are what you design. The value chain is the organizing axis. Where a capability produces data for others to consume, you apply data product thinking. Wardley mapping adds the build-vs-buy dimension.

**You're Ready When:** Given a business capability, you can identify the platform services it needs, explain why each service exists, and trace which service offerings depend on it.

**Practice:** Create a business capability map. Pick one capability row. List the platform services in that row. For each: why does this service exist? Which service offerings need it? Compare to the architecture proposal's module list.

### Start Here (2 resources)

1. **The Architect Elevator — Visiting the Upper Floors** — Gregor Hohpe — Article (15 min)
   Why developers need to understand business architecture.
   https://martinfowler.com/articles/architect-elevator.html

2. **Identify Business Capabilities** — Cartwright, Horn & Lewis — Article (15 min)
   Practical guide to identifying business capabilities as the first step in architecture.
   https://martinfowler.com/articles/patterns-legacy-displacement/identify-business-capabilities.html

### Go Deeper (7 resources)

1. **Business Capability Centric** — Martin Fowler — Article (5 min)
   What it means to organize around capabilities rather than technical layers.
   https://martinfowler.com/bliki/BusinessCapabilityCentric.html

2. **Platform Tech Strategy: The Three Layers** — ThoughtWorks — Article (12 min)
   Technology platform, service platform, experience platform.
   https://www.thoughtworks.com/insights/blog/platform-tech-strategy-three-layers

3. **Introduction to Value Chain Mapping** — Simon Wardley — Video (40 min)
   Why value chain position determines what to build, buy, or outsource.
   https://www.youtube.com/watch?v=NnFeIt-uaEc

4. **Wardley Maps (free book) — Ch 1-2** — Simon Wardley — Guide (~60 min)
   The complete on-ramp to Wardley mapping. Free, CC-licensed.
   https://learnwardleymapping.com/book/

5. **Use Domain Analysis to Model Microservices** — Azure Architecture Center — Article (20 min)
   The full chain from capability identification to service design.
   https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis

6. **Legacy Architecture Modernisation with Strategic DDD** — Nick Tune — Article (15 min)
   Business capability analysis as the starting point for bounded contexts.
   https://medium.com/nick-tune-tech-strategy-blog/legacy-architecture-modernisation-with-strategic-domain-driven-design-3e7c05bb383f

7. **Core Domain Patterns** — Nick Tune — Article (10 min)
   Core Domain Charts: classify capabilities as core, supporting, or generic.
   https://medium.com/nick-tune-tech-strategy-blog/core-domain-patterns-941f89446af5

---

## CAPABILITY 9: Lead the Conversation

**Situation:** You have the analysis. Now you need to do something with it. The architecture team is proposing. Leadership wants to know if it's right. Your team needs to understand why decisions are being made.

**What Changes:** The vocabulary stops being foreign—not because you memorized definitions, but because you've used the concepts to do real work. You can explain a trade-off to a consultant, justify a scope decision to a director, and walk a developer through why a boundary exists.

**You're Ready When:** You can run a working session—not just attend one. You can present your domain map and defend your boundary choices.

**Practice:** Pick one: (1) Write a 5-minute presentation of the capability map for a non-technical stakeholder. (2) Prepare a co-design agenda for a 90-minute session with the architecture team. (3) Teach a teammate one concept using a real example.

### Start Here (2 resources)

1. **Starbucks Does Not Use Two-Phase Commit** — Gregor Hohpe — Article (15 min)
   The best non-academic intro to async messaging and eventual consistency.
   https://www.enterpriseintegrationpatterns.com/ramblings/18_starbucks.html

2. **The Architect Elevator — Visiting the Upper Floors** — Gregor Hohpe — Article (15 min)
   How architects translate between business strategy and technical execution.
   https://martinfowler.com/articles/architect-elevator.html

### Go Deeper (10 resources)

1. **Data Consistency Using Sagas** — Chris Richardson — Video (50 min)
   Practical walkthrough of the saga pattern.
   https://www.infoq.com/presentations/saga-microservices/

2. **When to Use Microservices (And When Not To)** — Sam Newman & Martin Fowler — Video (35 min)
   When microservices are overkill and why 'the monolith is not the enemy.'
   https://gotopia.tech/episodes/20/moving-to-microservices-with-sam-newman-and-martin-fowler

3. **Consumer-Driven Contracts** — Ian Robinson — Article (25 min)
   How consumers express expectations that providers must satisfy.
   https://martinfowler.com/articles/consumerDrivenContracts.html

4. **Turning the Database Inside Out** — Martin Kleppmann — Video (45 min)
   Reframes databases as streams of immutable facts.
   https://www.youtube.com/watch?v=fU9hR3kiOK0

5. **Hard Parts Ch 12: Transactional Sagas** — Ford, Richards et al. — Book (~50 min)
   8 named saga patterns.
   https://learning.oreilly.com/library/view/software-architecture-the/9781492086888/ch12.html

6. **Hard Parts Ch 13: Contracts** — Ford, Richards et al. — Book (~35 min)
   Strict vs loose contracts, stamp coupling, the 'need-to-know' principle.
   https://learning.oreilly.com/library/view/software-architecture-the/9781492086888/ch13.html

7. **DDIA 2e Ch 5: Encoding and Evolution** — Kleppmann & Riccomini — Book (~60 min)
   Schema evolution: JSON, Thrift, Protobuf, Avro.
   https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch05.html

8. **DDIA 2e Ch 8: Transactions** — Kleppmann & Riccomini — Book (~75 min)
   ACID, isolation levels, write conflicts, serializability.
   https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch08.html

9. **Chris Richardson on Microservice Patterns** — SE Radio #370 — Podcast (55 min)
   Broad vocabulary survey: sagas, API gateways, event sourcing, CQRS.
   https://se-radio.net/2019/06/episode-370-chris-richardson-on-microservice-patterns/

10. **Schema Evolution in Avro, Protobuf and Thrift** — Martin Kleppmann — Article (20 min)
    Concrete comparison of backward/forward compatibility.
    https://martin.kleppmann.com/2012/12/05/schema-evolution-in-avro-protocol-buffers-thrift.html

---

## CAPABILITY 10: Write to Drive Decisions

**Situation:** You had a great conversation in a meeting. Everyone agreed. Two weeks later, nobody can remember what was decided or why. Or: you have an important technical position but can't get 30 minutes with the right people.

**What Changes:** You learn that writing is not documentation—it's a tool of influence. An RFC isn't a formality; it's how you get a decision made without needing everyone in a room. An ADR isn't a record; it's how you prevent the same argument from happening every quarter.

**You're Ready When:** You've written an RFC or design doc that drove a real decision—not just described one after the fact.

**Practice:** Pick one architectural decision facing the new platform. Write a one-page decision document: context, options considered, recommendation, trade-offs, what you're giving up. Share it and ask someone to disagree with one specific point.

### Start Here (2 resources)

1. **Scaling the Practice of Architecture, Conversationally** — Andrew Harmel-Law — Article (30 min)
   How to decentralize architectural decisions using ADRs and conversational practices.
   https://martinfowler.com/articles/scaling-architecture-conversationally.html

2. **FSA Ch 19: Architecture Decisions** — Richards & Ford — Book (~35 min)
   ADR structure, anti-patterns (Covering Your Assets, Groundhog Day).
   https://learning.oreilly.com/library/view/fundamentals-of-software/9781492043447/ch19.html

### Go Deeper (3 resources)

1. **Writing an Engineering Strategy** — Will Larson — Article (15 min)
   Strategy docs as the upstream artifact.
   https://lethain.com/eng-strategies/

2. **The Architect Elevator** — Gregor Hohpe — Article (15 min)
   Writing for executives vs writing for engineers—same decision, different framing.
   https://martinfowler.com/articles/architect-elevator.html

3. **FSA Ch 20: Analyzing Architecture Risk** — Richards & Ford — Book (~30 min)
   Risk storming as a collaborative written exercise.
   https://learning.oreilly.com/library/view/fundamentals-of-software/9781492043447/ch20.html

---

## CAPABILITY 11: Use AI as a Thinking Partner

**Situation:** You have GitHub Copilot. Maybe you've tried Claude or ChatGPT. You use them for autocomplete or quick answers. But when you try something harder, the results are too generic or confidently wrong.

**What Changes:** You stop treating AI like a search engine and start treating it like a junior colleague who's read everything but built nothing. You lead the conversation—you provide the context, set the constraints, decide what's useful. You develop a healthy skepticism: AI output sounds authoritative whether it's right or wrong.

**You're Ready When:** You can take a document and run a structured AI-assisted analysis that produces findings you'd trust enough to bring into a review.

**Practice:** Feed a section of the architecture proposal to Claude with specific context. Ask: 'What assumptions is this making? Where are the gaps?' Compare findings to your own reading.

### Start Here (2 resources)

1. **Agentic Coding** — Armin Ronacher — Video (71 min)
   The creator of Flask sharing his real production workflow with Claude Code.
   https://www.youtube.com/watch?v=bpWPEhO7RqE

2. **AI Coding Degrades: Silent Failures** — IEEE Spectrum — Article (10 min)
   How LLMs silently remove safety checks and fake output formatting.
   https://spectrum.ieee.org/ai-coding-degrades

### Go Deeper (4 resources)

1. **AI Impact on Experienced Developer Productivity** — METR — Research (20 min)
   AI tools made experienced devs 19% slower on familiar codebases—despite believing they were 20% faster.
   https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/

2. **A Year of Vibes** — Armin Ronacher — Article (15 min)
   Full-year retrospective on agentic coding in production.
   https://lucumr.pocoo.org/2025/12/22/a-year-of-vibes/

3. **Agentic Engineering Patterns** — Simon Willison — Guide (30 min)
   Curated practices for AI coding agents. Living document.
   https://simonwillison.net/guides/agentic-engineering-patterns/

4. **AI Tooling for Software Engineers in 2026** — Gergely Orosz — Article (25 min)
   Survey of ~1000 engineers on actual AI usage. Data, not vendor claims.
   https://newsletter.pragmaticengineer.com/p/ai-tooling-2026
