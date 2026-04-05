---
title: "Gherkin As Notation, Not Infrastructure"
artifact: ADR-030
track: standing
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
linked-artifacts:
  - EPIC-060
  - DESIGN-019
  - DESIGN-020
depends-on-artifacts: []
evidence-pool: ""
---

# Gherkin As Notation, Not Infrastructure

## Context

Swain uses BDD traceability to link spec acceptance criteria to agent-produced tests ([EPIC-060](../../epic/Active/(EPIC-060)-BDD-Traceability/(EPIC-060)-BDD-Traceability.md)). Standard BDD tools — Cucumber, Behave, SpecFlow — expect `.feature` files. A runner parses those files and maps steps to glue code. Swain works differently. Its artifacts are markdown files. Its test runners are agents and shell scripts, not step-definition registries.

We had to choose: does Gherkin enter swain as infrastructure (its own files, runners, and step registries) or as notation (a known format inside the markdown artifacts agents already read and write)?

## Decision

We adopt Gherkin as **notation only**. It lives in fenced code blocks inside existing markdown artifacts. There are no `.feature` files, no step-definition registries, and no dedicated BDD runner. Agents act as runners: they read Gherkin scenarios, derive tests, and produce evidence.

This matches the Jinja2 pattern in spec templates. Agents understand the format without a rendering pipeline. Gherkin gives structure (Given/When/Then, `@id:` tags, `@bdd:` markers). Agents and tooling handle execution.

## Alternatives Considered

**Full BDD framework integration (Cucumber/Behave).** Export `.feature` files from specs. Keep step definitions next to code. Use a runner to map steps to glue code. Rejected because:
- Swain is framework-agnostic. A specific BDD runner adds a dependency swain can't control.
- Step-definition registries create a new sync burden — the same gap BDD was meant to close.
- `.feature` files copy data already in spec acceptance criteria.

**Gherkin sidecar files.** Generate `.feature` files next to specs. Skip the runner but use them as structured input for agents. Rejected because:
- Each spec now has two files (markdown and `.feature`). Drift between them brings the problem back.
- Embedding in markdown works just as well — agents read both formats the same way.

**Custom structured format (YAML/JSON scenarios).** Build a swain-specific schema for behavioral contracts. Rejected because:
- Agents already know Gherkin. A new format means agents must learn it and operators lose their mental model.
- YAML scenarios are harder to read in review. Operators review behavior, not data structures.

**No structured notation (status quo).** Keep prose Given/When/Then in acceptance criteria with no formal structure. Rejected because:
- Intent leakage persists. Without `@id:` tags and `@bdd:` markers, no machine-traceable link ties a declared behavior to its test.
- Drift detection needs structure. You can't find undeclared behaviors in free-form prose with a script.

## Consequences

**Positive:**
- Zero new dependencies. No BDD framework to install, configure, or version.
- Artifacts stay as plain markdown. Any viewer (Typora, GitHub, VS Code) renders them correctly.
- Agents already understand Gherkin. No training, prompts, or custom parsers needed.
- The pattern fits swain's existing toolchain. `spec-verify.sh`, `swain-doctor`, and `specgraph` all work on markdown files and git metadata.

**Accepted downsides:**
- No automatic step-to-code mapping. Agents must derive tests by reading scenarios, not by running a step-to-function lookup. This is fine because agents handle meaning better than rote mapping.
- No parser catches Gherkin syntax errors at write time. `swain-doctor` can check structure, but there is no IDE support for Gherkin-in-markdown. The format is simple enough that syntax errors are rare.
- Projects that want `.feature` files for their own test suites must export them on their own. This is a project-level opt-in, not a swain concern.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | _pending_ | Adopted based on design conversation exploring BDD integration |
