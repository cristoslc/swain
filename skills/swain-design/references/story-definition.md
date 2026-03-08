# User Story (STORY-NNN)

**Template:** [story-template.md.template](story-template.md.template)

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Ready
    Ready --> Implemented
    Implemented --> [*]
    Draft --> Abandoned
    Ready --> Abandoned
    Abandoned --> [*]
```

The atomic unit of user-facing requirements. Follow **Mike Cohn's user story model** (from *User Stories Applied*): a Story captures a single capability from the user's perspective in the "As a / I want / so that" format with clear acceptance criteria. Stories should satisfy the **INVEST** criteria — Independent, Negotiable, Valuable, Estimable, Small, Testable. Decomposes an Epic into verifiable, implementable increments.

- **Format:** Single markdown file at `docs/story/<Phase>/(STORY-NNN)-<Title>.md` — placed in a subdirectory matching its current lifecycle phase. Phase subdirectories: `Draft/`, `Ready/`, `Implemented/`.
  - Example: `docs/story/Draft/(STORY-003)-Resumable-Data-Pull.md`
  - When transitioning phases, **move the file** to the new phase directory (e.g., `git mv docs/story/Draft/(STORY-003)-Foo.md docs/story/Ready/(STORY-003)-Foo.md`).
- Stories should be small enough to implement and verify independently. If a story requires multiple Agent Specs, it is likely scoped too broadly (should be an Epic).
- A Story is "Ready" when acceptance criteria are defined and agreed upon. A Story is "Implemented" when all acceptance criteria pass.
- **Tracking requirement:** All Stories carry `swain-do: required` in frontmatter. When a Story comes up for implementation, invoke the swain-do skill to create a tracked plan before writing code (see SKILL.md § Execution tracking handoff).
