---
title: "Artifact Type System & Issue Integration"
artifact: EPIC-002
status: Proposed
author: cristos
created: 2026-03-11
last-updated: 2026-03-11
parent-vision:
  - VISION-001
success-criteria:
  - swain-design supports lightweight enhancement tracking (not just BUG or full SPEC) for small improvements that may touch multiple stories
  - External issue tracker work items (starting with GitHub Issues) can be pulled into the swain workflow with bidirectional status sync
  - Issue integration is backend-agnostic — designed for future support of Jira, Linear, etc. via CLI tools, MCPs, or scripts
depends-on: []
addresses:
  - JOURNEY-001.PP-01
evidence-pool: ""
---

# Artifact Type System & Issue Integration

## Goal / Objective

Extend swain-design's artifact model in two directions:

1. **Standalone SPECs with type metadata** — Make `parent-epic` optional on SPECs so small improvements can be tracked without requiring an epic. Add an optional `type: feature | enhancement` frontmatter field for display grouping and issue tracker label mapping. This was decided by SPIKE-003, which found that SPEC ceremony isn't the friction (agents fill it out regardless) — the mandatory `parent-epic` is.

2. **External issue integration** — Pull work from external issue trackers (GitHub Issues first) into the swain workflow. Backlink to the source issue so status updates flow back, and close issues in sync with artifact completion. Design the integration layer to be backend-agnostic — GitHub today, but Jira, Linear, and others in the future via different backends (CLI tools like `gh`, MCPs, or custom scripts). GitHub Issues becomes the lightweight intake funnel — most enhancements live as issues until promoted to a SPEC when worth structuring.

## Scope Boundaries

**In scope:**
- ~~Spike to determine the right modeling approach for enhancements~~ SPIKE-003 complete — decision: standalone SPECs with optional `type` field
- Make `parent-epic` optional in SPEC template, definition, and tooling
- Add optional `type` frontmatter field to SPEC
- GitHub Issues integration with bidirectional sync (pull in, post updates, close)
- Backend abstraction layer for future issue tracker support
- Updates to swain-status to surface integrated issues alongside artifacts
- swain-doctor migration: audit existing SPECs, detect missing parent-epic gracefully
- README and skill documentation updates to reflect the new model
- Updates to VISION-001 supporting docs (architecture overview, roadmap)

**Out of scope:**
- Jira, Linear, or other non-GitHub backends (future epics)
- Web dashboard for issue management (belongs to a dashboard epic)
- Automated issue creation from swain artifacts (reverse direction)
- Changes to BUG artifact type (stays as-is)

## SPIKE-003 Decision

SPIKE-003 investigated five options for enhancement tracking. Finding: the agent fills out full SPEC ceremony regardless of scope, so "lighter specs" aren't needed. The real friction is `parent-epic` being mandatory — it forces organizational overhead that doesn't serve either consumer (operator or agent).

**Decision:** Option B (modified) — make `parent-epic` optional on SPECs, add optional `type: feature | enhancement` metadata. No new artifact types, no migration for existing consumers, zero tooling changes required (specgraph/specwatch/swain-status already handle SPECs fully).

## Child Specs

- ~~SPIKE-003: Enhancement Type Modeling~~ **Complete** — decision captured above
- SPEC-NNN: Standalone SPECs (make parent-epic optional, add type field) — TBD
- SPEC-NNN: GitHub Issues Integration (bidirectional sync, backend abstraction) — TBD
- SPEC-NNN: swain-doctor Migration (audit, detect, remediate for existing users) — TBD

## Initial Implementation Plan

This epic touches a wide surface area. Rough ordering:

### Phase 1: Artifact model changes
- Update SPEC definition (`spec-definition.md`) — make `parent-epic` optional, document standalone SPECs
- Update SPEC template (`spec-template.md.template`) — add `type` field, make `parent-epic` default to empty
- Update specgraph.sh — tolerate missing `parent-epic` on SPECs, group standalone SPECs separately
- Update specwatch.sh — don't flag missing `parent-epic` as an error
- Update swain-status.sh — display standalone SPECs in their own section or inline with epic children

### Phase 2: Issue integration
- Design backend abstraction (interface for pull, push-status, close)
- Implement GitHub backend via `gh` CLI
- Add `source-issue` frontmatter field to SPEC and BUG (links back to external issue)
- swain-status: surface linked issues with sync status
- Bidirectional lifecycle sync (artifact transitions → issue comments/close)

### Phase 3: Migration and documentation
- swain-doctor: detect existing SPECs, validate gracefully, offer remediation
- README updates: document standalone SPECs, type field, issue integration
- Skill documentation updates (swain-design, swain-status, swain-do)
- VISION-001 supporting docs: architecture overview, roadmap with this epic

### Phase 4: Ecosystem alignment
- Update AGENTS.md skill routing docs
- Ensure all existing artifacts validate cleanly under new rules
- Design audit (optional) — review existing project artifacts against new model

## Key Dependencies

- ~~SPIKE-003 findings~~ Complete
- GitHub CLI (`gh`) availability for issue integration
- VISION-001 for parent-vision linkage

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-11 | a950529 | Initial creation |
