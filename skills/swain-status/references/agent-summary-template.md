# Agent Summary Template

After running the status script, present a structured summary using these tables.
The script's terminal output goes to the terminal with OSC 8 hyperlinks; this
summary is what the user actually reads for decision-making.

Do NOT just dump bullet lists. Use tables so the user can scan and compare.

Lead with decisions and actions — answer "what's waiting on me?" before showing
anything else. Reference data (Epic Progress, Spikes, Blocked) comes after.

## Section 1: Session Context

Read `.session.bookmark` from the JSON cache. If the bookmark exists and has a
non-null `note`, show it as a one-line orientation header before the recommendation:

> **Resuming:** {note}

If the bookmark has `files`, list them on the next line as clickable paths.

This tells the operator where they left off. It's context, not a recommendation —
the recommendation section follows and may suggest continuing that work or
pivoting elsewhere.

Omit this section entirely if no bookmark exists or the note is null/empty.

## Section 2: Recommendation

Read `.priority.recommendations[0]` from the JSON cache. Write exactly two sentences:

- **Action:** One sentence naming the action (e.g., "Activate EPIC-017.")
- **Why:** One sentence naming the score, vision context, and unblock count (e.g., "Security is weighted high with 3 pending decisions — activating this unblocks EPIC-023. Note: your last 2 weeks of work has been in design tooling.")

Include attention drift context if any drift is detected for the recommendation's vision (check `.priority.drift`).

Omit this section entirely if no ready items exist.

**Drift prompt:** If `.priority.drift` is non-empty, include a drift prompt after the recommendation:
"Your attention has drifted from [Vision Name] (weight: [W]) — [N] days since last activity. Is that intentional, or should we course-correct?"

This is not a recommendation to change — it's a mirror. The operator decides.

## Section 3: Peripheral Awareness

If a focus lane is set (`.session.focus_lane` is non-null) and there are decisions in other visions, summarize:
"Meanwhile: [Vision Name] has N pending decisions (weight: W)"

One line per non-focus vision with pending decisions from `.priority.decision_debt`.
Omit this section entirely if no focus lane is set.

## Section 4: Decisions Needed

Artifacts requiring human judgment, sorted by unblock_count descending so
highest-leverage decisions appear first. Includes:

- Proposed/Draft specs needing review
- Proposed ADRs needing acceptance
- Proposed spikes needing activation
- For the full type/phase classification (including VISION, JOURNEY, EPIC in Proposed state, PERSONA, DESIGN), see the `is_decision` definition in SKILL.md.

```
| Artifact | What's Needed | Unblocks |
|----------|--------------|----------|
| **TYPE-NNN**: Title | review and approve / review and decide / activate | SPEC-NNN, ... or — |
```

Rules:
- Sort by unblock count descending (highest first)
- "What's Needed" = the human action required (approve, decide, accept, activate)
- Unblocks = downstream artifact IDs waiting on this decision
- Only show this section if there are items to list
- For EPICs without a parent chain to an Initiative (check `.priority.decision_debt` — if the EPIC appears in `_unaligned`), append "(no initiative — assign first)" to the What's Needed column

## Section 5: Work Ready to Start

Agent-delegatable, implementation-ready items from `.artifacts.ready[]` that
are NOT decision-type artifacts (i.e., not Proposed specs, ADRs, or spikes).

```
| Artifact | Purpose | Unblocks |
|----------|---------|----------|
| SPEC-NNN: Title | Truncated description (~60 chars) | DEP-NNN, ... or — |
```

Rules:
- Purpose = first ~60 chars of the artifact's description
- Unblocks = downstream artifact IDs that become unblocked once this is done
- Omit this section if there are no implementation-ready items

## Section 6: Epic Progress

One table with all active epics and their child specs in a tree.
Use `└` to indent children under their parent epic.

```
| Artifact | Purpose | Readiness |
|----------|---------|-----------|
| **EPIC-NNN**: Title | Truncated description (~60 chars) | Needs decomposition / N/M specs resolved / Blocked on X |
| └ SPEC-NNN: Title | Truncated description | Proposed — review and approve / Ready — implementation ready / Blocked on Y |
| └ SPEC-NNN: Title | Truncated description | Status — next action |
| **EPIC-NNN**: Title | Truncated description | ... |
```

Rules:
- **Bold** the epic ID and title
- Include ALL child specs under each epic, indented with `└`
- Purpose = first ~60 chars of the artifact's description
- Readiness = current status + what needs to happen next
- Epics with no children: readiness = "Needs decomposition into specs"
- Epics/specs that are blocked: note what they're blocked on

## Section 7: Research (Spikes)

Table of all unresolved spikes.

```
| Spike | Question | Status | Unblocks |
|-------|----------|--------|----------|
| SPIKE-NNN | Core research question from description | Proposed / Active | SPEC-NNN, ... or — |
```

Rules:
- Question = the spike's core question (its description), truncated to ~80 chars
- Unblocks = downstream artifacts waiting on this spike
- Sort: Active first, then by unblock count descending, then by ID

## Section 8: Blocked Items

Only if there are blocked items not already shown in the epic tree.

```
- **TYPE-NNN**: Title — blocked on: DEP-NNN (with note if the blocker is actionable)
```

Rules:
- Group items that share a common blocker under a single entry. State whether
  the blocker is actionable now.

## Section 9: Tasks & Issues

Brief summary of in-progress tk tasks. Omit if empty.

## Section 10: Open GitHub Issues

Table of open GitHub issues. These are external signals — bugs, feature requests,
or process gaps reported outside the artifact system.

```
| Issue | Title | Labels |
|-------|-------|--------|
| #NNN | Issue title (~60 chars) | bug, enhancement, ... or — |
```

Rules:
- Show all open issues from the status data (up to 10)
- If the user has assigned issues, show those first with a bold **Assigned** prefix
- Labels help the user triage — include them if present, `—` if none
- If an issue is linked to an artifact (visible in the Linked Issues section), note the artifact ID in parentheses after the title
- Omit this section if there are no open issues

## Section 11: Cross-Reference Gaps

Table of artifacts with frontmatter/body cross-reference discrepancies. Only
show artifacts with at least one discrepancy. Merge body-not-in-frontmatter and
missing-reciprocal into one row per artifact. Omit this section entirely when
there are no discrepancies.

```
| Artifact | Undeclared Body References | Missing Reciprocal | Action |
|----------|--------------------------|-------------------|--------|
| EPIC-005 | SPIKE-007, SPIKE-008 | — | Classify as depends-on or linked-artifacts |
| SPIKE-007 | — | EPIC-005 | Add EPIC-005 to linked-artifacts |
```

Rules:
- Only show artifacts with at least one discrepancy
- Merge body-not-in-frontmatter and missing-reciprocal into one row per artifact
- Omit the entire section when there are no discrepancies
- The agent should suggest concrete frontmatter edits based on context (e.g., which field to add the reference to)
- When xref gaps exist, include in suggestions: "There are N cross-reference gaps — want me to review and fix the frontmatter declarations?"

## Full Example

```markdown
> **Resuming:** Fixed xref gaps across 79 artifact files — 0 missing reciprocals remain

## Recommendation

**Action:** Approve SPEC-009.
**Why:** Approving it unblocks SPEC-010 and EPIC-007 — highest downstream leverage of all actionable items.

## Decisions Needed

| Artifact | What's Needed | Unblocks |
|----------|--------------|----------|
| **SPEC-009**: Normalize Artifact Frontmatter Relationships | review and approve | SPEC-010, EPIC-007 |
| **SPIKE-012**: Which artifact types are decision-only? | activate | SPEC-010 |

## Work Ready to Start

| Artifact | Purpose | Unblocks |
|----------|---------|----------|
| SPEC-011: Skill Context Footprint Audit | Audit context size across all active skills | EPIC-006 |

## Epic Progress

| Artifact | Purpose | Readiness |
|----------|---------|-----------|
| **EPIC-005**: Isolated Claude Code Environment | One-command workflow for isolated, ephemeral Claude Code | Needs decomposition into specs |
| **EPIC-006**: Skill Context Footprint Reduction | Reduce disproportionate context consumption by swain skills | 0/1 specs resolved (1 remaining) |
| └ SPEC-010: Decision-Only Artifacts Bug | Misclassifies decision-only artifacts as implementable | Proposed — blocked on SPIKE-012 |
| **EPIC-007**: Model Routing & Reasoning Effort | Route skills to appropriate models and effort levels | Blocked on EPIC-006 |

## Research

| Spike | Question | Status | Unblocks |
|-------|----------|--------|----------|
| SPIKE-006 | What task tracking backend should swain-do use? | Active | — |
| SPIKE-012 | Which artifact types are decision-only across their lifecycle? | Proposed | SPEC-010 |
| SPIKE-010 | Which skills consume the most context and where's the waste? | Proposed | — |
| SPIKE-011 | What strategies can reduce skill content loaded into context? | Proposed | — |
| SPIKE-013 | How do agent runtimes expose model selection and effort controls? | Proposed | — |
| SPIKE-014 | Which skill operations belong to which cognitive load tier? | Proposed | — |

## Blocked Items

- **EPIC-007**: Model Routing & Reasoning Effort — blocked on: EPIC-006 (actionable: yes, EPIC-006 has ready specs)

## Tasks & Issues

No tasks in progress.

## Open GitHub Issues

| Issue | Title | Labels |
|-------|-------|--------|
| #36 | MOTD: show uncommitted file count, explore clickable commit | enhancement |
| #29 | Decision-only artifacts shown as implementable in status | bug |
| #28 | VISION-to-VISION deps should not block status | bug |
| #27 | swain-search: normalize YouTube transcripts to markdown | enhancement |
| #26 | Spike conclusions not surfaced in final pass | enhancement |
```
