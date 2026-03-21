# Synthesis: Product Management on the AI Exponential

## Theme 1: The PM role is shifting from orchestrator to builder

Multiple sources converge on the same observation: AI tools are transforming product managers from coordinators who write specs for others to execute into individual contributors who can prototype, test, and validate independently.

- **Cat Wu** (claude-blog-pm-ai-exponential) describes a three-tool workflow (Claude.ai / Claude Code / Cowork) where PMs go from idea to working prototype in an afternoon. At Anthropic, "designers ship code, engineers make product decisions, product managers build prototypes and evals."
- **Fabio Piazza** (medium-ai-powered-pm-orchestrator-to-creator) frames this as "orchestrator to creator" — AI is a force multiplier enabling PMs to design, build, and validate at speeds previously unimaginable. But warns: "Are we creating better products, or just more products?"
- **AutonomyAI** (autonomyai-pm-product-builders) coins "Product Builder" — a PM who can define, prototype, launch, and measure experiments independently. Argues PRDs are "no longer the central artifact of product velocity."
- **Pendo** (pendo-every-pm-ai-pm) observes the feedback loop: the more PMs use AI in their own work, the more they develop intuition for what's useful and broken — making them better at building AI features for users.

## Theme 2: Documentation is dying — or evolving

A sharp tension emerges across sources about whether documentation (PRDs, specs, ADRs) is becoming obsolete or more important than ever.

### The "docs are dying" camp

- **Cat Wu** advocates "demos and evals over docs" — Anthropic replaced documentation-first thinking with prototype-first thinking. "After you write a spec, send it to Claude Code and see if it can build it."
- **AutonomyAI** argues short hypothesis documents plus rapid experiments outperform long predictive specifications. The old model (Think, Plan, Build, Launch) is giving way to Build, Launch, Learn, Repeat.
- **Vibe Coding Debt** (techchampion-vibe-coding-debt) observes that developers feel less inclined to document when "the AI knows" — creating a knowledge vacuum where the "why" behind decisions is lost.

### The "docs are more important than ever" camp

- **ThoughtWorks** (thoughtworks-spec-driven-dev) argues vibe coding is "too fast, spontaneous and haphazard" and that spec-driven development brings back necessary requirements analysis and architectural constraints. A specification is "more than just a PRD" — it defines external behavior, not just business requirements.
- **Faisal Feroz** (gopubby-agents-md-new-adr) makes the strongest case: documentation isn't dying, it's *shifting audience* from humans to AI agents. AGENTS.md is "active" documentation — consulted on every AI coding session — while traditional docs were "passive" artifacts that people might or might not read.
- The key insight: **ADRs answer "what did we decide?" while AGENTS.md answers "what must be true?"** One is historical. The other is operational.

## Theme 3: The exponential model improvement changes the calculus

- **Cat Wu** provides the anchor data point: METR shows a 41x jump in task complexity (21 minutes to ~12 hours human-equivalent) in 16 months. This breaks the PM assumption that technological constraints remain stable during a project.
- **Cat Wu** also articulates the "do the simple thing" principle: workarounds for model limitations become unnecessary complexity when the next model drops. Anthropic cut 20% of their system prompt for Opus 4.6 because behaviors that required prompting now come for free.
- **AI PM Tools** (aipmtools-future-ai-pm-2026-2030) quantifies this in the tooling landscape: only ~25% of PM tools have meaningful agentic capabilities, but this is the dimension with the most room for rapid improvement. By 2028, agentic capabilities will be table stakes.

## Theme 4: The risks of moving too fast

Several sources raise red flags:

- **Piazza** warns about "feature validation vs problem validation" — the ease of prototyping may cause teams to validate solutions for problems users don't actually have.
- **Vibe Coding Debt** warns about locality bias (AI optimizes locally, breaks globally), the 75% higher error rate in AI-assisted PRs, and the open-source maintenance crisis (consumers stop understanding libraries).
- **ThoughtWorks** notes spec drift and hallucination are "inherently difficult to avoid" — deterministic CI/CD practices are still needed.
- **AutonomyAI** identifies why "empowered PM" initiatives fail: still dependent on engineering backlogs, fragmented tools, experimentation gated by process.

## Theme 5: What documentation *should* look like in the AI era

Across sources, a new shape for documentation emerges:

| Old Artifact | New Artifact | Key Difference |
|---|---|---|
| PRD (long, predictive) | Experiment brief (1-page hypothesis) | Optimized for learning speed, not prediction |
| ADR (historical, passive) | AGENTS.md (operational, active) | Consumed by AI agents, not just humans |
| Detailed roadmap | Short sprints + side quests | Adapts to model capability changes |
| Stand-up docs | Demos and evals | Tangible artifacts replace written updates |
| Formal specs | Structured prompts / spec-driven dev | Machine-readable, drives code generation |

## Gaps

- **No source directly addresses the swain question**: how a documentation-artifact system (Visions, Epics, Specs, ADRs) fits when the industry is debating whether docs should even exist. The tension between swain's artifact-centric model and the "prototype-first" movement is the central unresolved question.
- **Missing: the "documentation for AI agents" angle applied to product planning artifacts**, not just code-level constraints. AGENTS.md handles code architecture — what handles product architecture decisions for AI-augmented teams?
- **No voice from regulated industries** where documentation is mandatory (healthcare, finance, government) and the "just prototype it" approach hits compliance walls.
- **Missing: empirical data on documentation ROI** — does documented decision-making actually produce better outcomes than rapid prototyping, or is it cargo-culting an era of scarce engineering capacity?
- **The open-source knowledge crisis** raised by the vibe coding debt article deserves deeper exploration — if AI consumes but doesn't replenish the knowledge base, what happens to the quality of AI-generated code over time?
