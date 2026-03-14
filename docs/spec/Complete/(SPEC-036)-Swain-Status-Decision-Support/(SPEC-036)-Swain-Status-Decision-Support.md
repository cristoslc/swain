---
title: "swain-status Decision Support"
artifact: SPEC-036
track: implementable
status: Complete
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
type: enhancement
parent-epic: EPIC-014
linked-artifacts:
  - SPIKE-018
  - JOURNEY-001
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# swain-status Decision Support

## Problem Statement

JOURNEY-001 (§ O-01) defined this requirement explicitly: add a dedicated "Decisions waiting on you" section that is the developer's **primary entry point** — answer "what's waiting on me?" before showing anything else. It also defined the two-bucket structure: **Decision backlog** (requires human judgment) before **Implementation backlog** (agent-delegatable).

That structure was never implemented in `agent-summary-template.md`. The current template leads with **Epic Progress** — an inventory view that is neither bucket. The operator must read the entire output and extract their own decision from it.

The result is state-snapshotting without decision support. The suggestions at the bottom feel low-priority because they appear after all the data, and listing multiple options is equivalent to listing none.

## External Behavior

### Input

The existing swain-status invocation — no new flags required.

### Output changes

The agent summary (what the operator reads, not the terminal OSC 8 output) restructures around a single leading recommendation:

**Before (current):**
```
## Epic Progress
[full table]

## Research (Spikes)
[table]

## Blocked
[list]

## Follow-up
- Option A
- Option B
```

**After (this spec) — two-bucket layout from JOURNEY-001 § O-01:**
```
## Recommendation
**Action:** Approve SPEC-030
**Why:** It is the gate for EPIC-013 — approving it unblocks SPEC-031, SPEC-032, and
SPEC-033 in one move (highest downstream leverage among all actionable items).

## Decisions Needed  ← human-owned bucket, shown first
[artifacts requiring human judgment, sorted by unblock_count descending]

## Work Ready to Start  ← agent-owned bucket, shown second
[implementation-ready items the agent can execute autonomously]

## Epic Progress / Research / Blocked / Issues
[reference data — shown after the two action buckets]
```

The primary fix is to `agent-summary-template.md`: it currently leads with Epic Progress (inventory) and has no two-bucket structure. This spec corrects that.

### Specific behavioral changes

1. **Lead with one recommendation.** The first section of the agent summary is always `## Recommendation` — one action, one reason. The reason must include the downstream impact (how many artifacts unblock, which epic activates, etc.), not just the dependency name.

2. **Rank ready items by unblock count.** The status script already emits `unblocks: [...]` arrays in the cache JSON. The agent summary must use this to rank and should name only the top item, not list all of them.

3. **Inline transition prompts.** Active epics with `progress.done == progress.total` (all specs resolved) must show a `→ ready to close` note in the Readiness column, not appear as "work on child specs." This was surfaced manually by the operator in the session that produced this spec; it should be automatic.

4. **Blocked items state cost, not just dependency.** Instead of "SPEC-031 blocked on SPEC-030", the blocked section should read "SPEC-031, SPEC-032, SPEC-033 — all blocked on SPEC-030 (actionable now)." The grouping and the "actionable now" qualifier matter.

5. **Suppress fully-resolved active epics from the Implementation section.** An epic with all specs done should not appear as "work on child specs" — it clutters actionable signal.

### Files changed

- `.claude/skills/swain-status/references/agent-summary-template.md` — add `## Recommendation` section definition, update Follow-up section to be singular and leading
- `.claude/skills/swain-status/SKILL.md` — update follow-up instructions to require single ranked recommendation, not "offer one or two"
- `skills/swain-status/scripts/swain-status.sh` — expose `unblock_count` per ready artifact in the JSON cache so the agent has leverage data without needing to compute it

## Acceptance Criteria

1. **Given** swain-status runs with multiple actionable items, **When** the agent summary is presented, **Then** the first section is `## Recommendation` containing exactly one action and a leverage-based reason (not a list of options).

2. **Given** a ready artifact has `unblocks: [A, B, C]`, **When** the recommendation is selected, **Then** it names the unblock count and artifact IDs in the reason line.

3. **Given** an Active epic has `progress.done == progress.total`, **When** it appears in the Epic Progress table, **Then** its Readiness cell reads "ready to close" (not "work on child specs") and it does not appear in the Implementation section.

4. **Given** multiple specs are all blocked by the same artifact, **When** they appear in the Blocked section, **Then** they are grouped under a single entry that names the common blocker and states whether it is actionable now.

5. **Given** the status script is run, **When** the JSON cache is written, **Then** each ready artifact entry includes `unblock_count: N` alongside the existing `unblocks: [...]` array.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Single recommendation leads | Manual review of agent summary output | PASS |
| Leverage-based reason | Recommendation names unblock count | PASS |
| All-specs-done epic shows "ready to close" | EPIC-007/010 pattern reproduced in test run | PASS |
| Blocked items grouped by common blocker | SPEC-031/032/033 → SPEC-030 grouping | PASS |
| Cache includes unblock_count | `jq '.artifacts.ready[].unblock_count' cache.json` returns integers | PASS |

## Scope & Constraints

**In scope:**
- Agent summary template (`agent-summary-template.md`) restructuring
- SKILL.md follow-up instruction update
- Status script JSON cache: add `unblock_count` field to ready items

**Out of scope:**
- Changes to the terminal OSC 8 output (that goes to the terminal, not the operator's reading surface)
- Changing what data the script collects (only how the agent surfaces it)
- Ranking algorithm beyond unblock count (downstream depth, priority-weighted, etc. — future work)
- Compact/MOTD mode changes

## Implementation Approach

Three files, three independent changes — can be done in a single pass:

1. **`swain-status.sh`** — in the section that builds the `ready` array for the JSON cache, add `"unblock_count": (unblocks | length)` to each entry. One jq expression change.

2. **`agent-summary-template.md`** — prepend a `## Recommendation` section definition before the Epic Progress section. The section instructs the agent to: sort ready items by `unblock_count` descending, pick the top one, write one action sentence, write one leverage sentence naming count and IDs. Update the Follow-up section to reference the Recommendation section and be removed (the recommendation replaces it).

3. **`SKILL.md`** — update the follow-up table and the "offer one or two suggestions" instruction to instead say "lead with a single ranked recommendation in the `## Recommendation` section; the recommendation is the first thing the operator sees, not a footnote."

No test infrastructure changes needed — verification is by manual review of a fresh `swain-status` run against the acceptance criteria.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | 8e30b25 | Initial creation; motivated by operator feedback: "state-snapshotted, not decision-supported" |
| Ready | 2026-03-14 | b4037a0 | Batch approval — ADR compliance and alignment checks pass |
| Complete | 2026-03-14 | dacbf2c | Recommendation section, two-bucket layout, unblock_count in cache — all 5 ACs verified |
