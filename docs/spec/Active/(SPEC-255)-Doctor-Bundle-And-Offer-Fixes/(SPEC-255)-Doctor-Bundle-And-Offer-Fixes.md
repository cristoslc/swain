---
title: "Doctor Bundle-And-Offer Fixes"
artifact: SPEC-255
track: implementable
status: Active
author: Cristos L-C
created: 2026-04-03
last-updated: 2026-04-03
priority-weight: medium
type: enhancement
parent-epic: ""
parent-initiative: INITIATIVE-002
linked-artifacts:
  - ADR-020
  - ADR-029
  - DESIGN-017
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Doctor Bundle-And-Offer Fixes

## Problem Statement

swain-doctor currently operates in warn-only mode for most findings. It detects issues (missing tools, stale config, fixable problems) and reports them with install hints, but never offers to fix them. The operator must read the hint, copy the command, and run it themselves. This wastes operator attention on mechanical fixes that doctor has all the information to perform.

ADR-020 (now Active) establishes a three-tier remediation model: self-heal silently for local fixes, bundle and offer for external fixes, report only for judgment calls. Doctor does not yet implement the "bundle and offer" tier.

## Desired Outcomes

Doctor becomes a one-stop remediation tool. At the end of a scan, the operator sees a single bundled fix plan covering all fixable issues and can approve the batch. Missing optional tools get installed, fixable project issues get repaired, and the operator makes one decision instead of N.

## External Behavior

### Current behavior

```
Tool availability:
  rtk ............ MISSING — git-compact passes through. Install: brew install rtk
  tmux ........... MISSING — tab-naming unavailable. Install: brew install tmux
```

Operator must manually run each install command.

### New behavior

Doctor collects all findings during its scan, classifies each as self-heal / bundle-offer / report-only per ADR-020, then:

1. **Self-heal findings** execute silently with advisory log lines (no change from current behavior where this already works)
2. **Bundle-offer findings** are collected into a fix plan presented at the end
3. **Report-only findings** are shown as warnings (no change)

```
Doctor found 2 fixable issues:

  1. rtk not installed — git-compact passes through without compression
     Fix: brew install rtk

  2. tmux not installed — session tab-naming unavailable
     Fix: brew install tmux

Run all fixes? [y/N]
```

If the operator approves, doctor runs each fix command sequentially, reporting success/failure per item. If declined, the findings are logged as advisories and the session continues.

### `--auto-fix` flag

For non-interactive contexts (dispatched agents, CI), `swain-doctor --auto-fix` runs self-heal fixes but skips bundle-offer fixes (no operator to consent). This preserves the safety guarantee that external installs require operator presence.

## Acceptance Criteria

1. **Given** doctor detects missing optional tools, **when** the scan completes, **then** a bundled fix plan is presented listing all missing tools with their install commands
2. **Given** the operator approves the fix plan, **when** doctor executes, **then** each install command runs and its success/failure is reported
3. **Given** the operator declines the fix plan, **when** doctor continues, **then** findings are logged as advisories and the session proceeds normally
4. **Given** `--auto-fix` flag, **when** doctor runs, **then** self-heal fixes execute but bundle-offer fixes are skipped
5. **Given** no fixable issues found, **when** the scan completes, **then** no fix plan is presented (silent pass)
6. All tools in the tool-availability table with `brew install` hints are classified as bundle-offer
7. The fix plan groups findings by category (tool installs, project fixes) for readability

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1: Bundled plan shown | Run doctor with rtk/tmux missing, verify plan output | |
| AC2: Fixes execute on approval | Approve plan, verify tools installed | |
| AC3: Decline continues | Decline plan, verify session proceeds | |
| AC4: --auto-fix skips offers | Run with flag, verify no install prompts | |
| AC5: Silent on no issues | Run with all tools present, verify no plan | |
| AC6: All optional tools classified | Check tool-availability entries are in plan | |
| AC7: Grouped by category | Verify plan output grouping | |

## Scope & Constraints

- Only tools already in the tool-availability table are covered — no new tool detection
- `brew install` is the only install method supported initially (macOS). Linux support (`apt`, `pacman`) is out of scope
- Doctor must not install anything without explicit operator consent (ADR-020)
- Self-heal fixes (local, idempotent) continue to run silently — they are not part of the bundle
- The fix plan is presented once at the end of the scan, not interleaved with findings

## Implementation Approach

1. Add a `fix_action` column to the tool-availability table entries: `self-heal`, `bundle-offer`, or `report-only`
2. During the doctor scan, collect bundle-offer findings into an array
3. After all checks complete, if the array is non-empty, present the bundled fix plan
4. On operator approval, iterate and execute each fix command
5. Report per-item results and overall summary
6. Update swain-doctor SKILL.md to document the three-tier model

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-03 | 3435901 | Initial creation |
