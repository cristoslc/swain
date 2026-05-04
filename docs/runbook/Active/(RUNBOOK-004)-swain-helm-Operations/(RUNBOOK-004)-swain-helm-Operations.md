---
title: "swain-helm Operations"
artifact: RUNBOOK-004
track: standing
status: Active
mode: manual
trigger: on-demand
author: cristos
created: 2026-04-18
last-updated: 2026-04-18
validates:
  - SPEC-318
  - SPEC-319
parent-epic: EPIC-084
depends-on-artifacts:
  - ADR-047
linked-artifacts:
  - VISION-006
  - ADR-046
  - ADR-047
---

## Purpose

Start and manage the swain-helm bridge system so you can interact with agent sessions from Zulip on any device.

## Prerequisites

- opencode CLI installed.
- 1Password CLI (`op`) installed and configured.
- A Zulip organization with a bot account.
- Projects registered via `swain-helm project add`.

## Steps

### 1. Provision the host

**Action:** Run `swain-helm host provision`.

**Expected:** Bot registered, stream created, `~/.config/swain-helm/helm.config.json` written with op:// references.

### 2. Start the bridge

**Action:** Run `swain-helm host up`.

**Expected:** 1Password biometric prompt. On unlock, watchdog starts. Output: "Watchdog running (PID XXXX). X project bridges started."

### 3. Verify Zulip connectivity

**Action:** Send a message in Zulip #\<project\> > control.

**Expected:** Bot responds. Session starts on trunk worktree.

### 4. Check status

**Action:** `swain-helm host status`.

**Expected:** Shows watchdog PID, each bridge PID and health, opencode serve port and health.

### 5. Add another project

**Action:** `swain-helm project add ./another-project`.

**Expected:** Project config written. Watchdog discovers it within 30s.

### 6. Shut down

**Action:** `swain-helm host down`.

**Expected:** All bridges stopped, watchdog stopped.

## Teardown

`swain-helm host down` stops everything. Session data persists in project `.swain` directories.

## Troubleshooting

| Symptom | Resolution |
|---------|------------|
| "1Password locked" | Unlock 1Password and restart with `swain-helm host up`. |
| "Watchdog not starting" | Check `~/.config/swain-helm/helm.config.json` exists and is valid JSON. |
| "No messages in Zulip" | Check bot is subscribed to stream, check bot_api_key. |
| "opencode serve not found" | Check opencode is installed (`which opencode`), check configured port. |
| "Bridge keeps restarting" | Check bridge logs, look for import errors or missing config. |

## Run Log

| Date | Operator | Result | Duration | Notes |
|------|----------|--------|----------|-------|
| 2026-04-18 | cristos | - | - | Template created |

## Lifecycle

| Status | Date | Until | Note |
|--------|------|-------|------|
| Active | 2026-04-18 | -- | Replaces RUNBOOK-003. |