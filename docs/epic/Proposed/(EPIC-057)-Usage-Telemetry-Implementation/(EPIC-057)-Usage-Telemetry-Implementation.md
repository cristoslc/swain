---
title: "Usage Telemetry Implementation"
artifact: EPIC-057
status: Proposed
author: cristos
created: 2026-04-03
last-updated: 2026-04-03
parent-initiative: ""
linked-artifacts:
  - DESIGN-015
artifact-refs:
  - artifact: DESIGN-015
    rel: [aligned]
depends-on-artifacts: []
success-criteria:
  - Telemetry config management implemented (SPEC-244)
  - Event emission framework operational (SPEC-245)
  - Daily aggregation working (SPEC-246)
  - Export mechanism functional (SPEC-247)
  - All privacy safeguards verified
  - Integration complete in target skills
---

# Usage Telemetry Implementation

## Overview
Implement the usage logging and telemetry system per DESIGN-015. This epic covers the full implementation of opt-in, anonymous, local-first telemetry collection and export.

## Scope
This epic delivers:
1. Configuration management for telemetry (enable/disable/endpoint)
2. Event emission framework for skills
3. Daily aggregation of raw events into summaries
4. Export mechanism for sending summaries to external endpoints
5. Integration into core skills (session, design, do, worktree)

## Success Criteria
- [ ] Operator can enable/disable telemetry via CLI
- [ ] Events emitted when enabled, skipped when disabled
- [ ] All 8 event types implemented with correct schemas
- [ ] Daily summaries generated automatically
- [ ] Export works with operator confirmation
- [ ] No PII in any event or summary
- [ ] All integration points wired

## Child SPECs
- SPEC-244: Telemetry Configuration Management
- SPEC-245: Telemetry Event Emission Framework
- SPEC-246: Telemetry Aggregator and Summary Generation
- SPEC-247: Telemetry Export Mechanism

## Dependencies
- None (foundational epic)

## Risks
- Privacy concerns: mitigated by opt-in default and local-first architecture
- Integration complexity: mitigated by clear event schemas and graceful degradation

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-03 | pending | Initial creation |
