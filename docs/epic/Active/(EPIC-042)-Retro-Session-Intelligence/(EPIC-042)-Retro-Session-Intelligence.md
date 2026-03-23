---
title: "Retro Session Intelligence"
artifact: EPIC-042
track: container
status: Active
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
parent-vision: VISION-004
parent-initiative: INITIATIVE-019
priority-weight: high
success-criteria:
  - Retros capture scrubbed session JSONL archives in structured folders
  - Each retro folder contains a manifest.yaml with session provenance and scrub metadata
  - Session summaries surface Decision Points, Pivot Points, Surprises, and Learnings
  - Existing flat-file retros are migrated to folder structure by swain-doctor
depends-on-artifacts: []
addresses: []
evidence-pool: "agent-alignment-monitoring@8047381"
---

# Retro Session Intelligence

## Goal / Objective

Transform retros from output-focused documents (what was produced) into process-alignment records (how the agent navigated decisions). Capture, scrub, archive, and summarize session transcripts so that future agents and operators can study how past sessions made choices — not just what they shipped.

## Desired Outcomes

The operator (PERSONA-001) gains durable decision records that survive session context windows. Future agents can read prior session summaries to learn from past navigation patterns — what worked, what pivoted, what surprised. Cross-retro analysis becomes possible via machine-readable manifests, enabling systemic process alignment insights across many sessions.

This advances INITIATIVE-019's direction by making session decision history retrievable beyond the session boundary, and grounds VISION-004's cognitive support in empirical session evidence rather than abstract guidance.

## Scope Boundaries

**In scope:**
- JSONL scrubbing pipeline (secrets + PII redaction) as an extension to swain-security-check
- Retro folder structure with manifest.yaml
- Session JSONL capture, compression, and archival
- Agent-generated session summaries with bookmark-based narrative structure
- Decision Points / Pivot Points / Surprises / Learnings extraction
- Migration of existing flat-file retros to folder structure

**Out of scope:**
- Continuous session-time decision logging (future work — would require changes to every skill)
- Cross-retro aggregation tooling (future epic — consumes manifests this epic produces)
- Real-time monitoring of agent process alignment (different from post-hoc retro analysis)

## Child Specs

| Spec | Title | Depends on |
|------|-------|------------|
| SPEC-150 | swain-security-check: JSONL scrub mode | — |
| SPEC-151 | swain-retro: folder structure, manifest, + JSONL capture | SPEC-150 |
| SPEC-152 | swain-retro: session summary generation | SPEC-151 |
| SPEC-153 | swain-doctor: retro flat-file migration | SPEC-151 |

## Key Dependencies

- swain-security-check (SPEC-150 extends it)
- swain-session (bookmarks used as waypoints in SPEC-152; graceful fallback if absent)
- zstd or gzip for compression

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-22 | — | Initial creation |
