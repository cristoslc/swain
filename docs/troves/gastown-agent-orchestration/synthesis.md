# Synthesis: Gas Town Agent Orchestration

## Key findings

Maggie Appleton reviews Steve Yegge's Gas Town — an agent orchestrator that runs dozens of coding agents at once. She frames it as speculative design fiction, not production tooling. The essay pulls four themes from the chaos.

**Design becomes the bottleneck.** When agents churn through code tasks at high speed, the limit shifts to deciding what to build. Product strategy, architecture, and taste are things agents cannot supply. Gas Town shows the failure mode: it was "vibe designed" — never planned up front. The result is a pile of overlapping, ad hoc concepts.

**Orchestration patterns are emerging.** Beneath the Mad Max theming, Gas Town sketches patterns that future systems will likely follow:

- Specialized agent roles with a clear chain of command (Mayor, Polecats, Witness, Refinery).
- Persistent identities and tasks stored in Git. Sessions are disposable.
- Work queues fed by a planning agent. Supervisors nudge idle workers.
- A dedicated merge agent that resolves conflicts or "re-imagines" changes. Stacked diffs fit better than traditional PRs.

**The economics work.** At $1-3k/month for a mature version, the cost is 10-30% of a US senior developer salary. If it gives 2-3x output, the math holds. Current costs ($2-5k/month) are inflated by waste.

**Code distance is contextual, not tribal.** How close developers should stay to code depends on domain, feedback loops, risk, greenfield vs brownfield, team size, and experience. Both the "purist" and "agentic maximalist" camps are wrong to treat this as identity.

## Points of agreement with existing troves

- **multi-agent-collision-vectors:** The merge queue pattern (Refinery) and stacked diffs match this trove's coverage of merge queues, bors, and Graphite.
- **agentic-control-loops:** The "nudging" heartbeat — supervisors poking workers to stay on task — is a variant of the loop patterns in this trove.
- **slop-creep:** The "vibe designed" footgun — moving so fast you skip thinking — is the same decay that slop-creep tracks.
- **agentic-coding-dual-modes:** The code-distance spectrum maps to the headless/headful mode axis.

## Points of disagreement

- None across sources (single-source trove).

## Gaps

- No first-hand testing of Gas Town by Appleton. Analysis is based on the manifesto and second-hand reports.
- No comparison to other orchestrators (e.g., OpenHands, Devon, Factory).
- Little coverage of security or compliance risks from fully autonomous agent fleets.
- Economic analysis uses US salary benchmarks only. Global numbers would shift the picture.
