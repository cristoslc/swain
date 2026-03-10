# Agent Specs (SPEC-NNN)

**Template:** [spec-template.md.template](spec-template.md.template)

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Review
    Review --> Approved
    Approved --> Testing
    Testing --> Implemented
    Implemented --> Deprecated
    Deprecated --> [*]
    Draft --> Abandoned
    Review --> Abandoned
    Approved --> Abandoned
    Testing --> Abandoned
    Implemented --> Abandoned
    Abandoned --> [*]
```

Follow **spec-driven development** principles: an Agent Spec is a behavior contract — precise enough for an agent to create an implementation plan from, but concise enough to scan in a single pass. It defines external behavior (inputs, outputs, preconditions, constraints), not exhaustive requirements. Supplemental detail comes from child Stories and linked research.

- **Folder structure:** `docs/spec/<Phase>/(SPEC-NNN)-<Title>/` — the Spec folder lives inside a subdirectory matching its current lifecycle phase. Phase subdirectories: `Draft/`, `Review/`, `Approved/`, `Testing/`, `Implemented/`, `Deprecated/`.
  - Example: `docs/spec/Approved/(SPEC-002)-Widget-Factory/`
  - When transitioning phases, **move the folder** to the new phase directory (e.g., `git mv docs/spec/Draft/(SPEC-002)-Foo/ docs/spec/Review/(SPEC-002)-Foo/`).
  - Primary file: `(SPEC-NNN)-<Title>.md` — the spec document itself.
  - Supporting docs live alongside it in the same folder.
- Should be scoped to something a team (or agent) can ship and validate independently.
- **Tracking requirement:** All Specs carry `swain-do: required` in frontmatter. When a Spec comes up for implementation, invoke the swain-do skill to create a tracked plan before writing code (see SKILL.md § Execution tracking handoff).

## Testing phase

The `Testing` phase is the acceptance-verification gate between implementation and completion. A Spec enters `Testing` when its swain-do implementation plan is complete (all tasks done). It exits `Testing` only when every acceptance criterion has documented evidence.

### Entering Testing

When all swain-do tasks for a Spec are complete, transition the Spec from `Approved` to `Testing`. Do **not** skip directly to `Implemented`.

### Verification table

On entry to `Testing`, populate the Spec's **Verification** section. For each acceptance criterion:

1. **Criterion** — copy or paraphrase the Given/When/Then scenario from the Acceptance Criteria section.
2. **Evidence** — the test name, file path, manual check, or demo scenario that proves the criterion is satisfied. Reference specific test functions or files (e.g., `test_widget_export in tests/test_widget.py`).
3. **Result** — one of: `Pass`, `Fail`, or `Skip (reason)`.

Every criterion must have a non-empty Evidence and Result cell before the Spec can transition to `Implemented`.

### Verification gate

Before transitioning from `Testing → Implemented`, run `scripts/spec-verify.sh <artifact-path>`. The script checks that every acceptance criterion has corresponding evidence. Exit 0 = all criteria covered. Exit 1 = gaps found. Address gaps before proceeding.

### Supporting docs

For complex Specs with extensive test evidence (10+ criteria, multi-environment matrices), place detailed results in a `verification-report.md` alongside the Spec in its folder. The Verification table in the Spec should summarize; the report holds the detail.

```
docs/spec/Testing/(SPEC-003)-Widget-Factory/
  (SPEC-003)-Widget-Factory.md       ← the spec (with summary Verification table)
  verification-report.md             ← detailed evidence (optional)
```
