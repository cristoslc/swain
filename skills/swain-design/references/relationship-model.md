# Artifact Relationship Model

```mermaid
erDiagram
    VISION ||--o{ EPIC : "parent-vision"
    VISION ||--o{ JOURNEY : "parent-vision"
    EPIC ||--o{ SPEC : "parent-epic"
    EPIC ||--o{ STORY : "parent-epic"
    JOURNEY ||--|{ PAIN_POINT : "PP-NN"
    PAIN_POINT }o--o{ EPIC : "addresses"
    PAIN_POINT }o--o{ SPEC : "addresses"
    PAIN_POINT }o--o{ STORY : "addresses"
    PERSONA }o--o{ JOURNEY : "linked-personas"
    PERSONA }o--o{ STORY : "linked-stories"
    ADR }o--o{ SPEC : "linked-adrs"
    ADR }o--o{ EPIC : "linked-epics"
    SPEC }o--o{ SPIKE : "linked-research"
    SPEC ||--o| IMPL_PLAN : "seeds"
    RUNBOOK }o--o{ EPIC : "validates"
    RUNBOOK }o--o{ SPEC : "validates"
    SPIKE }o--o{ ADR : "linked-research"
    SPIKE }o--o{ EPIC : "linked-research"
    DESIGN }o--o{ EPIC : "linked-designs"
    DESIGN }o--o{ STORY : "linked-designs"
    DESIGN }o--o{ SPEC : "linked-designs"
```

**Key:** Solid lines (`||--o{`) = mandatory hierarchy. Diamond lines (`}o--o{`) = informational cross-references. SPIKE can attach to any artifact type, not just SPEC. Any artifact can declare `depends-on:` blocking dependencies on any other artifact. Per-type frontmatter fields are defined in each type's template.
