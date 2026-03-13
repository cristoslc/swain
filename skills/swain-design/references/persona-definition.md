# Personas (PERSONA-NNN)

**Template:** [persona-template.md.template](persona-template.md.template)

**Lifecycle track: Standing**

```mermaid
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
```

A user archetype that represents a distinct segment of the product's audience. Follow **Alan Cooper's persona model** (from *The Inmates Are Running the Asylum*): a Persona is a concrete, narrative description of a fictional but realistic user — defined by goals, behaviors, and context, not demographics alone. Personas are cross-cutting — they are referenced by Journeys, Visions, and other artifacts but are not owned by any single one.

- **Folder structure:** `docs/persona/<Phase>/(PERSONA-NNN)-<Title>/` — the Persona folder lives inside a subdirectory matching its current lifecycle phase. Phase subdirectories: `Proposed/`, `Active/`, `Retired/`, `Superseded/`.
  - Example: `docs/persona/Active/(PERSONA-001)-Solo-Developer/`
  - When transitioning phases, **move the folder** to the new phase directory (e.g., `git mv docs/persona/Proposed/(PERSONA-001)-Foo/ docs/persona/Active/(PERSONA-001)-Foo/`).
  - Primary file: `(PERSONA-NNN)-<Title>.md` — the persona definition.
  - Supporting docs: interview notes, survey data, behavioral research, demographic analysis.
- A Persona is "Active" when its attributes have been confirmed through review or data analysis.
- Personas are *reference artifacts* — they inform Journey and Agent Spec creation but are not directly implemented. They do NOT contain acceptance criteria, task breakdowns, or feature specifications.
