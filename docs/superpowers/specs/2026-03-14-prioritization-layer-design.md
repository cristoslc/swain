# Prioritization Layer for Swain

## Problem

Swain presents a flat decision surface with no hierarchy, vision anchoring, or strategic context. An operator managing 10+ concurrent projects sees a wall of equally-weighted items — epics, spikes, specs all flattened together — with no way to determine which decisions best serve the project's vision(s).

The system answers "what's actionable?" but not "what matters most for where this project is going?"

### Specific gaps

1. **No priority at the artifact level** — all actionable items appear equal
2. **No vision connection** — decisions aren't framed in terms of which vision they advance
3. **Missing hierarchy layer** — everything is either a Vision (too strategic) or an Epic (too tactical), with no grouping for strategic focus areas
4. **No small work pipeline** — bugs, minor enhancements, and chores require full epic ceremony
5. **No attention tracking** — no way to detect that the operator is drifting from stated priorities
6. **No steering support** — no mechanism for the operator to declare focus or see peripheral accumulation

## Design

### Work Hierarchy

A new **Initiative** layer sits between Vision and Epic, representing a coordinated strategic focus. ("Initiative" is the working name — may be renamed later via mechanical find-and-replace.)

```
Vision           →  why does this product exist?
                    (has priority-weight: high / medium / low)

Initiative       →  what strategic focus are we pursuing?
                    (inherits vision weight, can override, groups epics)

Epic             →  what are we shipping?
                    (belongs to an initiative)

Spec             →  implementable unit
                    (belongs to an epic, OR directly to an initiative for small work)
```

**Small work path:** Specs can attach directly to an initiative without an epic parent. A bugfix tagged to a Security initiative shows up in the priority model, gets the initiative's weight, and goes straight to implementation without needing an epic wrapper. If small work clusters, the operator promotes it to a proper epic.

### Vision Weight Model

Visions get a `priority-weight` field in their frontmatter:

```yaml
priority-weight: high    # active strategic focus
priority-weight: medium  # maintained, progressing
priority-weight: low     # parked, not abandoned
```

Numeric scores behind the scenes (high=3, medium=2, low=1) for computation, but the operator only sees the labels.

**Defaults:** If no weight is set, visions default to `medium`. With no configuration, the system falls back to pure leverage-based ranking (decision debt + unblock count). Zero setup cost to get value.

**Weight cascade:** Vision weight flows down to its initiatives. An initiative can override its vision's weight (e.g., a low-priority initiative under a high-priority vision for work being deliberately parked).

**Vision-to-vision relationships:** No explicit hierarchy between visions. The "master plan" emerges from the attention pattern, not from structural nesting. Visions can link to each other via `linked-artifacts` — informational, not computational.

### Orphan Handling

Artifacts without proper parents are flagged as decisions in swain-status, ranked alongside all other decisions:

- **Epic without an initiative** → "Assign EPIC-017 to an initiative"
- **Initiative without a vision** → "Attach initiative to a vision"
- **Spec without an epic or initiative** → "Where does this belong?"

These are not auto-assigned or silently bucketed. Each is a decision the operator needs to make.

### Recommendation Signals

Three signals feed the recommendation engine. No velocity metrics, no sprint tracking, no health scores.

**1. Decision Debt**

Count of decisions waiting on the operator, per vision and per initiative. Weighted by downstream unblock count (already computed by specgraph).

Example: "Security has 3 pending decisions that would unblock 7 specs. Design has 1 that would unblock 2."

**2. Attention Drift**

Compares vision weights (what the operator said matters) against where they've actually been engaging (artifact transitions, decisions made, specs completed).

**Data source:** Git commit history, not manual frontmatter timestamps. Each commit that touches an artifact file (phase transition, creation, completion) is attributed to the artifact's vision via the parent chain. This is reliable (every meaningful change produces a commit), automated (no manual timestamp maintenance), and retrospective (can recompute from history at any time). When an artifact has no vision ancestor (orphan), its commits go into an "unaligned" bucket.

**Sparse data:** In new projects or visions with little history, drift is not reported. Attention drift only surfaces after a minimum activity threshold (5+ artifact transitions across the project, configurable via `prioritization.minActivityThreshold` in `swain.settings.json`) to avoid noisy signals from small sample sizes.

Not a judgment — a mirror. "You weighted security high but your last 8 decisions were all in design tooling."

**3. Leverage**

Which single decision has the highest unblock count? Already computed by specgraph. Tiebreaker: prefer decisions in higher-weighted visions.

**How they compose into a recommendation:**

The ranking function scores each actionable decision:

```
score = unblock_count × vision_weight
```

Where `vision_weight` is the numeric value (high=3, medium=2, low=1) inherited from the decision's vision via initiative. When a focus lane is set, only decisions within that lane are scored; peripheral lanes are summarized separately.

Tiebreakers, applied in order:
1. Higher decision debt in the decision's vision (prefer decisions in lanes with more accumulating work)
2. Decision-type artifacts over implementation-type (human-gated decisions are more valuable to unblock than agent-executable tasks)
3. Artifact ID (deterministic fallback)

The output is a sentence, not a score. Swain picks the top-ranked decision and frames it with context:

Example: "Activate EPIC-017 (Security Scanning). Security is weighted high with 3 pending decisions, but your last 2 weeks of work has been in design tooling."

If there is attention drift (see below), it is appended as context, not used to change the ranking. The operator decides whether to redirect — swain surfaces the information.

### Steering: Focus Lane + Peripheral Awareness

The operator decides whether to go breadth-first (address highest debt wherever it is) or depth-first (finish one lane before switching). Swain doesn't make this choice — it surfaces the tradeoff.

**Focus lane (optional, operator-set):**
- Operator declares "I'm focused on security right now"
- Swain recommends within that lane, doesn't nag about other lanes
- Peripheral awareness: "Design has 4 pending decisions (you weighted it medium)" — a mirror, not a redirect
- Focus lane persists in swain-session state as a vision ID or initiative ID (either granularity — "focused on the Security vision" or "focused on the Hardening initiative")

**No focus set (default):**
- Swain shows decision debt per vision, sorted by weight
- Recommends the highest-leverage single decision across all lanes
- Operator picks a lane or picks the recommendation — their call

### Two Operating Modes

**Vision mode — "right thing built":**
- Operator is steering strategy
- Shows: vision weights, decision debt per lane, focus lane, peripheral awareness
- Recommendation: highest-leverage strategic decision (activate this epic, begin this spike, approve this ADR)
- After deciding: operator kicks off agents, walks away
- Artifacts in scope: visions, initiatives, epics, spikes, ADRs

**Detail mode — "thing built right":**
- Operator is reviewing agent output
- Shows: specs within the active direction, what's been implemented, what needs review
- Recommendation: which spec most needs architectural review or has drifted from its parent epic's intent
- Artifacts in scope: specs, implementation plans, code

**Mode inference:** swain-status evaluates rules in priority order (first match wins):
1. Specs awaiting operator review (agent finished, needs sign-off) → detail mode
2. Focus lane set with pending strategic decisions → vision mode within that lane
3. No specs in review, decisions piling up → vision mode
4. Both specs in review AND strategic decisions pending → ask: "Steering or reviewing?"
5. Nothing actionable in either mode → vision mode (show the master plan mirror)

Once the operator answers, swain remembers for the session (via swain-session bookmark) so it doesn't ask again on the next status check.

**Shipping mode** (future — not in this design): a third lens focused on "what's the highest-leverage to getting the right thing out the door?"

### Emergent Master Plan

The master plan is not a document — it's a pattern swain observes and reflects back to the operator.

**What it is:** A snapshot of where attention has actually gone, mapped against stated vision weights. Computed from decisions made, specs completed, and focus lane history.

**Example output:**
```
Over the last 30 days:
  Security (weight: high)         — 2 decisions, 1 spec completed
  Design tooling (weight: medium) — 11 decisions, 6 specs completed
  Session mgmt (weight: low)      — 0 decisions

Your stated priorities and actual work are diverging.
```

**Periodic review triggers:**
- **Drift threshold:** A high-weight vision with zero artifact transitions for 14+ days, or a medium-weight vision with zero transitions for 28+ days. Low-weight visions do not trigger drift alerts (they are explicitly parked). These thresholds are configurable via `swain.settings.json` under `prioritization.driftThresholds`.
- **Initiative completion:** When an initiative's last epic reaches Complete (natural reflection point)
- **Operator request:** "how's the master plan looking?" or `swain-status --review`

The review is a prompt, not a report: "Your attention has drifted from security. Is that intentional, or should we course-correct?" The operator looks at the mirror, decides if the pattern is right, and adjusts vision weights or focus lane if needed.

### Integration Points

**New artifact type: Initiative**
- Managed by swain-design, with lifecycle phases like epics
- Frontmatter: `parent-vision`, `priority-weight` (optional override)
- Templates and phase transitions added to swain-design

**Artifact frontmatter changes:**
- Vision: add `priority-weight: high / medium / low`
- Epic: `parent-initiative` replaces `parent-vision`. Epics no longer point directly to visions — they reach their vision through the initiative chain. Migration converts existing `parent-vision` references to `parent-initiative` references (after initiatives are created in the migration step). During the migration period, specgraph accepts both fields and resolves the vision ancestor through whichever path exists.
- Spec: `parent-epic` remains the primary field. For small work without an epic, `parent-initiative` is used instead. A spec has exactly one of `parent-epic` or `parent-initiative`, never both — specgraph's xref validation rejects specs that populate both fields. Specgraph is updated to accept `parent-initiative` as a valid alternative to `parent-epic` on specs.

**specgraph changes:**
- Parse initiative layer into dependency graph (new parent-edge type: `parent-initiative`)
- Compute decision debt per vision and per initiative (count of ready items, weighted by unblock count)
- Expose decision debt and leverage as queryable signals for swain-status

**Attention tracking (new component):**
Attention distribution is not a specgraph feature — it requires temporal data that specgraph (a static graph parser) does not have. A new lightweight module computes attention from `git log`:
- Scans commits for artifact file changes (creation, phase transitions, completions)
- Attributes each change to a vision via the artifact's parent chain
- Aggregates into a per-vision activity summary over a configurable window (default: 30 days)
- Output: `{ vision_id: { decisions: N, completions: N, last_activity: date } }`
- Called by swain-status when rendering the recommendation and by the periodic review trigger
- No persistent state — recomputed from git history on each invocation (fast: just a `git log --name-only` scan filtered to artifact directories)

**swain-status changes:**
- Mode inference (vision / detail / ask)
- Focus lane awareness (from session state)
- Recommendation rewritten: leverage + decision debt + attention drift
- Peripheral awareness section for non-focus lanes
- Orphan flagging (epics without initiatives, initiatives without visions)
- Periodic review trigger when drift threshold exceeded

**swain-session changes:**
- Store focus lane in session state
- Store current mode (after inference or operator answer)
- Persist across status checks within a session

**Unchanged:** tk for task tracking, spec/epic lifecycle phases, ADR/Spike/Persona/Journey/Runbook/Design artifacts, swain-dispatch, swain-sync, swain-release, swain-do.

### Migration for Existing Projects

When swain-doctor detects a project without initiatives (epics parenting directly to visions, or orphaned), it enters a guided triage using the same decision support machinery:

1. **Scan** — identify all epics, group by `parent-vision` (or flag as orphaned)
2. **Propose clusters** — suggest initiative groupings based on epic titles, descriptions, and shared dependencies. This is an LLM-driven inference step: the agent analyzes epic descriptions and proposes thematic clusters. The operator reviews and adjusts — proposals are suggestions, not commitments.
3. **Operator decides** — approve, adjust, or reject each proposed cluster (surfaced as a standard decision in swain-status)
4. **Scaffold** — swain-design creates approved initiative artifacts, re-parents epics, sets default vision weights to `medium`
5. **Operator sets weights** — prompted once to assign vision weights (can defer — everything stays `medium`)

**Migration principles:**
- Incremental — adopt the initiative layer for one vision, leave others flat
- Orphaned epics flagged as decisions, not auto-assigned
- Projects without visions get a gentle prompt, not a blocker — system degrades gracefully to pure leverage-based ranking
- swain-doctor checks on session start, prompts once per session

## Out of Scope

- **Shipping mode** — third operating lens focused on delivery. Deferred to round 2.
- **Cross-project prioritization** — ranking decisions across multiple swain projects. Future work.
- **Drift detection** (semantic) — whether work content matches vision intent. Too subjective to automate; belongs in periodic review, not computation.
- **Quality signals** — whether specs are well-written or code is good. That's detail mode's domain, not the prioritization layer.
- **Initiative naming** — "Initiative" is the working name. If renamed later, it's a mechanical find-and-replace across templates, frontmatter fields, and documentation.

## Success Criteria

1. Operator can set vision weights and see recommendations change accordingly
2. swain-status shows one recommendation anchored to vision context, with enough information to redirect
3. Orphaned artifacts are flagged as decisions, not silently deprioritized
4. Small work (bugs, minor enhancements) can enter the priority model without epic ceremony
5. Given a high-weight vision with no artifact transitions in 14+ days, swain-status displays the attention drift signal
6. Focus lane filters recommendations without hiding peripheral debt accumulation
7. Existing projects can migrate incrementally without breaking current workflows
8. Zero configuration still produces useful recommendations (defaults to leverage-based ranking)
