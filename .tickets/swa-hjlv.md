---
id: swa-hjlv
status: open
deps: []
links: []
created: 2026-03-20T00:42:36Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-kd71
tags: [spec:SPEC-091]
---
# Task 1: Create train-definition.md

**Files:**
- Create: `.claude/skills/swain-design/references/train-definition.md`

- [ ] **Step 1: Create the definition file**

Follow the pattern of `runbook-definition.md` and `design-definition.md`. Key elements:

```markdown
# Training Documents (TRAIN-NNN)

**Template:** [train-template.md.template](train-template.md.template)

**Lifecycle track: Standing**

\`\`\`mermaid
stateDiagram-v2
    [*] --> Proposed
    Proposed --> Active
    Active --> Retired
    Active --> Superseded
    Retired --> [*]
    Superseded --> [*]
    Proposed --> Abandoned
    Active --> Abandoned
    Abandoned --> [*]
\`\`\`

A TRAIN artifact is structured product documentation for human operators. It teaches users how to use features specified by SPECs and delivered by EPICs. TRAINs are the furthest-downstream artifact — they translate technical specifications into learning materials.

TRAIN uses the [Diataxis framework](https://diataxis.fr/) for document typing. Each TRAIN has exactly one type; never mix types in a single document.

**Train types:**
- `how-to` — goal-oriented steps for a specific task. Assumes competence. ("How to configure credential scoping")
- `reference` — factual lookup material. Descriptive, complete, neutral. ("Artifact type reference")
- `quickstart` — compressed tutorial for time-to-first-success under 10 minutes. ("Your first swain project")

Additional Diataxis types (`tutorial`, `explanation`) are not defined at launch. Add when demand emerges.

- **Folder structure:** `docs/train/<Phase>/(TRAIN-NNN)-<Title>/` — the TRAIN folder lives inside a subdirectory matching its current lifecycle phase. Phase subdirectories: `Proposed/`, `Active/`, `Retired/`, `Superseded/`.
  - Example: `docs/train/Active/(TRAIN-001)-Getting-Started/`
  - When transitioning phases, **move the folder** to the new phase directory.
  - Primary file: `(TRAIN-NNN)-<Title>.md` — the training document.
  - Supporting docs: screenshots, diagrams, example configs, exercise files.
- **Audience:** The `audience` field references PERSONAs when available or accepts free-text (e.g., "new operators", "skill authors"). It describes who the document is for.
- **Hierarchy:** `parent-epic` OR `parent-initiative`, never both (same pattern as SPEC). TRAINs without parents are valid but flagged as unanchored.
- **Default granularity:** One TRAIN per EPIC minimum. Operator-overridable via swain config.
- **Staleness tracking:** TRAINs use enriched `linked-artifacts` entries with `rel: [documents]` and commit pinning. The `train-check.sh` script detects drift between pinned commits and current HEAD. See the design doc for the enriched format specification.
- A TRAIN is "Active" when its content has been reviewed and accurately reflects the current state of the artifacts it documents. "Superseded" when a newer TRAIN replaces it (link via `superseded-by:`). "Retired" when the features it describes no longer exist.
- TRAINs do NOT replace READMEs, CLAUDE.md, or AGENTS.md (operational configuration). TRAINs do NOT replace RUNBOOKs (executable procedures with pass/fail outcomes). TRAINs are educational content with learning objectives.
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/swain-design/references/train-definition.md
git commit -m "docs: add TRAIN artifact type definition"
```

