---
title: "Task Management Decision Framework Integration"
artifact: SPIKE-046
track: container
status: Active
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
question: "Where should the task-management decision framework (from shines' evaluation rubric) live in swain, and can the rubric criteria generalize into a reusable tool-selection framework?"
gate: Pre-MVP
trove: task-management-systems@a120d0b
risks-addressed:
  - "Decision framework exists only as an external document, not integrated into swain workflows"
  - "New projects adopt tk by default without evaluating alternatives"
  - "Rubric criteria are ad-hoc rather than a reusable evaluation pattern"
trove: "docs/troves/task-management-systems"
---

# Task Management Decision Framework Integration

## Summary

<!-- Final-pass section: populated when transitioning to Complete. -->

## Question

Where should shines' task-management decision framework (from the task-tracking-evaluation.md rubric) live in swain, and can the 10 rubric criteria generalize into a reusable evaluation framework for other tool-selection decisions?

The decision framework is a structured tree:

```
Do you need cross-session persistence?
  NO  --> blizzy78/mcp-task-manager (session planner)
  YES -->
    Do you need artifact/spec traceability?
      YES -->
        Do you need ENFORCED traceability with lifecycle governance?
          YES --> Swain Integrated Ecosystem
          NO  -->
            Already using swain? --> swain-do + tk
            Starting fresh?     --> Claude Task Master (PRD-driven)
      NO -->
        Do humans also need to see task state?
          YES -->
            Team uses Linear/Jira/GitHub? --> External PM via MCP
            Solo / small team?            --> saga-mcp or Notion
          NO -->
            Need dependency logic?
              YES --> Built-in Tasks or saga-mcp
              NO  --> File-based markdown
```

The rubric uses 10 criteria: Dependency Awareness, Priority System, Persistence Model, Agent-Native Design, Cross-Session Continuity, Human Readability, Integration Effort, Artifact Traceability, Multi-Agent/Collaboration, Portability.

## Go / No-Go Criteria

1. **Integration point identified**: At least one concrete location in swain where the decision framework adds value to an existing workflow (not just a standalone reference doc).
2. **Generalization feasibility assessed**: Clear determination of whether the 10-criterion rubric pattern can be reused for at least one other tool-selection domain (e.g., MCP server selection, CI/CD pipeline choice, testing framework selection).
3. **Implementation scope estimated**: Rough sizing of the integration work — is this a SPEC-level change or an EPIC?

## Pivot Recommendation

If no natural integration point exists in swain's current workflow, capture the decision framework as a reference document in `docs/references/` and close. The value of the framework doesn't depend on automation — a well-placed reference doc that agents and operators can consult is sufficient if the workflow integration is forced.

## Findings

### Candidate integration points

#### 1. swain-init: Project onboarding questionnaire

**Fit: Medium-High.** swain-init already configures the project. Adding a task-backend selection step would be natural:

- Ask 2-3 discriminating questions (persistence needs, traceability needs, team size)
- Recommend a task backend (tk, saga-mcp, Task Master, Built-in Tasks)
- Configure the chosen backend (install MCP server, set AGENTS.md routing)

**Concern:** swain-init currently assumes tk. Making the task backend pluggable requires abstracting swain-do's tk dependency — that's significant work.

#### 2. swain-doctor: Fitness assessment

**Fit: Medium.** swain-doctor could assess whether the current task backend matches project characteristics:

- Solo project with 5 specs → "tk is well-suited"
- 50+ specs, 3 contributors → "Consider saga-mcp or Linear for richer hierarchy and collaboration"

**Concern:** This is advisory, not actionable. swain-doctor diagnoses problems; recommending a different tool feels outside its scope unless paired with migration tooling.

#### 3. swain-help: Contextual guidance

**Fit: High.** When users ask about task management ("what task tools can I use?", "should I use Linear?"), swain-help could surface the decision tree. This is the lowest-friction integration — no new skills, no configuration changes, just better help responses.

**Concern:** swain-help is a passive reference. The framework's value increases if it's actively invoked at decision points.

#### 4. Standalone reference doc

**Fit: Always works.** A reference doc at `docs/references/task-management-decision-framework.md` that agents and operators can consult. Low effort, immediate value.

**Concern:** Reference docs drift if not maintained. The trove (`task-management-systems@a120d0b`) provides the source material; the decision framework doc would need to stay in sync.

#### 5. swain-adopt: New skill for tool selection

**Fit: High but expensive.** A dedicated skill that helps projects evaluate and adopt tools:

- `swain adopt task-management` → runs the decision tree, configures the result
- `swain adopt ci-cd` → similar framework for CI/CD tools
- Reusable rubric engine that applies weighted criteria to tool candidates

**Concern:** Premature abstraction. Building a generic tool-selection framework is a significant investment. Start with the specific (task management) and generalize only if a second domain materializes.

### Generalization potential of the rubric criteria

The 10 criteria from shines' rubric map to a broader pattern:

| Rubric Criterion | Generalized Form | Other Domains |
|-----------------|------------------|---------------|
| Dependency Awareness | Relationship modeling | MCP server capabilities, CI pipeline stages |
| Priority System | Decision ordering | Feature prioritization, bug triage |
| Persistence Model | State durability | Cache selection, session storage |
| Agent-Native Design | API ergonomics for LLMs | Any MCP server evaluation |
| Cross-Session Continuity | State recovery | Conversation management, context systems |
| Human Readability | Inspectability | Logging, monitoring, observability tools |
| Integration Effort | Adoption cost | Any tool evaluation |
| Artifact Traceability | Provenance tracking | Documentation systems, audit tools |
| Multi-Agent / Collaboration | Concurrent access | Version control, shared state systems |
| Portability | Vendor independence | Cloud services, data formats |

At least 6 of the 10 criteria apply directly to MCP server evaluation — suggesting a reusable pattern exists. The criteria that are task-management-specific (Dependency Awareness, Priority System, Artifact Traceability) would need domain substitution for other contexts.

### Recommended approach

**Phase 1 (immediate):** Integrate into swain-help. When users ask about task management, surface the decision tree and link to the trove. Low effort, immediate value.

**Phase 2 (if demand materializes):** Add a task-backend selection step to swain-init. This requires designing the abstraction layer between swain-do and the underlying task backend — scope it as a SPEC under a relevant initiative.

**Phase 3 (only if a second domain appears):** Generalize the rubric into a reusable evaluation framework (swain-adopt or similar). Don't build this speculatively.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-22 | -- | Initial creation, research from task-management-systems trove |
