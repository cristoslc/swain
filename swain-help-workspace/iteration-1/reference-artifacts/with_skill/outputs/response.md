Swain manages **11 artifact types**, organized into four tiers based on how they're tracked.

---

### Implementation tier (tracked via bd)

These require a tracked plan before implementation begins.

| Type | ID Pattern | Phases | When to use |
|------|-----------|--------|-------------|
| **Story** | STORY-NNN | Todo -> In Progress -> Done | User-facing feature with acceptance criteria |
| **Agent Spec** | SPEC-NNN | Draft -> Review -> Approved -> Testing -> Implemented | Technical specification for an agent or component |
| **Bug** | BUG-NNN | Open -> In Progress -> Resolved -> Verified | Defect to track and fix |

### Coordination tier (children are tracked)

| Type | ID Pattern | Phases | When to use |
|------|-----------|--------|-------------|
| **Epic** | EPIC-NNN | Proposed -> Active -> Testing -> Complete | Large initiative decomposed into stories and specs |

### Research tier (tracking optional)

| Type | ID Pattern | Phases | When to use |
|------|-----------|--------|-------------|
| **Spike** | SPIKE-NNN | Planned -> Active -> Complete | Time-boxed investigation to reduce uncertainty |

### Reference tier (no tracking)

| Type | ID Pattern | When to use |
|------|-----------|-------------|
| **Vision** | VISION-NNN | Product direction and goals |
| **Journey** | JOURNEY-NNN | User journey with pain points |
| **ADR** | ADR-NNN | Architectural decision record |
| **Persona** | PERSONA-NNN | User persona definition |
| **Runbook** | RUNBOOK-NNN | Operational procedure |
| **Design** | DESIGN-NNN | UI/UX design artifact |

---

### How they connect

- **Vision** decomposes into Epics and Journeys
- **Epic** decomposes into Stories, Specs, and Spikes
- **Story/Spec** may reference ADRs, Personas, and Designs
- **Spike** attaches to any artifact and may produce ADRs
- **Bug** affects Specs and Epics; may link to Designs
- Any artifact can declare `depends-on:` blocking dependencies

---

To create any of these, just tell swain what you need -- for example, `/swain write a spec for auth token rotation` or `/swain file a bug about the login timeout`. Want details on a specific artifact type, or ready to create one?
