---
title: "Prune deprecated swain-push"
artifact: SPEC-080
track: implementable
status: Active
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
type: enhancement
parent-epic: EPIC-031
linked-artifacts: []
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Prune deprecated swain-push

## Problem Statement

swain-push is a deprecated redirect to swain-sync. The tilde in `name: swain-~push` was intentional (to sort it to the bottom of skill lists), but the skill itself serves no purpose — it just tells users to use swain-sync. Keeping it adds noise to the skill roster and confusion for agents that encounter it.

## External Behavior

The swain-push skill directory is deleted. The swain meta-router's routing table no longer includes a swain-push row. Users who invoke `/swain-push` get a "skill not found" response, which is clearer than a redirect.

## Acceptance Criteria

**AC-1:** `skills/swain-push/` and `.claude/skills/swain-push/` directories are deleted.

**AC-2:** swain meta-router SKILL.md no longer references swain-push.

**AC-3:** No other SKILL.md references swain-push (grep confirms).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC-1 | `ls` confirms directories absent | |
| AC-2 | Read swain SKILL.md | |
| AC-3 | grep -r "swain-push" across skills/ | |

## Scope & Constraints

**In scope:** Delete directories. Update routing table. Remove any cross-references.

**Out of scope:** Creating a successor or migration path — swain-sync already exists and is well-known.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | — | Prune deprecated skill identified in audit |
