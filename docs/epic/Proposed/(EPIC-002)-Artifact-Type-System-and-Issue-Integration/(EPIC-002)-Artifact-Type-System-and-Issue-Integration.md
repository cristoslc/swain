---
title: "Artifact Type System & Issue Integration"
artifact: EPIC-002
status: Proposed
author: cristos
created: 2026-03-11
last-updated: 2026-03-11
parent-vision: []
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

1. **Enhancement tracking** — Add support for lightweight enhancement work items. Today, BUG handles small defect fixes and SPEC handles full feature specifications, but there's no artifact for small improvements that aren't bugs and don't warrant a full spec. These may touch multiple stories and need proper lifecycle tracking without the overhead of a SPEC.

2. **External issue integration** — Pull work from external issue trackers (GitHub Issues first) into the swain workflow. Backlink to the source issue so status updates flow back, and close issues in sync with artifact completion. Design the integration layer to be backend-agnostic — GitHub today, but Jira, Linear, and others in the future via different backends (CLI tools like `gh`, MCPs, or custom scripts).

## Scope Boundaries

**In scope:**
- Spike to determine the right modeling approach for enhancements (new type vs. SPEC type discriminator)
- Implementation of the chosen enhancement model in swain-design
- GitHub Issues integration with bidirectional sync (pull in, post updates, close)
- Backend abstraction layer for future issue tracker support
- Updates to swain-status to surface integrated issues alongside artifacts

**Out of scope:**
- Jira, Linear, or other non-GitHub backends (future epics)
- Web dashboard for issue management (belongs to a dashboard epic)
- Automated issue creation from swain artifacts (reverse direction)

## Child Specs

- SPIKE-003: Enhancement Type Modeling (planned — determines approach before specs are written)
- Further specs TBD pending spike findings

## Key Dependencies

- SPIKE-003 findings will determine whether we add a new ENHANCEMENT type or add a `type` discriminator to SPEC
- GitHub CLI (`gh`) availability for issue integration

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-11 | a950529 | Initial creation |
