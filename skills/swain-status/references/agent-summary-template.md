# Agent Summary Template

After running the status script, present a structured summary using these tables.
The script's terminal output goes to the terminal with OSC 8 hyperlinks; this
summary is what the user actually reads for decision-making.

Do NOT just dump bullet lists. Use tables so the user can scan and compare.

## Section 1: Epic Progress

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
- Omit the Status column from the epic table in SKILL.md — readiness subsumes it

## Section 2: Research (Spikes)

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

## Section 3: Drafts Needing Review

Artifacts in Proposed status that need human review/approval.
**Exclude** items already shown in the epic tree or spike table — no duplication.

```
- **TYPE-NNN**: Title [Status] — what's needed (e.g., "review and approve", "review and decide")
```

Only show this section if there are items to list.

## Section 4: Blocked Items

Only if there are blocked items not already shown in the epic tree.

```
- **TYPE-NNN**: Title — blocked on: DEP-NNN (with note if the blocker is actionable)
```

## Section 5: Tasks & Issues

Brief summary of in-progress tk tasks and assigned GitHub issues.
Omit if empty. Keep it compact — these are context, not the decision point.

## Section 6: Follow-up

1-2 actionable suggestions. See the follow-up table in SKILL.md.
Pick suggestions based on what has the most downstream impact.

## Full Example

```markdown
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

## Drafts Needing Review

- **SPEC-009**: Normalize Artifact Frontmatter Relationships [Proposed] — review and approve

## Tasks & Issues

No tasks in progress. 5 open GitHub issues (#36, #29, #28, #27, #26).

---

EPIC-006 has the most downstream impact (unblocks EPIC-007). Ready to pick one up?
```
