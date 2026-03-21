# Session Decision Support — Synthesis

## The core problem: unbounded decision work degrades quality and never signals completion

Six research streams converge on a single design insight: an operator managing a project through swain is a **bounded cognitive agent** making sequential decisions under load, and the system currently does nothing to acknowledge or manage those bounds.

## Theme 1: Decision quality degrades with volume — cap the session

**Decision fatigue** (Baumeister's Strength Model) shows that sequential decision-making depletes executive function resources. Judges' favorable rulings drop from ~65% to near zero within a decision session, rebounding after breaks. Physicians prescribe unnecessary antibiotics at higher rates as the day progresses. The mechanism is disputed (ego depletion vs. attentional regulation shifts), but the behavioral outcome is consistent: **more decisions in sequence = worse decisions** (decision-fatigue-pmc).

**Working memory** holds ~4±1 items simultaneously (revised from Miller's 7±2). When total cognitive load exceeds working memory capacity, the system fails — decision-makers shift from analytical (System 2) to intuitive (System 1) processing, increasing bias susceptibility (cognitive-load-gcbs).

**Design implication:** Swain should propose a bounded decision budget per session. The literature doesn't provide a magic number, but the working memory constraint (~4 items) and the judge study (degradation within a single session block) suggest **3-5 substantive decisions per session** as a reasonable starting point. The budget should be a default the operator can override, not a hard gate.

## Theme 2: Clustering related decisions eliminates switching costs

**Task switching** imposes a measurable cognitive penalty: responses are slower and more error-prone after a switch, and preparation reduces but never eliminates the residual cost (~600ms minimum). Each shift requires the brain to reload context and adjust processing mode — this transition cost consumes cognitive resources without producing output (task-switching-monsell).

**Decision batching** exploits this: grouping related decisions lets the brain enter a specific problem-solving mode and stay there. Context switching between unrelated decisions is pure overhead (decision-batching-gcbs).

**Design implication:** Session goals should cluster decisions within a single initiative or focus area. Don't scatter the operator across INITIATIVE-005 and INITIATIVE-013 in the same session. The "focus lane" concept already exists — the session goal should be the bounded, coherent work *within* that lane.

## Theme 3: Specific, bounded goals drive performance — vague ones don't

**Locke & Latham's goal-setting theory** (400 studies, 40,000+ participants) shows specific, difficult goals produce performance 250% higher than easy goals, with meta-analysis effect sizes of .42-.80. Goals serve a **directive function**: they focus attention on goal-relevant activities and away from irrelevant ones. But when goals exceed ability limits, performance drops — the sweet spot is challenging but attainable (goal-setting-locke-latham).

**Design implication:** "Work on INITIATIVE-005" is a vague goal. "Activate or drop the 3 Proposed specs under INITIATIVE-005" is a specific, bounded goal with clear completion criteria. Swain should generate session goals in the second form: specific decisions, enumerated, with a clear "done" state.

## Theme 4: Completion signals relieve cognitive tension — their absence is harmful

**The Zeigarnik effect** demonstrates that unfinished tasks create persistent cognitive tension, with ~1.9x recall of interrupted vs. completed tasks. Starting a task establishes tension (Lewin's field theory) that persists until completion. Progress bars exploit this: showing incomplete state maintains tension and drives completion (zeigarnik-effect).

**The flip side is the walk-away signal.** If swain never says "you're done for this session," the operator carries the cognitive weight of all open work. The strategic backlog is unbounded by design — it will never be empty. Without explicit session-level closure, the operator experiences the Zeigarnik effect on the *entire project*, not just the current task.

**Design implication:** Swain needs two completion signals:
1. **Session goal complete** — "You've made your 4 decisions for this session. INITIATIVE-005 has no more pending operator decisions. Here's what changed." This relieves session-level tension.
2. **No decisions needed** — when the roadmap has zero items requiring operator input, say so explicitly. The absence of a decisions section reads as "I forgot to check," not "you're clear."

## Points of agreement across sources

All sources agree that:
- Cognitive resources for decision-making are finite and depletable
- Sequential decisions within a session degrade in quality
- Clustering related work reduces overhead
- Specific goals outperform vague ones
- Completion signals are psychologically necessary

## Points of disagreement

- The **ego depletion mechanism** is disputed — Baumeister's resource model vs. the Process Model's attentional/motivational account. Both predict the same behavioral outcome for our purposes.
- **No consensus on optimal decision count.** Working memory (~4 items) and session degradation studies suggest a small number, but no study provides a validated threshold for project management decisions specifically.

## Gaps

- No research specifically on **AI-assisted decision support** and whether the AI framing decisions (vs. the human discovering them) changes the fatigue curve.
- No research on **decision complexity weighting** — a "activate or drop" decision is lighter than a "choose between three architectural approaches" decision. A flat count may be too crude.
- No research on **cumulative session effects** — does a good closure signal in session N improve decision quality in session N+1?

## Design model for swain

```
SESSION START
  ├── Refresh ROADMAP.md (strategic view)
  ├── Detect focus lane (or suggest one)
  ├── Generate SESSION-ROADMAP.md:
  │     ├── Decisions section (operator-required, clustered by focus)
  │     ├── Recommended Next (highest-leverage item)
  │     ├── Session Goal (specific, bounded, ~3-5 decisions)
  │     └── Progress section (what changed since last session)
  │
  ├── Operator works (decisions + implementation delegation)
  │
  └── SESSION END / BUDGET REACHED
        ├── "Session goal complete" or "N/M decisions made"
        ├── Summary of what changed
        └── Walk-away signal: "No more decisions needed right now"
              or "Remaining decisions deferred to next session"
```
