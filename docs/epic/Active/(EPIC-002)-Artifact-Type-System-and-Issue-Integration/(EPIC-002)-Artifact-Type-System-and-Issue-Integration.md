---
title: "Artifact Type System & Issue Integration"
artifact: EPIC-002
status: Active
author: cristos
created: 2026-03-11
last-updated: 2026-03-11
parent-vision:
  - VISION-001
success-criteria:
  - SPEC supports standalone use (no parent-epic required) with type metadata (feature | enhancement | bug)
  - BUG artifact type is eliminated — bugs are SPECs with type: bug
  - External issue tracker work items (starting with GitHub Issues) can be pulled into the swain workflow with bidirectional status sync
  - Issue integration is backend-agnostic — designed for future support of Jira, Linear, etc. via CLI tools, MCPs, or scripts
  - Existing swain consumers have a clean migration path via swain-doctor
depends-on: []
addresses:
  - JOURNEY-001.PP-01
evidence-pool: ""
---

# Artifact Type System & Issue Integration

## Goal / Objective

Extend swain-design's artifact model in two directions:

1. **Unified SPEC type system** — Make `parent-epic` optional on SPECs so standalone work doesn't require an epic. Add a `type: feature | enhancement | bug` frontmatter field. Fold BUG into SPEC as `type: bug` — eliminating a separate artifact type. Bug-specific sections (reproduction steps, severity, expected/actual behavior) become optional SPEC sections included when `type: bug`. This reduces the artifact model from 11 types to 10 and unifies all implementation work under SPEC.

2. **External issue integration** — Pull work from external issue trackers (GitHub Issues first) into the swain workflow. Backlink to the source issue so status updates flow back, and close issues in sync with artifact completion. Design the integration layer to be backend-agnostic — GitHub today, but Jira, Linear, and others in the future via different backends (CLI tools like `gh`, MCPs, or custom scripts). GitHub Issues becomes the lightweight intake funnel — most enhancements live as issues until promoted to a SPEC when worth structuring.

## Scope Boundaries

**In scope:**
- ~~Spike to determine the right modeling approach for enhancements~~ SPIKE-003 complete
- Make `parent-epic` optional in SPEC template, definition, and tooling
- Add `type: feature | enhancement | bug` frontmatter field to SPEC
- Fold BUG into SPEC — migrate BUG definition, template, and lifecycle into SPEC with `type: bug`
- Remove BUG as a standalone artifact type (definition, template, folder structure)
- swain-doctor migration: detect existing BUG artifacts and convert to SPECs with `type: bug`
- Update all tooling (specgraph, specwatch, swain-status, adr-check) to drop BUG type
- GitHub Issues integration with bidirectional sync (pull in, post updates, close)
- Backend abstraction layer for future issue tracker support
- Updates to swain-status to surface integrated issues alongside artifacts
- README and skill documentation updates to reflect the new model
- Updates to VISION-001 supporting docs (architecture overview, roadmap)

**Out of scope:**
- Jira, Linear, or other non-GitHub backends (future epics)
- Web dashboard for issue management (belongs to a dashboard epic)
- Automated issue creation from swain artifacts (reverse direction)

## SPIKE-003 Decision

SPIKE-003 investigated five options for enhancement tracking. Finding: the agent fills out full SPEC ceremony regardless of scope, so "lighter specs" aren't needed. The real friction is `parent-epic` being mandatory — it forces organizational overhead that doesn't serve either consumer (operator or agent).

**Decision:** Option B (extended) — make `parent-epic` optional on SPECs, add `type: feature | enhancement | bug` metadata. Fold BUG entirely into SPEC as `type: bug`. This eliminates a standalone artifact type, unifies all implementation work under SPEC, and maps cleanly to external issue tracker labels. Existing BUG artifacts (if any) get migrated to SPECs via swain-doctor.

## Child Specs

- ~~SPIKE-003: Enhancement Type Modeling~~ **Complete** — decision captured above
- SPEC-NNN: Unified SPEC Type System (optional parent-epic, type field, fold BUG into SPEC) — TBD
- SPEC-NNN: GitHub Issues Integration (bidirectional sync, backend abstraction) — TBD
- SPEC-NNN: swain-doctor Migration (BUG→SPEC conversion, audit, remediation for existing users) — TBD

## Initial Implementation Plan

This epic touches a wide surface area. Rough ordering:

### Phase 1: Unified SPEC type system
- Update SPEC definition — make `parent-epic` optional, add `type: feature | enhancement | bug`, document standalone SPECs
- Update SPEC template — add `type` field, make `parent-epic` default to empty, add conditional bug sections (reproduction steps, severity, expected/actual)
- Remove BUG definition, template, and references from swain-design skill
- Update specgraph.sh — drop BUG type, tolerate missing `parent-epic`, group standalone SPECs
- Update specwatch.sh — drop BUG from TYPE_DIRS, don't flag missing `parent-epic`
- Update swain-status.sh — drop BUG-specific logic, display standalone SPECs, show type labels
- Update swain-design SKILL.md — remove BUG from artifact table, update relationship model, update tracking tiers
- Update AGENTS.md artifact references

### Phase 2: Issue integration
- Design backend abstraction (interface for pull, push-status, close)
- Implement GitHub backend via `gh` CLI
- Add `source-issue` frontmatter field to SPEC (links back to external issue)
- swain-status: surface linked issues with sync status
- Bidirectional lifecycle sync (artifact transitions → issue comments/close)

### Phase 3: Migration and documentation
- swain-doctor: detect existing BUG artifacts, convert to SPECs with `type: bug`, rewrite cross-references
- swain-doctor: validate standalone SPECs gracefully
- README updates: document unified SPEC types, standalone SPECs, issue integration
- Skill documentation updates (swain-design, swain-status, swain-do)
- VISION-001 supporting docs: architecture overview, roadmap

### Phase 4: Ecosystem alignment
- Update all existing artifacts to validate cleanly under new rules
- Design audit — review project artifacts against new model
- Ensure specwatch/specgraph produce clean output with no BUG references

## Key Dependencies

- ~~SPIKE-003 findings~~ Complete
- GitHub CLI (`gh`) availability for issue integration
- VISION-001 for parent-vision linkage

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-11 | a950529 | Initial creation |
