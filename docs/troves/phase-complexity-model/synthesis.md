# Phase Complexity Model — Synthesis

## Key Findings

### Two-axis complexity scoring is well-established

The Stacey Matrix (1990s, Ralph Douglas Stacey) uses **agreement** (stakeholder consensus on goals) × **certainty** (predictability of cause-and-effect) to classify situations into five zones. All four sources converge on this being the foundational framework for mapping complexity to process decisions. The Praxis Framework maps these zones directly onto Cynefin domains, establishing a formal correspondence between the two models.

### Complexity-to-rigor mapping has direct precedent

PMI's graded approach explicitly scores project complexity (low/medium/high) and maps each level to **minimum required rigor** across 8 process areas: team formation, planning documentation, stakeholder communication, requirements management, acquisition planning, risk management, execution, and monitoring/controlling. This is the closest analog to what SPIKE-043 proposes for swain — scored complexity driving concrete ceremony decisions.

### Cynefin adds constraint-type awareness

Where Stacey provides a scorable 2D space, Cynefin provides a qualitative lens on what *kind* of automation is appropriate per domain:
- **Clear/Simple**: fully automatable — fixed constraints, known order
- **Complicated**: rules-based automation with expert judgment at decision points
- **Complex**: automate scaffolding (experiments, feedback loops) but not decisions
- **Chaotic**: alerting and stabilization only

This maps directly to swain's autonomy question: P1×S1 (Clear) → agent acts autonomously; P3×S3 (Complex) → agent automates the scaffolding but consults the operator for decisions.

### The off-diagonal cases are where value lives

All sources agree that the interesting cases are not the extremes. Stacey specifically identifies:
- **Zone 2** (far from agreement, close to certainty) → "decision making becomes political rather than technical" → in swain: the problem is clear but stakeholders disagree on scope → operator consultation needed even though implementation is straightforward
- **Zone 3** (close to agreement, far from certainty) → "head towards an agreed future state even though specific paths are not fully predetermined" → in swain: alignment exists on what to build, but implementation is exploratory → full ceremony to catch drift, but autonomy on day-to-day tasks

## Points of Agreement

1. **Two independent axes** are sufficient to classify most work into actionable buckets
2. **Process rigor should scale with complexity** — over-rigor wastes resources, under-rigor creates risk
3. **The quadrant determines the *type* of management**, not just the *amount* — Stacey's zones prescribe different skills (technical analysis vs. negotiation vs. creativity vs. crisis response)
4. **Classification can change over time** — AgilityPortal explicitly notes that Agile projects may shift quadrants, requiring continuous reassessment

## Points of Disagreement

1. **Stacey vs. Cynefin as primary model**: Stacey is scorable (continuous axes), Cynefin is categorical (discrete domains). For automated process selection, Stacey is more directly useful. Cynefin is better for the "what kind of automation" question.
2. **Subjectivity concern**: AgilityPortal notes the Stacey Matrix has a subjectivity problem — "varying levels of experience can lead to disparate assessments." This is less problematic for swain because we're scoring from frontmatter signals (objective) not human judgment.
3. **Haas (via PMI) vs. Stacey**: Haas distinguishes complicated from complex based on non-linear feedback loops, while Stacey uses agreement/certainty. For swain's purposes the distinction isn't critical — both produce the same recommended action (more ceremony for less predictable work).

## Gaps

1. **No existing framework addresses model selection** (opus vs. sonnet vs. haiku) — this is novel to LLM-based agents. The complexity-to-rigor mapping must be extended to include computational cost optimization.
2. **No framework addresses the "manual test vs. automated verification" gate** — PMI's graded approach covers monitoring rigor but doesn't distinguish human verification from automated testing.
3. **"Shines" methodology** — the original inspiration — was not findable as a public framework. The operator may have a proprietary source or a different name.
4. **Agent autonomy boundaries** are not addressed in any traditional framework — these are novel to AI agent systems. Cynefin's constraint types come closest but don't map directly to "when can the agent skip consulting the operator."
