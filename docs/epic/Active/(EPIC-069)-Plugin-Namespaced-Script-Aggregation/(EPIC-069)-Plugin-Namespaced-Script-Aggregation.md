---
title: "Plugin-Namespaced Script Aggregation"
artifact: EPIC-069
track: container
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
parent-vision: VISION-001
parent-initiative: INITIATIVE-002
priority-weight: high
success-criteria:
  - All agent-facing script references use `.agents/scripts/swain/<script>` path.
  - All operator-facing script references use `.agents/bin/swain/<script>` path.
  - No references to `.agents/bin/<script>` (flat namespace) remain in skill files.
  - No `bin/` directory at project root.
  - swain-init bootstrap creates plugin-namespaced aggregation directories.
  - swain-doctor detects and migrates legacy `.agents/bin/` flat layout.
  - README.md files generated in `.agents/scripts/` and `.agents/bin/`.
  - Consumer projects receive automatic migration on first doctor run after update.
depends-on-artifacts:
  - ADR-036
addresses: []
trove: agent-script-directory-conventions
---

# Plugin-Namespaced Script Aggregation

## Goal / Objective

The flat `.agents/bin/` layout from [ADR-019](../../adr/Superseded/(ADR-019)-Project-Root-Script-Convention/(ADR-019)-Project-Root-Script-Convention.md) risks collisions and doesn't match the Agent Skills standard. This epic replaces it with namespaced dirs per [ADR-036](../../adr/Active/(ADR-036)-Plugin-Namespaced-Script-Aggregation/(ADR-036)-Plugin-Namespaced-Script-Aggregation.md). Agent scripts move to `.agents/scripts/swain/`. Operator scripts move to `.agents/bin/swain/`. The `bin/` dir at project root goes away.

## Desired Outcomes

- No flat-namespace collisions in consumer projects.
- Script naming aligns with the Agent Skills ecosystem: `scripts/` for agents, `bin/` for operators.
- Other frameworks can coexist alongside swain with no path interference.
- Migration is transparent. Consumers update swain and doctor handles the rest.

## Scope Boundaries

**In scope:**
- ADR-036 authoring and ADR-019 supersession.
- swain-init bootstrap rewrite (namespaced dir creation).
- swain-doctor health checks (detect, migrate, repair).
- Update all skill refs to new paths.
- README.md generation in aggregation dirs.
- Consumer migration (doctor advisory + auto-migrate).
- Script audience header convention (`# swain-audience: operator`).

**Out of scope:**
- Operator-facing DX (how the human invokes `swain` or `swain-box`). Deferred to a DESIGN.
- Upstream issue on agentskills/agentskills. Optional.
- Multi-runtime polymorphism (plugin shape per host). See related spike.

## Child Specs

- **SPEC-TBD-1:** ADR-036 authoring and ADR-019 supersession. *(Done inline with EPIC creation.)*
- **SPEC-TBD-2:** Rewrite swain-init bootstrap. Replace `.agents/bin/` flat symlinks with namespaced dirs. Add audience header parsing. Add README.md generation.
- **SPEC-TBD-3:** Update swain-doctor health checks. Detect legacy flat layout, migrate, repair symlinks in new dirs.
- **SPEC-TBD-4:** Migrate all skill references. Replace `.agents/bin/<script>` with `.agents/scripts/swain/<script>` across SKILL.md files and shell scripts. Replace `bin/<script>` with `.agents/bin/swain/<script>`.
- **SPEC-TBD-5:** Remove `bin/` from project root. Delete symlinks, update gitignore entries.
- **SPEC-TBD-6:** Consumer migration. Doctor detects old layout on first run, auto-migrates, emits advisory.

## Key Dependencies

- [ADR-036](../../adr/Active/(ADR-036)-Plugin-Namespaced-Script-Aggregation/(ADR-036)-Plugin-Namespaced-Script-Aggregation.md) must be Active before implementation begins. *(Done.)*

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | -- | Created with ADR-036. Consumer bug report plus industry research (14 sources). |
