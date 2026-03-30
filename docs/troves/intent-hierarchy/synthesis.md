# Synthesis: Intent Hierarchy

**Trove:** intent-hierarchy
**Created:** 2026-03-25
**Extended:** 2026-03-29
**Question:** What is each tier of the intent hierarchy -- purpose, principles, vision, initiative, epic -- and where do the boundaries fall between them? How does writing serve as the mechanism that drives decisions and alignment across those tiers?

---

## 1. The Full Stack

The sources converge on a layered model where each tier answers a different question and operates at a different timescale. Not all tiers are artifacts; some are foundational concepts that constrain and orient everything below them.

| Tier | Question it answers | Timescale | Changes when... | Artifact? |
|------|-------------------|-----------|----------------|-----------|
| **Purpose** | Why do we exist? | Indefinite | Almost never | No -- foundational identity |
| **Principles** | How do we make decisions? | Years | Values or context shift fundamentally | No -- decision-making framework |
| **Vision** | What future state are we building toward? | 2-5 years | The world we're building for changes | Yes -- but stable for years |
| **Strategy** | What challenges must we overcome? | Year-plus | Diagnosis changes or policies fail | Yes -- written document (Larson) |
| **Initiative** | What problem are we solving? | Quarters to a year | Strategy shifts or problem is solved | Yes -- lifecycle-managed |
| **Epic** | How might we solve it? | Weeks to a quarter | Solution is shipped or invalidated | Yes -- lifecycle-managed |

## 2. Purpose: Why We Exist

**Definition:** Purpose is the reason an organization exists beyond making money. It is the deeply-held belief that inspires the organization to make a difference. (Aespire, Sinek)

**Key properties:**
- Answers "Why?" -- the reason for the journey, not the destination
- Precedes everything else: "Purpose precedes the first step" (Gary Burnison via Aespire)
- Is NOT a mission statement (mission = how), NOT a vision (vision = where), NOT a goal (goal = what you measure)
- Rarely changes -- it's identity, not strategy
- In Sinek's Golden Circle, purpose sits at the center ("Why")

**The boundary below:** Purpose tells you *why you're going*. Vision tells you *where*. If you can swap your purpose statement for another organization's and it still works, it's too generic -- you've written a vision or a platitude, not a purpose.

**What purpose is NOT:**
- Not a plan (purpose needs a plan, but is not one)
- Not measurable (you don't "achieve" purpose -- you pursue it)
- Not a slogan or tagline

## 3. Principles: How We Make Decisions

**Definition:** Principles are the decision-making framework that constrains how an organization pursues its purpose and vision. They define what you will and won't do, crystallizing your convictions and the lines you won't cross. (Ha Phan, ProductPlan, Regroup)

**Key properties:**
- Answer "How do we decide?" -- not "what do we build" or "where are we going"
- Are never "reached" -- they are an ever-present beacon, not a target (ProductPlan)
- Fill the gap between the 10,000-foot vision and day-to-day decisions (ProductPlan)
- Must be specific enough to resolve a real trade-off -- "user friendly" or "intuitive" are useless principles (Ha Phan)
- You can't define what you are until you define what you're not (Ha Phan)
- Go along with and support the product strategy/vision (Cagan)
- Are distinct from values, goals, metrics, requirements, and design principles

**Architectural principles as a special case:** Harmel-Law argues that architectural principles must be SMART (specific, measurable, achievable, realistic, testable), team-sourced rather than top-down, and limited to 8-15 so teams can remember them. An example: "Value independence of teams most highly -- split solutions along team lines." These principles guide decisions without dictating solutions, and they specifically evaluate architectural choices rather than general behavior.

**Principles as constraint, not aspiration:** Regroup draws a sharp line between principles and aspirations. "Be the most innovative in the industry" is a destination, not a principle. A principle articulates the *approach* -- how you navigate, not where you're going. Principles are tools, not ideals.

**The boundary above (vs. purpose):** Purpose says why you exist. Principles say how you'll behave while pursuing that purpose. Purpose is the motivation; principles are the constraints.

**The boundary below (vs. vision):** Vision describes a future state. Principles don't describe any state -- they describe a mode of operating that persists across visions. If your vision changes, your principles might not.

**What principles are NOT:**
- Not metrics or KPIs (too granular, too transitory)
- Not product requirements (you don't build principles)
- Not design principles (too implementation-specific)
- Not the company's mission statement (though they may inform it)

## 4. Vision: What Future State We're Building Toward

**Definition:** Vision is the desired future state -- what the world looks like when you get there. It's a 2-5 year aspirational destination that organizes work and inspires action. (Cagan, Aespire, existing product-vision-frameworks trove)

**Key properties:**
- Answers "What will it be like when we arrive?" (Aespire) or "How will things be better?" (Cagan)
- 2-5 year timeframe (Cagan), possibly longer (Pichler says 5+)
- Stable while strategy evolves -- "stubborn on the vision, flexible on the details" (Cagan)
- Does NOT lock you into features or sequencing (Cagan)
- Is the bridge between business strategy and product roadmap (Cagan)
- Should be clear, compelling, and inspiring -- not a spec

**The boundary above (vs. principles):** Vision describes a destination; principles describe how you'll travel. Vision changes when the destination shifts; principles endure across destinations.

**The boundary below (vs. strategy/initiative):** Vision describes the future state holistically. Strategy diagnoses the challenges standing between here and there (Larson). Initiatives are the strategic problems you choose to solve *in service of* that vision. Multiple initiatives execute against a single vision, each tackling a different facet.

**What vision is NOT:**
- Not a mission (mission = how you accomplish the vision)
- Not a roadmap (roadmap = what you build next; vision = where you're going)
- Not features or specs (too specific)

## 5. Strategy: What Challenges Must We Overcome

**Definition:** Strategy is a written diagnosis of the current situation combined with guiding policies and coherent actions to address it. Following Rumelt's framework, strategy has three parts: diagnosis (a theory of the challenge), guiding policies (approaches to grapple with it), and coherent actions (specific steps directed by policy). (Larson)

**Key properties:**
- Answers "What's in our way and how do we navigate it?"
- Must be written down -- undocumented strategy is implicit, unenforceable, and misaligned (Larson)
- Guiding policies must be applicable (usable for real tradeoffs), enforced (teams held accountable), and creating leverage (compounding impact)
- Strategy cannot be purely bottoms-up because enforcement requires authority (Larson)
- Three types of coherent actions: enforcements (maintaining rules), escalations (pathways for challenging policies), transitions (moving from current to new state)

**The boundary above (vs. vision):** Vision says where you're going. Strategy says what stands in the way and how you'll deal with it. Vision is aspirational; strategy is diagnostic. "Visions of ideal states without grounding in current reality often fail because they don't help organizations navigate actual challenges" (Larson).

**The boundary below (vs. initiative):** Strategy frames the overall challenge and the policies to address it. Initiatives carve off specific problems within that framing. One strategy generates multiple initiatives.

**Why strategy was a gap in the original synthesis:** The original 8 sources identified "strategy as a tier" as fuzzy and underspecified. Larson's framework fills this gap directly -- strategy sits between vision and initiative, its distinctive contribution being the *diagnosis* that grounds aspirational vision in current reality.

## 6. Initiative: What Problem Are We Solving?

**Definition:** An initiative is a larger-scale, problem-oriented effort that aligns with strategic goals. It identifies a problem area, opportunity, or domain to address -- the "what" of strategy execution. (ProdPad, Atlassian)

**Key properties:**
- Answers "What problem are we solving?" (ProdPad decision stack)
- Quarter-to-year timescale -- longer than epics, shorter than visions
- Problem-focused and outcome-oriented, NOT solution-focused (ProdPad, work-item-hierarchy trove)
- Compiles epics from potentially multiple teams toward a broader goal (Atlassian)
- Should be broken down if too large -- "build a profitable community" is an objective, not an initiative; V1/V2/V3 of the community are initiatives (ProdPad)
- The term "initiative" has largely replaced "theme" in modern usage (ProdPad)

**The boundary above (vs. strategy):** Strategy provides the diagnosis and guiding policies. Initiatives operationalize those policies by targeting specific problems. An initiative should be traceable back to a strategic diagnosis.

**The boundary below (vs. epic):** Initiative asks "What problem?" -- Epic asks "How might we solve it?" (ProdPad). Initiatives are problem-scoped; epics are solution-scoped. One initiative typically contains multiple epics representing different approaches or phases.

**What initiative is NOT:**
- Not an objective (objectives = why; initiatives = what problem)
- Not a feature (initiatives are problem-framed, not solution-framed)
- Not an epic (epics are solution-oriented)

## 7. Epic: How Might We Solve It?

**Definition:** An epic is a bounded body of solution-oriented work -- an experiment you run to address part or all of an initiative's problem space. (Atlassian, ProdPad)

**Key properties:**
- Answers "How might we solve this problem?" (ProdPad decision stack)
- Weeks-to-quarter timescale -- teams typically have 2-3 epics per quarter (Atlassian)
- Solution-focused and delivery-oriented
- Should be thought of as experiments, not feature commitments -- "Will implementing single sign-on reduce friction? Let's find out!" (ProdPad)
- Can involve building, removing, or changing features -- not just adding new code
- Breaks down into user stories/specs for implementation

**The boundary above (vs. initiative):** Initiative defines the problem space. Epic proposes a specific approach to the problem. If you're describing *what's wrong*, you're in initiative territory. If you're describing *what to try*, you're in epic territory.

**What epic is NOT:**
- Not a feature list (epics are experiments, not commitments)
- Not an initiative (epics are solution-scoped, not problem-scoped)
- Not a sprint-sized item (that's a story)

## 8. Writing as a Tool of Influence

The three new sources (Harmel-Law, Larson, Hohpe) converge on a theme absent from the original synthesis: **writing is not just documentation -- it is the primary mechanism through which decisions get made, alignment gets built, and influence gets exercised across organizational levels.**

### 8.1 Writing Drives Decisions (ADRs and Strategy Docs)

Harmel-Law's Advice Process makes this concrete: the act of writing an ADR *is* the decision-making process. The ADR is not a record of a decision made elsewhere -- it is the artifact through which the decision takes shape. Writing forces the decision-maker to articulate context, enumerate options, weigh consequences, and seek advice. The document becomes the thinking.

Larson makes the same argument at the strategy level: many organizations have implicit strategies but fail to write them down, which means the strategy cannot be enforced, debated, or improved. "Documentation makes implicit decisions explicit, enabling better enforcement and organizational alignment." The ten-step writing process he prescribes is not about producing a document -- it is about forcing clarity of thought through the discipline of writing.

### 8.2 Writing Before Meetings Changes Meetings

Both Harmel-Law and Larson describe workflows where written artifacts precede synchronous discussion:

- **Harmel-Law:** ADRs are written *before* the Architecture Advisory Forum meets. The forum discusses existing documents, not blank-slate brainstorms. This transforms meetings from discovery sessions into refinement sessions.
- **Larson:** Strategy drafts circulate to working groups, then stakeholders, then the full organization -- each round of written feedback narrows the scope of what needs synchronous discussion.

The pattern is consistent: **write first, then meet.** When you show up with a document, the meeting becomes about improving the decision, not discovering what the decision is about.

### 8.3 Writing for Different Audiences (The Elevator Problem)

Hohpe's architect elevator metaphor highlights that influence requires communicating across organizational levels -- from the engine room to the penthouse. The same architectural reality must be expressed differently depending on the audience:

- **For executives:** Frame architecture as options -- "you invest in architecture so you can change your mind later." Financial framing, business value, risk reduction.
- **For engineers:** Runtime architecture details, deployment patterns, scalability constraints. Technical depth, code-level implications.
- **For both:** The architect's job is to translate between these levels. Writing is the medium of that translation.

This has direct implications for the intent hierarchy: **each tier of the stack has a different audience and requires a different writing register.** Purpose and vision are written to inspire. Strategy is written to diagnose and constrain. ADRs are written to decide. Specs are written to execute.

### 8.4 Decentralized Writing as Scalable Architecture

Harmel-Law's central insight is that writing decentralizes architectural authority. When "anyone can make architectural decisions" and the mechanism is a written ADR, you replace gatekeeping with conversation. The five supporting elements (Advice Process, ADRs, Advisory Forum, Principles, Technology Radar) all revolve around written artifacts that enable asynchronous collaboration.

This is precisely the model that agentic design tools like swain-design implement: agents produce written artifacts (specs, ADRs, spikes) that move humans to act. The artifacts are not passive documentation -- they are active instruments of influence. An ADR that proposes a technology choice is exerting architectural influence. A spec that defines acceptance criteria is constraining implementation. A strategy doc that diagnoses challenges is framing what gets worked on next.

### 8.5 The Shadow Architecture Anti-Pattern

Harmel-Law identifies the most dangerous failure mode: **shadow architecture**, where decisions are made behind the scenes while written artifacts maintain a fiction of decentralization. This directly parallels the risk in any artifact-driven system -- if the written artifacts don't reflect actual decisions, the system of influence collapses. Writing only works as a tool of influence when the written artifacts are the actual source of truth.

## 9. The Boundaries: A Sharpening Test

For each tier, ask: "Could I swap this for another and still serve the tier above?"

- **Purpose:** Could another organization use this purpose? If yes, it's too generic.
- **Principles:** If I changed the vision, would these principles still apply? If yes, they're real principles. If no, they're strategy in disguise.
- **Vision:** If I eliminated one initiative entirely, would the vision still make sense? If yes, the vision is properly above the initiative layer.
- **Strategy:** If I changed the diagnosis, would the guiding policies still apply? If not, the strategy is properly grounded in reality, not platitudes.
- **Initiative:** Could I solve this problem with a completely different set of epics? If yes, the initiative is properly problem-scoped.
- **Epic:** Could this epic serve a different initiative? Sometimes yes -- and that's fine. But if it always could, the initiative might be too vague.

## 10. Points of Agreement Across Sources

1. **Each tier answers a fundamentally different question** -- why, how-to-decide, where, what-challenge, what-problem, how-to-solve
2. **Principles are not aspirations** -- they constrain; they don't inspire
3. **Vision is not strategy** -- vision is the destination; strategy is the diagnosis of what stands in the way (Larson fills the gap the original synthesis identified)
4. **Initiatives are problem-framed, epics are solution-framed** -- this is the sharpest boundary in the execution tiers
5. **Not everything needs to be an artifact** -- purpose and principles are foundational, not lifecycle-managed
6. **Terminology matters less than shared understanding** -- every source acknowledges naming varies across organizations
7. **Writing is the mechanism of influence** -- ADRs drive decisions (Harmel-Law), strategy docs create alignment (Larson), and translating between organizational levels requires written artifacts (Hohpe)
8. **Writing before meetings transforms meetings** -- from discovery into refinement (Harmel-Law, Larson)
9. **Decentralized writing scales decision-making** -- anyone can decide when the mechanism is a written document and an advice process (Harmel-Law)

## 11. Points of Disagreement

- **Where "mission" fits:** Aespire places mission as "how" (the path). Sinek's Golden Circle places "how" as processes/methods. Cagan doesn't use "mission" at all -- he uses "vision" and "strategy" in that space. The concept of mission is genuinely ambiguous in this hierarchy.
- **Whether principles sit above or beside vision:** Cagan says principles "accompany" the product strategy/vision. Regroup says principles are part of strategy itself. The placement differs, but the function is consistent: principles constrain how you pursue the vision.
- **Timeframe of vision:** Cagan says 2-5 years. Pichler says 5+ years. The range depends on domain volatility.
- **Top-down vs. bottoms-up for strategy:** Larson argues strategy requires top-down enforcement. Harmel-Law argues architectural decisions should be decentralized. These are not contradictory -- Larson's strategy sets the frame; Harmel-Law's advice process decentralizes decisions *within* that frame -- but the tension is real.

## 12. Gaps (Updated)

- ~~**"Strategy" as a tier:** Multiple sources reference strategy as sitting between vision and initiative, but none define it with the same precision as the other tiers.~~ **Resolved:** Larson's Rumelt-based framework (diagnosis + guiding policies + coherent actions) gives strategy the same structural precision as other tiers.
- **Principles for solo/small-team contexts:** All sources assume organizational scale. How principles work when you're the only decision-maker -- and your "team" is AI agents -- is unexplored territory.
- **Relationship to documentation artifacts:** Harmel-Law's ADR model and Larson's strategy-doc model partially address this, but a comprehensive mapping of conceptual tiers to document types (specs, ADRs, design docs, spikes) across the full hierarchy remains incomplete.
- **Writing-as-influence in agentic contexts:** All three new sources assume human writers and human readers. How the dynamics change when agents produce the written artifacts -- and when the "advice process" involves agent-to-human or agent-to-agent communication -- is uncharted territory that swain directly explores.

## Related Troves

- `product-vision-frameworks` -- deep dive on vision specifically (7 sources on vision as a practice)
- `work-item-hierarchy` -- how PM tools implement initiative/epic/story (14 sources on tooling)
- `architecture-intent-evidence-loop` -- the loop framing that connects intent to execution to evidence
