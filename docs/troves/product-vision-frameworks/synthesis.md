# Product Vision Frameworks: Trove Synthesis

## What Is a Vision?

The sources converge on one definition: **a vision describes a desired future state** — not what the product does today, but where it's going and what the world looks like when it gets there.

Key distinction from every source: a vision is NOT a mission (purpose/why), NOT a strategy (how to get there), NOT a roadmap (what to build next). These are separate levels in a hierarchy.

## The Hierarchy (Sources Agree)

| Level | What it answers | Timeframe | Stability |
|---|---|---|---|
| **Purpose/Mission** | Why do we exist? | Indefinite | Rarely changes |
| **Vision** | What future state are we building toward? | 2-5 years (Cagan), 5+ years (Pichler) | Stable for years |
| **Strategy** | What problems do we solve to get there? | Annual/quarterly | Changes regularly |
| **Tactics/Roadmap** | What do we build next? | Weeks/months | Changes constantly |

Cagan: "Stubborn on the vision, flexible on the details."
Pichler: Vision and strategy should be "loosely coupled."

## What Makes a Good Vision

### Pichler's Six Criteria (most structured test)
1. **Inspiring** — resonates emotionally
2. **Shared** — people genuinely support it
3. **Ethical** — does no harm
4. **Concise** — memorable, can be stated in one sentence
5. **Ambitious** — possibly never fully achieved
6. **Enduring** — provides guidance for 5+ years

### Cagan's Characteristics
- Customer-centric (focuses on user impact, not features)
- Compelling and persuasive (not a specification)
- Not overly detailed or prescriptive
- Emotionally resonant
- Single and unifying across all teams

### Bassino's Four Attributes
- Customer-centric
- Inspirational
- Differentiated
- Stretch but attainable (3-5 year horizon)

## Two Schools of Vision Format

### School 1: Strategic Positioning (Geoffrey Moore)
"For [target customer] who [problem], our product is a [category] that [key benefit]. Unlike [alternative], our product [differentiation]."

- Forces specificity
- Good for market positioning
- **Limitation:** describes WHO and HOW, not WHY or WHERE

### School 2: Aspirational Goal (Pichler, Cagan)
A concise statement of the desired future state. Example: "HEALTHY EATING" for a diabetes management app.

- Captures the ultimate purpose
- Stable while strategy evolves
- **Preferred by most sources** because it separates vision from strategy

## Common Mistakes

1. **Confusing vision with mission** — mission is WHY you exist; vision is WHERE you're going (Cagan)
2. **Confusing vision with roadmap** — 1-year horizons are roadmaps, not visions (Cagan FAQ)
3. **Multiple competing visions** — "everyone picking out their own star from the sky" (Cagan)
4. **Generic platitudes** — "be more innovative" gives no direction (SAFe)
5. **Template worship** — forcing equal emphasis on irrelevant sections (Bassino)
6. **Premature abandonment** — giving up after 6-12 months without proper discovery (Cagan FAQ)

## The Vision Test Battery

Synthesizing across sources, a well-formed vision passes ALL of these:

1. **The Elevator Test** (Moore/Fowler): Can you explain it in 2 minutes?
2. **The Sorting Test**: Given a proposed initiative, can you quickly tell whether it advances this vision or not?
3. **The Stability Test** (Pichler): Would this still be the vision if you pivoted your strategy completely?
4. **The Inspiration Test** (Cagan): Does it make talented people want to help make it real?
5. **The Specificity Test** (SAFe): Is it specific enough to guide prioritization, or could any company claim it?
6. **The Concision Test** (Pichler): Can you state it in one sentence that anyone can paraphrase from memory?

## What Are Product Principles?

A concept distinct from both vision and strategy, identified by Cagan and formalized by Amazon as "tenets."

### Cagan's Definition

Product principles "complement the product vision and strategy by outlining the core beliefs and values guiding the development of a product or product line." They speak to the **nature** of the products, not features or releases. Cagan notes they are "often lumped together and just referred to as 'the product vision'" — created alongside the vision as part of the same exercise.

**The eBay example:** Despite revenue coming from sellers, eBay established the principle "In cases where the needs of buyers and sellers conflict, we will prioritize the needs of the buyer." This resolved a recurring tension, was counterintuitive, and guided decisions without prescribing features.

### Amazon's Tenets

Amazon formalizes principles as "tenets" — "carefully articulated guiding principles for any endeavor that act as a guide to align on a vision and simplify decision-making."

**Two types of tenets:**
- **Foundational** — describe why the team/product exists (present reality)
- **Aspirational** — describe how the team intends to operate, even if not currently doing so (future intent)

This distinction is critical: **Amazon explicitly allows principles that aren't yet true.** An aspirational tenet is a statement of intended behavior that guides decisions even before the infrastructure to enforce it exists.

**Key characteristics of good tenets (Kindel):**
1. Be endeavor-specific — generic tenets communicate no useful information
2. Counsel, don't prescribe — guide through trade-offs, take a stand that one thing matters more
3. One main idea per tenet
4. Present tense — "will" or "should" is almost always a mistake
5. Distinguish rather than elevate — what makes you different, not superior
6. "Unless you know better ones" — tenets evolve

**Key insight for swain:** A charter describes WHAT a team does; tenets describe HOW they do it. The purpose describes WHY; the vision describes WHERE. Tenets are orthogonal to both — they constrain all work at every level.

### Where Principles Sit in the Hierarchy

Principles are NOT a level in the Purpose → Vision → Strategy → Tactics hierarchy. They are **orthogonal constraints** that cut across all levels:

| Level | What it answers | Constrained by principles? |
|---|---|---|
| Purpose | Why do we exist? | No — purpose defines principles |
| Vision | What future state? | Yes — visions must be consistent with principles |
| Strategy | What problems to solve? | Yes — strategy operates within principles |
| Tactics | What to build? | Yes — every tactic must respect principles |

Principles flow FROM purpose and constrain everything downstream. They don't compete with visions for position in the hierarchy — they operate on a different axis entirely.

### Foundational vs. Aspirational: The Dual Nature

Amazon's foundational/aspirational distinction resolves a key confusion in swain's current restructuring:

Some statements are **foundational principles** (already true, constrain all work):
- "Artifacts are the single source of truth"
- "Git is the persistence layer"
- "Intent and evidence are separate things"

Some are **aspirational tenets** (not yet fully true, but guide decisions as if they were):
- "Process compliance is enforced" — guides decisions today even though enforcement is incomplete
- "Unattended execution is safe" — guides decisions today even though the sandbox isn't built on all platforms
- "Swain works where you do" — guides decisions today even though runtime portability is partial

Aspirational tenets are NOT visions. They don't describe a future state to invest toward — they describe a present-tense behavioral guide. "We enforce process compliance" is how we make decisions NOW, even when the infrastructure is incomplete. The VISION would be the experience that results: "Never Overwhelm the Operator" or "The Agent Always Recaps Its Work."

## Relevance to Swain

Swain's context is unusual: it's a personal tool with one user, not a product team. This changes several assumptions:

- **"Shared" criterion** (Pichler #2) — the vision doesn't need organizational buy-in, but it does need to be legible to agents (the "team" in this context)
- **"Inspiring"** — in a solo context, inspiration means "does this help me decide what to work on next?" not "does this recruit talent?"
- **"Customer-centric"** — the operator IS the customer. The vision should describe the operator's future experience.
- **The Sorting Test is the most important** — with 68+ artifacts, the vision's primary job is organizing work, not inspiring missionaries

The frameworks suggest visions should be **concise future states that organize work and remain stable while strategy evolves**. For swain, that means each vision should be a sentence describing what the operator's experience looks like when the capability exists — not what we're building, not how we're building it, not why we're building it (that's PURPOSE.md).

### The Three Axes for Swain

Synthesizing all sources, swain needs three distinct categories:

1. **Purpose** (PURPOSE.md) — why swain exists, the alignment loop, who it's for. Changes = different project.
2. **Principles/Tenets** (PURPOSE.md or separate) — both foundational (already true) and aspirational (guide decisions before fully realized). Orthogonal to visions. Present tense. "Unless you know better ones."
3. **Visions** (VISION-NNN artifacts) — future operator experiences to invest toward. Organize work. May never be fully achieved.

Work items advance visions while respecting principles. Some infrastructure work exists specifically to make aspirational tenets more enforceable — that work can be organized under the vision whose experience it enables, or left as principle-infrastructure.

## Related Troves
- `architecture-intent-evidence-loop` — the loop framing that motivated this vision restructuring
- `work-item-hierarchy` — how artifacts relate in swain's system
